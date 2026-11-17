#!/usr/bin/env python3
"""Gizli bölge bekçisi: kişisel klasörleri (yaşam ve wiki `ozel/`) kodla korur, yalnız metinle değil.

Yazım tarifi: mimari/is-tarifleri/gizli_bolge.md

Bölgeler koda yazılmaz, `harita.json` -> `gizlilik` içinden okunur:
  - `yasak_yollar`: hiçbir ajan okumaz ve yazmaz, hiçbir modele gitmez, commit'lenmez.
  - `ucretsiz_yasak_yollar`: ücretsiz web planlarına ve ücretsiz API havuzuna gitmez (abonelikli Claude ve Gemini okuyabilir).

Kullanım:
  python araclar/gizli_bolge.py kanca                       # Claude Code PreToolUse: bölgeye değen çağrı 'deny'
  python araclar/gizli_bolge.py denetle                     # git pre-commit: sahnelenen dosyaları denetler
  python araclar/gizli_bolge.py sina --sinif ucretsiz YOL... # gönderen betikler için: çıkış 1 = gönderme
  python araclar/gizli_bolge.py liste                       # bölgeleri basar

Kanca hiçbir koşulda hata vermez (çıkış 0); karar veremezse araç normal izin akışında kalır.
`denetle` sorun bulursa çıkış 1, sorunlar standart hataya yazılır. Yalnızca standart kitaplık.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

KOK = Path(__file__).resolve().parent.parent
HARITA_YOLU = KOK / "harita.json"
SINIFLAR = ("abonelik", "ucretsiz")
# Yol taşıyan araç alanları (Read, Edit, Write, MultiEdit, NotebookEdit, NotebookRead, Grep, Glob, LS).
YOL_ALANLARI = ("file_path", "notebook_path", "path", "pattern", "glob")
WIKI_KOKU = "kasa/80-Wiki/"
_ON_BILGI = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)


# --- Bölgeler ----------------------------------------------------------------

def harita_oku(kok: Path = KOK) -> dict:
    """Projenin `harita.json` dosyası, yoksa merkezinki. İkisi de yoksa (merkezin kopyası eksik başka depo) boş sözlük:
    bölge yoktur ama ASCII ad denetimi yine çalışır."""
    # Merkez kopyası (`.merkez/harita.json`) deponun kendi başka amaçlı `harita.json`'ından üstündür.
    try:
        kopya = json.loads(HARITA_YOLU.read_text(encoding="utf-8"))
        if isinstance(kopya, dict) and kopya.get("merkez_kopyasi"):
            return kopya
    except (OSError, ValueError):
        pass
    for yol in (kok / "harita.json", HARITA_YOLU):
        if yol.is_file():
            return json.loads(yol.read_text(encoding="utf-8"))
    return {}


def bolgeler(harita: dict, sinif: str | None = None) -> list[str]:
    """`sinif=None` ya da 'abonelik': yalnız yasak yollar. 'ucretsiz': yasak yollar + ücretsiz yasakları."""
    g = harita.get("gizlilik") or {}
    liste = [str(y) for y in g.get("yasak_yollar") or []]
    if sinif == "ucretsiz":
        liste += [str(y) for y in g.get("ucretsiz_yasak_yollar") or []]
    return liste


def _duz(yol: str) -> str:
    g = yol.replace("\\", "/").strip().strip("\"'")
    while g.startswith("./"):
        g = g[2:]
    return g.lower()


def goreli(yol: str, kok: Path) -> str:
    """Proje köküne göre eğik çizgili yol. Kök dışındaysa düzleştirilmiş mutlak yol döner (yine de denetlenir)."""
    p = Path(yol.replace("\\", "/"))
    if not p.is_absolute():
        p = kok / p
    norm = Path(os.path.normpath(p))
    try:
        return PurePosixPath(norm.relative_to(Path(os.path.normpath(kok))).as_posix()).as_posix()
    except ValueError:
        return norm.as_posix()


def bolgede_mi(yol: str, liste: list[str]) -> str | None:
    """Yol listedeki bir bölgenin içindeyse (ya da bölgenin kendisiyse) o girdiyi döner.

    Göreli yolda baştan, mutlak yolda herhangi bir kök altında eşleşir: başka bir kopyadaki
    `.../volkan-merkez/kasa/80-Wiki/ozel/x.md` de yakalanır."""
    g = _duz(yol)
    for girdi in liste:
        e = _duz(girdi).rstrip("/")
        if not e:
            continue
        if g == e or g.startswith(e + "/") or ("/" + e + "/") in ("/" + g + "/") or g.endswith("/" + e):
            return girdi
    return None


def _kabuk_bolge(komut: str, liste: list[str]) -> str | None:
    """Komut metninde bölge yolu geçiyor mu. Bölgenin son iki parçası yeter (`80-Wiki/ozel`): `cd kasa && cat 80-Wiki/ozel/x`."""
    k = _duz(komut)
    for girdi in liste:
        parcalar = [p for p in _duz(girdi).split("/") if p]
        if not parcalar:
            continue
        iz = "/".join(parcalar[-2:]) if len(parcalar) >= 2 else parcalar[0]
        if re.search(r"(?<![a-z0-9_.-])" + re.escape(iz) + r"(?![a-z0-9_-])", k):
            return girdi
    return None


# --- Claude Code kancası -----------------------------------------------------

def karar(veri: dict, harita: dict, kok: Path) -> dict | None:
    girdi = veri.get("tool_input")
    if not isinstance(girdi, dict):
        return None
    liste = bolgeler(harita)
    if not liste:
        return None
    bulunan = None
    if veri.get("tool_name") == "Bash" or "command" in girdi:
        if isinstance(girdi.get("command"), str):
            bulunan = _kabuk_bolge(girdi["command"], liste)
    else:
        for alan in YOL_ALANLARI:
            deger = girdi.get(alan)
            if isinstance(deger, str) and deger:
                if (bulunan := bolgede_mi(goreli(deger, kok), liste) or _kabuk_bolge(deger, liste)):
                    break
    if not bulunan:
        return None
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": f"Gizli bölge ({bulunan}): kişisel veri hiçbir ajana ve modele gitmez (AGENTS.md bölüm 4). "
                                    "Bu klasörü okuma, arama ya da yazma. Volkan bu notları kendisi Obsidian'da yazar."}}


# --- Dışarı gönderme kapısı --------------------------------------------------

def disari_cikabilir(yollar, sinif: str, harita: dict | None = None, kok: Path = KOK) -> tuple[bool, list[str]]:
    """Dosyalar `sinif` sınıfındaki bir modele gönderilebilir mi. (izin, engellenen yollar).

    Gönderen her betik (ücretsiz web kuyruğu, API havuzu, dağıtıcı) içerik göndermeden önce bunu çağırır.
    Bilinmeyen sınıf en sıkı sınıf (ucretsiz) sayılır."""
    if harita is None:
        harita = harita_oku(kok)
    liste = bolgeler(harita, sinif if sinif in SINIFLAR else "ucretsiz")
    engel = [str(y) for y in yollar if bolgede_mi(goreli(str(y), kok), liste)]
    return (not engel), engel


# --- Git pre-commit ----------------------------------------------------------

def _git(kok: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=kok, capture_output=True, check=True).stdout


def sahnelenenler(kok: Path) -> list[tuple[str, str]]:
    """(durum, yol) çiftleri: eklenen, değişen, adı değişen ve kopyalanan dosyalar."""
    ham = _git(kok, "diff", "--cached", "--name-status", "--no-renames", "-z", "--diff-filter=ACMR")
    parcalar = [p.decode("utf-8", errors="replace") for p in ham.split(b"\0") if p]
    return list(zip(parcalar[0::2], parcalar[1::2]))


def on_bilgi(metin: str) -> dict:
    m = _ON_BILGI.match(metin)
    alanlar = {}
    for satir in (m.group(1).splitlines() if m else []):
        if ":" in satir and not satir.startswith((" ", "\t", "-")):
            ad, deger = satir.split(":", 1)
            alanlar[ad.strip()] = deger.split("#", 1)[0].strip().strip("\"'")
    return alanlar


def icerik_sorunlari(yol: str, metin: str, harita: dict) -> list[str]:
    """Commit'lenecek wiki sayfasında özel işaret ya da kişi verisi deseni var mı."""
    sorunlar = []
    if on_bilgi(metin).get("gizlilik", "").lower() == "ozel":
        sorunlar.append(f"{yol}: 'gizlilik: ozel' sayfası commit'lenmez. Taşı: python araclar/wiki.py ozele-tasi \"{yol}\"")
    for ad, desen in ((harita.get("gizlilik") or {}).get("desenler") or {}).items():
        if re.search(desen, metin):
            sorunlar.append(f"{yol}: kişi verisi ya da anahtar deseni ({ad}). Sil ya da sayfayı ozel/ klasörüne taşı")
    return sorunlar


def denetle(kok: Path, harita: dict) -> list[str]:
    liste = bolgeler(harita)
    sorunlar = []
    for durum, yol in sahnelenenler(kok):
        if (b := bolgede_mi(yol, liste)):
            sorunlar.append(f"{yol}: gizli bölgede ({b}), commit'lenmez. Çıkar: git rm --cached \"{yol}\"")
            continue
        if durum == "A" and not PurePosixPath(yol).name.isascii():
            sorunlar.append(f"{yol}: dosya adında Türkçe ya da ASCII dışı karakter var (AGENTS.md bölüm 6)")
        if yol.startswith(WIKI_KOKU) and yol.lower().endswith(".md"):
            metin = _git(kok, "show", ":" + yol).decode("utf-8", errors="replace")
            sorunlar += icerik_sorunlari(yol, metin, harita)
    return sorunlar


# --- Giriş -------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    for akis in (sys.stdout, sys.stderr):
        if hasattr(akis, "reconfigure"):
            akis.reconfigure(encoding="utf-8", errors="replace")
    argv = list(sys.argv[1:] if argv is None else argv)
    kok = Path(os.environ.get("CLAUDE_PROJECT_DIR") or KOK)
    komut = argv[:1]
    if komut == ["kanca"]:
        try:
            veri = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
            ret = karar(veri, harita_oku(kok), kok) if isinstance(veri, dict) else None
        except Exception:  # noqa: BLE001 - kanca işi hiçbir koşulda bozmaz
            ret = None
        if ret is not None:
            print(json.dumps(ret, ensure_ascii=True))
        return 0
    if komut == ["denetle"]:
        kok = Path(_git(Path.cwd(), "rev-parse", "--show-toplevel").decode().strip())
        sorunlar = denetle(kok, harita_oku(kok))
        for s in sorunlar:
            print("gizli-bolge: " + s, file=sys.stderr)
        return 1 if sorunlar else 0
    if komut == ["sina"]:
        try:
            i = argv.index("--sinif")
            sinif, yollar = argv[i + 1], argv[1:i] + argv[i + 2:]
        except (ValueError, IndexError):
            print("Kullanım: python araclar/gizli_bolge.py sina --sinif abonelik|ucretsiz YOL...", file=sys.stderr)
            return 2
        izin, engel = disari_cikabilir(yollar, sinif, harita_oku(kok), kok)
        for y in engel:
            print(f"gönderilmez ({sinif}): {y}")
        return 0 if izin else 1
    if komut == ["liste"]:
        h = harita_oku(kok)
        print("Hiçbir ajana: " + ", ".join(bolgeler(h)))
        print("Ücretsiz modellere ek olarak: " + ", ".join((h.get("gizlilik") or {}).get("ucretsiz_yasak_yollar") or []))
        return 0
    print("Kullanım: python araclar/gizli_bolge.py kanca | denetle | sina --sinif S YOL... | liste", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
