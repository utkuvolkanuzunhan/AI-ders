#!/usr/bin/env python3
"""Bekçi dosyası kancası: AGENTS.md bölüm 8'deki "bekçi dosyaları onay ister" kuralını Claude Code'da zorlar.

Yazım tarifi: mimari/is-tarifleri/koruma.md

Claude Code `PreToolUse` kancası. Dosya yazan araç (Edit, Write, MultiEdit, NotebookEdit) bekçi dosyasına dokunuyorsa ya da
kabuk komutu bekçi dosyasını değiştirecek gibi görünüyorsa çağrı durdurulmaz ama `ask` kararıyla Volkan'ın onayına gider.
Bekçi listesi koda yazılmaz: `harita.json` -> `depolar.<depo>.bekci_dosyalari` (depo adı proje klasörünün adıdır).

Kullanım:
  python araclar/koruma.py kanca     # standart girdiden kanca JSON'u okur
  python araclar/koruma.py liste     # bu deponun bekçi listesini basar

Kanca hiçbir koşulda hata vermez: girdi ya da harita okunamazsa karar vermez (araç normal izin akışında kalır).
Sınır: kabuk denetimi sezgiseldir (yazma işleci ya da değiştiren komut + bekçi yolu); bilerek gizlenmiş yazmayı yakalamaz.
Yalnızca standart kitaplık.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path, PurePosixPath

KOK = Path(__file__).resolve().parent.parent
HARITA_YOLU = KOK / "harita.json"
YAZAN_ARACLAR = ("Edit", "Write", "MultiEdit", "NotebookEdit")
YOL_ALANLARI = ("file_path", "notebook_path", "path")
# Kabukta dosyayı değiştiren kalıplar: yönlendirme, yerinde düzenleme, taşıma, silme, git geri alma.
_DEGISTIREN = re.compile(r"(?:>>?|\btee\b|\bsed\s+[^|;&]*-i|\bperl\s+[^|;&]*-i|\bmv\b|\bcp\b|\brm\b|\btruncate\b|"
                         r"\bgit\s+(?:rm|mv|checkout|restore|apply|am)\b|\bpython3?\s+-c\b|\bSet-Content\b|\bOut-File\b)")


def bekci_listesi(harita: dict, depo_adi: str) -> list[str]:
    for ad, kayit in (harita.get("depolar") or {}).items():
        if ad.lower() == depo_adi.lower() and isinstance(kayit, dict):
            return [str(y) for y in kayit.get("bekci_dosyalari") or []]
    # Merkezin başka depoya dağıttığı kopya (`.merkez/harita.json`) yalnız o deponun kaydını taşır; klasör adı
    # (bulut oturumu, farklı klon adı) depo adından farklı olsa da o kayıt geçerlidir.
    depolar = harita.get("depolar") or {}
    if harita.get("merkez_kopyasi") and len(depolar) == 1:
        kayit = next(iter(depolar.values()))
        if isinstance(kayit, dict):
            return [str(y) for y in kayit.get("bekci_dosyalari") or []]
    return []


def _goreli(yol: str, kok: Path) -> str | None:
    """Proje köküne göre eğik çizgili yol; kökün dışındaysa None."""
    p = Path(yol)
    if not p.is_absolute():
        p = kok / p
    try:
        return PurePosixPath(Path(os.path.normpath(p)).relative_to(Path(os.path.normpath(kok))).as_posix()).as_posix()
    except ValueError:
        return None


def bekci_mi(goreli: str, liste: list[str]) -> str | None:
    """Yol bekçi listesindeki bir dosya ya da klasörün altındaysa o girdiyi döner."""
    g = goreli.replace("\\", "/").lower()
    while g.startswith("./"):
        g = g[2:]
    for girdi in liste:
        e = girdi.replace("\\", "/").lower()
        if e.endswith("/"):
            if g == e.rstrip("/") or g.startswith(e):
                return girdi
        elif g == e:
            return girdi
    return None


def _kabuk_bekci(komut: str, liste: list[str]) -> str | None:
    if not _DEGISTIREN.search(komut):
        return None
    kucuk = komut.replace("\\", "/").lower()
    for girdi in liste:
        e = girdi.replace("\\", "/").lower().rstrip("/")
        if re.search(r"(?<![a-z0-9_.-])" + re.escape(e) + r"(?![a-z0-9_-])", kucuk):
            return girdi
    return None


def harita_sec(kok: Path) -> dict:
    """Merkez kopyası (`.merkez/harita.json`, `merkez_kopyasi: true`) varsa o; yoksa proje kökündeki harita, yoksa merkezinki.
    Başka depo kendi `harita.json`'ını başka amaçla taşıyabilir (gelisim gibi); kopya ona üstün gelir."""
    adaylar = [HARITA_YOLU, kok / "harita.json"]
    okunan = []
    for yol in adaylar:
        try:
            okunan.append(json.loads(yol.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            okunan.append(None)
    if isinstance(okunan[0], dict) and okunan[0].get("merkez_kopyasi"):
        return okunan[0]
    for h in (okunan[1], okunan[0]):
        if isinstance(h, dict):
            return h
    raise ValueError("harita yok")


def karar(veri: dict, harita: dict, kok: Path) -> dict | None:
    arac = veri.get("tool_name")
    girdi = veri.get("tool_input")
    if not isinstance(girdi, dict):
        return None
    liste = bekci_listesi(harita, kok.name)
    if not liste:
        return None
    bulunan = None
    if arac in YAZAN_ARACLAR:
        for alan in YOL_ALANLARI:
            if isinstance(girdi.get(alan), str):
                goreli = _goreli(girdi[alan], kok)
                if goreli is not None and (bulunan := bekci_mi(goreli, liste)):
                    break
    elif arac == "Bash" and isinstance(girdi.get("command"), str):
        bulunan = _kabuk_bekci(girdi["command"], liste)
    if not bulunan:
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                   "permissionDecisionReason": f"Bekçi dosyası ({bulunan}): AGENTS.md bölüm 8 gereği Volkan'ın "
                                                               "onayı gerekir. Onay yoksa bu değişikliği yapma, öner."}}


def main(argv: list[str] | None = None) -> int:
    for akis in (sys.stdout, sys.stderr):
        if hasattr(akis, "reconfigure"):
            akis.reconfigure(encoding="utf-8", errors="replace")
    argv = list(sys.argv[1:] if argv is None else argv)
    kok = Path(os.environ.get("CLAUDE_PROJECT_DIR") or KOK)
    if argv[:1] == ["liste"]:
        try:
            print("\n".join(bekci_listesi(json.loads(HARITA_YOLU.read_text(encoding="utf-8")), kok.name)))
        except (OSError, ValueError):
            return 2
        return 0
    if argv[:1] == ["kanca"]:
        try:
            veri = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace") or "{}")
            harita = harita_sec(kok)
            ret = karar(veri, harita, kok) if isinstance(veri, dict) else None
        except Exception:  # noqa: BLE001 - kanca işi hiçbir koşulda bozmaz
            ret = None
        if ret is not None:
            print(json.dumps(ret, ensure_ascii=True))
        return 0
    print("Kullanım: python araclar/koruma.py kanca | liste", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
