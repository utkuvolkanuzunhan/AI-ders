#!/usr/bin/env python3
"""Oturum içi zorlamalar: okuma bütçesi, yönlendirici paketi, karar öncesi okuma, kural adayı.

Yazım tarifi: mimari/is-tarifleri/zorla.md

Volkan'ın kuralları (2026-11-17):
  - 400 satırı aşan dosya önce aranmadan bütün okunmaz (token).
  - Her iş yönlendirici paketiyle başlar (AGENTS.md bölüm 1): paket görülmeden depoya yazılmaz.
  - Kota, hesap ya da yetki kuralına dokunmadan önce ilgili dallar ve kural kaydı okunur.
  - Eklenen her kural kancayla korunur: kural gibi görünen istem gelince ajan onu kural kaydına çevirir.

Değerler koda yazılmaz: `harita.json` -> `zorlama` (`okuma_satir_tavani`, `hassas_yollar`, `kural_kaliplari`).
Oturum izi geçici klasörde tutulur (`<tmp>/volkan-zorla/<session_id>.json`); depoya yazılmaz.
Kanca hiçbir koşulda işi bozmaz: girdi ya da harita okunamazsa karar vermez.

Kullanım (Claude Code kancaları):
  python araclar/zorla.py kanca     # PreToolUse: Read, Grep, Glob, Edit, Write, MultiEdit, NotebookEdit, Bash
  python araclar/zorla.py istem     # UserPromptSubmit: kural adayı uyarısı
Yalnızca standart kitaplık.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent      # merkezde depo kökü, kopyada `.merkez/`
HARITA_YOLU = KOK / "harita.json"
YAZAN = ("Edit", "Write", "MultiEdit", "NotebookEdit")
VARSAYILAN = {"okuma_satir_tavani": 400, "hassas_yollar": [], "kural_kaliplari": [], "paket_zorunlu": True,
              "baglam_uyari_token": 150000, "baglam_dur_token": 200000, "devir_desenleri": ["devir", "devam"]}
_YON = re.compile(r"\byon\.py\b")
_BAGLAM = re.compile(r"\bkural_kayit\.py\s+baglam\b")
_ARAMA = re.compile(r"\b(?:rg|grep|git\s+grep)\b")


def ayar(harita: dict) -> dict:
    a = dict(VARSAYILAN)
    a.update(harita.get("zorlama") or {})
    return a


def harita_oku() -> dict:
    try:
        return json.loads(HARITA_YOLU.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


# --- Oturum izi --------------------------------------------------------------

def iz_yolu(oturum: str) -> Path:
    temiz = re.sub(r"[^A-Za-z0-9_-]", "_", oturum or "bilinmiyor")[:80]
    return Path(os.environ.get("VOLKAN_ZORLA_DIZIN") or Path(tempfile.gettempdir()) / "volkan-zorla") / f"{temiz}.json"


def iz_oku(oturum: str) -> dict:
    try:
        d = json.loads(iz_yolu(oturum).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def iz_yaz(oturum: str, iz: dict) -> None:
    yol = iz_yolu(oturum)
    try:
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(json.dumps(iz, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


# --- Yardımcılar ---------------------------------------------------------------

def _goreli(yol: str, kok: Path) -> str | None:
    p = Path(yol)
    if not p.is_absolute():
        p = kok / p
    try:
        return Path(os.path.normpath(p)).relative_to(Path(os.path.normpath(kok))).as_posix()
    except ValueError:
        return None


def _eslesir(goreli: str, liste: list[str]) -> str | None:
    g = goreli.lower()
    for girdi in liste:
        e = str(girdi).replace("\\", "/").lower()
        if (e.endswith("/") and (g.startswith(e) or g == e.rstrip("/"))) or g == e:
            return girdi
    return None


def satir_sayisi(yol: Path, tavan: int) -> int:
    """Tavanı aşınca durur; okunamazsa 0."""
    try:
        if yol.stat().st_size < tavan * 20:        # kısa dosya: saymaya değmez
            return 0
        n = 0
        with yol.open("rb") as f:
            for _ in f:
                n += 1
                if n > tavan:
                    break
        return n
    except OSError:
        return 0


def merkez_var(kok: Path) -> bool:
    """Yönlendirici erişilebilir mi: merkezin kendisi ya da yanında volkan-merkez."""
    if (kok / "araclar" / "yon.py").is_file() and (kok / "harita.json").is_file() and not (kok / ".merkez").is_dir():
        return True
    adaylar = [Path(os.environ["VOLKAN_MERKEZ"])] if os.environ.get("VOLKAN_MERKEZ") else []
    adaylar.append(kok.parent / "volkan-merkez")
    return any((a / "araclar" / "yon.py").is_file() for a in adaylar)


def _red(neden: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": neden}}


# --- Karar ----------------------------------------------------------------------

def karar(veri: dict, harita: dict, kok: Path, iz: dict) -> tuple[dict | None, dict]:
    """(kanca çıktısı ya da None, güncel iz)."""
    a = ayar(harita)
    arac = veri.get("tool_name")
    girdi = veri.get("tool_input") if isinstance(veri.get("tool_input"), dict) else {}
    iz = dict(iz)
    aranan = list(iz.get("aranan") or [])

    if arac == "Bash":
        komut = str(girdi.get("command") or "")
        if _YON.search(komut):
            iz["paket"] = True
        if _BAGLAM.search(komut):
            iz["baglam"] = True
        if _ARAMA.search(komut):
            iz["kabuk_arama"] = True
        return None, iz

    if arac in ("Grep", "Glob"):
        yol = girdi.get("path") or "."
        g = _goreli(str(yol), kok)
        if g is not None and g not in aranan:
            aranan.append(g)
            iz["aranan"] = aranan[-50:]
        return None, iz

    if arac == "Read":
        yol = girdi.get("file_path")
        if not isinstance(yol, str) or girdi.get("limit"):
            return None, iz
        tavan = int(a["okuma_satir_tavani"])
        p = Path(yol) if Path(yol).is_absolute() else kok / yol
        # Aynı oturumda değişmemiş dosyayı ikinci kez bütün okumak bağlamı boşuna büyütür.
        try:
            imza = f"{os.path.normpath(p)}|{p.stat().st_mtime_ns}"
        except OSError:
            imza = None
        okunan = list(iz.get("tam_okunan") or [])
        if imza and imza in okunan and iz.get("tekrar_izni") != imza:
            iz["tekrar_izni"] = imza
            return _red("Tekrar okuma: bu dosyayı bu oturumda zaten bütün okudun ve o zamandan beri değişmedi. "
                        "Bağlamdaki sürümü kullan; gerçekten gerekiyorsa aynı okumayı bir kez daha iste."), iz
        def izin() -> tuple[None, dict]:
            if imza and imza not in okunan:
                iz["tam_okunan"] = (okunan + [imza])[-200:]
            return None, iz
        if satir_sayisi(p, tavan) <= tavan:
            return izin()
        g = _goreli(yol, kok)
        if g is not None and any(r == "." or g == r or g.startswith(r.rstrip("/") + "/") for r in aranan):
            return izin()
        if iz.get("okundu_izni") == g:              # aynı dosyada ikinci deneme: bilerek tam okuma
            return izin()
        iz["okundu_izni"] = g
        return _red(f"Okuma bütçesi: dosya {tavan} satırdan uzun. Önce Grep ile ara ya da offset/limit ile yalnız "
                    "gereken bölümü oku. Bütününe gerçekten gerekiyorsa aynı okumayı bir kez daha iste."), iz

    if arac in YAZAN:
        yol = next((girdi[k] for k in ("file_path", "notebook_path") if isinstance(girdi.get(k), str)), None)
        g = _goreli(yol, kok) if yol else None
        if g is None:                                 # proje dışı (karalama, bellek): zorlanmaz
            return None, iz
        if (iz.get("baglam_dur") and not any(d in g.lower() for d in a.get("devir_desenleri") or [])
                and guvenli_nokta(kok)):
            return _red(f"Bağlam {iz['baglam_dur']} tokenı aştı ve iş güvenli noktada (değişiklik yok, hepsi "
                        "gönderilmiş): yeni işe başlama, devir notu yaz (adında 'devir' geçen dosya serbest), işi yeni "
                        "oturumda sürdür."), iz
        if a.get("paket_zorunlu") and not iz.get("paket") and merkez_var(kok):
            return _red("Yönlendirici paketi yok: AGENTS.md bölüm 1 gereği önce `python araclar/yon.py \"<iş>\"` "
                        "(başka depoda `python ../volkan-merkez/araclar/yon.py \"<iş>\" --depo <ad>`) çalıştır, "
                        "paketi kural say, sonra yaz."), iz
        hassas = _eslesir(g, [str(y) for y in a.get("hassas_yollar") or []])
        if hassas and not iz.get("baglam"):
            return _red(f"Karar öncesi okuma: {hassas} kota, hesap ya da yetki kuralı taşıyor. Önce "
                        "`python araclar/kural_kayit.py baglam` ile ilgili dalları ve kural kaydını oku, "
                        "projenin belleğindeki ilgili dosyaya bak, sonra değiştir."), iz
    return None, iz


def guvenli_nokta(kok: Path) -> bool:
    """İş yarıda değil mi: çalışma ağacı temiz ve yerel commit'lerin hepsi gönderilmiş. Git yoksa ya da bozuksa evet sayılır.

    Volkan (2026-11-17): eşik aşılınca iş yarıda kesilmez; süren alt iş biter, commit'lenir, gönderilir, sonra devredilir."""
    try:
        durum = subprocess.run(["git", "-C", str(kok), "status", "--porcelain"], capture_output=True, text=True,
                               timeout=5)
        if durum.returncode != 0:
            return True
        if durum.stdout.strip():
            return False
        ileri = subprocess.run(["git", "-C", str(kok), "rev-list", "--count", "@{u}..HEAD"], capture_output=True,
                               text=True, timeout=5)
        return ileri.returncode != 0 or ileri.stdout.strip() in ("", "0")
    except (OSError, subprocess.SubprocessError):
        return True


def baglam_olc(dokum: str | None, kuyruk: int = 400_000) -> int | None:
    """Dökümün son asistan turunun bağlamı (giriş + önbellekten okunan + önbelleğe yazılan token); bulunamazsa None."""
    if not dokum:
        return None
    try:
        with open(dokum, "rb") as f:
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - kuyruk))
            satirlar = f.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for satir in reversed(satirlar):
        if '"usage"' not in satir:
            continue
        try:
            u = (json.loads(satir).get("message") or {}).get("usage") or {}
        except ValueError:
            continue
        toplam = sum(int(u.get(k) or 0) for k in ("input_tokens", "cache_read_input_tokens",
                                                   "cache_creation_input_tokens"))
        if toplam:
            return toplam
    return None


def baglam_notu(token: int | None, harita: dict) -> tuple[str | None, int | None]:
    """(ajana not, durdurma eşiği aşıldıysa token)."""
    a = ayar(harita)
    if token is None or token < int(a["baglam_uyari_token"]):
        return None, None
    if token >= int(a["baglam_dur_token"]):
        return (f"BAĞLAM {token:,} token: devir eşiği aşıldı. İşi yarıda kesme: süren alt işi bitir, testini koş, "
                "commit'le, gönder, ilerleme listesini güncelle; sonra kısa ve eksiksiz devir notu yaz (ne istendi, ne "
                "bitti, dal ve son commit, sıradaki adım, açık onaylar). Yeni alt işe başlama; iş güvenli noktaya "
                "gelince yazan araçlar yalnız devir notuna açık kalır.").replace(",", "."), token
    return (f"BAĞLAM {token:,} token: devir yaklaşıyor. Alt işleri küçük tut ki eşikte yarım iş kalmasın."
            ).replace(",", "."), None


def istem_notu(metin: str, harita: dict) -> str | None:
    """Kural gibi görünen istemde ajana verilecek kısa not; değilse None."""
    kaliplar = ayar(harita).get("kural_kaliplari") or []
    kucuk = metin.lower()
    if not any(re.search(k, kucuk) for k in kaliplar):
        return None
    return ("KURAL ADAYI: Bu istem yeni ya da değişen bir kural içeriyor olabilir. Kuralsa: tek satırlık kurala çevir, "
            "volkan-merkez'de `python araclar/kural_kayit.py ara <sözcük>` ile çelişen kuralı bul, çelişki varsa karar kartıyla sor, "
            "sonra `kural_kayit.py ekle` ile kaydet ve koruyan kancayı ya da testi aynı işte yaz "
            "(koruyanı olmayan kural kontrol.py'de kırmızıdır).")


def main(argv: list[str] | None = None) -> int:
    for akis in (sys.stdout, sys.stderr):
        if hasattr(akis, "reconfigure"):
            akis.reconfigure(encoding="utf-8", errors="replace")
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] not in (["kanca"], ["istem"]):
        print("Kullanım: python araclar/zorla.py kanca | istem", file=sys.stderr)
        return 2
    try:
        veri = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
        if not isinstance(veri, dict):
            return 0
        harita = harita_oku()
        kok = Path(os.environ.get("CLAUDE_PROJECT_DIR") or veri.get("cwd") or KOK)
        oturum = str(veri.get("session_id") or "")
        if argv[0] == "istem":
            notlar = [istem_notu(str(veri.get("prompt") or ""), harita)]
            b_notu, dur = baglam_notu(baglam_olc(veri.get("transcript_path")), harita)
            notlar.append(b_notu)
            iz = iz_oku(oturum)
            if dur and iz.get("baglam_dur") != dur:
                iz["baglam_dur"] = dur
                iz_yaz(oturum, iz)
            elif not dur and iz.get("baglam_dur"):
                iz.pop("baglam_dur")
                iz_yaz(oturum, iz)
            for n in notlar:
                if n:
                    print(n)
            return 0
        cikti, iz = karar(veri, harita, kok, iz_oku(oturum))
        iz_yaz(oturum, iz)
        if cikti is not None:
            print(json.dumps(cikti, ensure_ascii=True))
    except Exception:  # noqa: BLE001 - kanca işi hiçbir koşulda bozmaz
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
