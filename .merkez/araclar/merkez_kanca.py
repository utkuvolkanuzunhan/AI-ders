#!/usr/bin/env python3
"""Merkez kopyasının oturum başı denetimi (başka depolarda `.merkez/araclar/merkez_kanca.py` olarak çalışır).

Yazım tarifi: mimari/is-tarifleri/dagitim.md

Claude Code SessionStart kancası. Üç şey yapar, kısa basar, işi hiçbir koşulda bozmaz (her zaman 0 ile çıkar):
  1. `.merkez/SURUM.json` içindeki her dosyanın özetini yeniden hesaplar; değişen ya da eksik dosyayı söyler.
  2. Depoda `.githooks/` varsa ve `core.hooksPath` başka bir yeri gösteriyorsa onu `.githooks` yapar
     (yalnız bu deponun yerel git ayarı; geri almak: `git config --unset core.hooksPath`).
  3. volkan-merkez bu bilgisayarda bulunursa (`VOLKAN_MERKEZ` ortam değişkeni ya da kardeş klasör `../volkan-merkez`)
     kaynak dosyaların özetini karşılaştırır; kopya eskiyse yeniden dağıtma komutunu söyler.

Kullanım:
  python .merkez/araclar/merkez_kanca.py kanca     # SessionStart
  python .merkez/araclar/merkez_kanca.py durum     # aynı denetim, insan için
Yalnızca standart kitaplık.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent          # kopyada `.merkez/`, merkezde depo kökü
SURUM_ADI = "SURUM.json"


def ozet(yol: Path) -> str | None:
    try:
        return hashlib.sha256(yol.read_bytes()).hexdigest()
    except OSError:
        return None


def surum_oku(merkez_klasoru: Path) -> dict | None:
    try:
        veri = json.loads((merkez_klasoru / SURUM_ADI).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return veri if isinstance(veri, dict) else None


def bozulanlar(depo: Path, surum: dict) -> list[str]:
    """SURUM.json'daki özetle uyuşmayan ya da eksik dosyalar (depo köküne göre yol)."""
    sonuc = []
    for hedef, kayit in sorted((surum.get("dosyalar") or {}).items()):
        if isinstance(kayit, dict) and ozet(depo / hedef) != kayit.get("sha"):
            sonuc.append(hedef)
    return sonuc


def merkez_bul(depo: Path) -> Path | None:
    adaylar = []
    if os.environ.get("VOLKAN_MERKEZ"):
        adaylar.append(Path(os.environ["VOLKAN_MERKEZ"]))
    adaylar.append(depo.parent / "volkan-merkez")
    for aday in adaylar:
        if (aday / "harita.json").is_file() and (aday / "araclar" / "dagitim.py").is_file():
            return aday
    return None


def eskiyenler(merkez: Path, surum: dict) -> list[str]:
    """Merkezdeki kaynağı kopya alındıktan sonra değişmiş dosyalar."""
    sonuc = []
    for hedef, kayit in sorted((surum.get("dosyalar") or {}).items()):
        if not isinstance(kayit, dict) or not kayit.get("kaynak"):
            continue
        if ozet(merkez / kayit["kaynak"]) != kayit.get("kaynak_sha"):
            sonuc.append(hedef)
    return sonuc


def _git(depo: Path, *arg: str) -> str | None:
    try:
        return subprocess.run(["git", *arg], cwd=depo, capture_output=True, text=True, timeout=4).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def kanca_yolu_kur(depo: Path) -> str | None:
    """`.githooks/` varsa `core.hooksPath`'i ona çevirir. Ne yapıldığını döner; gerek yoksa None."""
    if not (depo / ".githooks").is_dir() or _git(depo, "rev-parse", "--git-dir") in (None, ""):
        return None
    if _git(depo, "config", "--get", "core.hooksPath") == ".githooks":
        return None
    if _git(depo, "config", "core.hooksPath", ".githooks") is None:
        return "git kancaları kurulamadı: `git config core.hooksPath .githooks` çalıştır"
    return "git kancaları kuruldu (core.hooksPath .githooks)"


def denetim(depo: Path, merkez_klasoru: Path, kur: bool = True) -> list[str]:
    surum = surum_oku(merkez_klasoru)
    if surum is None:
        return [f"MERKEZ: {merkez_klasoru.name}/{SURUM_ADI} okunamadı; kurallar ve kancalar doğrulanamıyor. "
                "volkan-merkez'de `python araclar/dagitim.py uygula <bu-depo>` çalıştır."]
    satirlar = []
    bozuk = bozulanlar(depo, surum)
    if bozuk:
        satirlar.append("MERKEZ UYARI: elle değişmiş ya da eksik merkez dosyası: " + ", ".join(bozuk)
                        + ". Bunları değiştirme; volkan-merkez'den yeniden dağıt.")
    if kur and (not_ := kanca_yolu_kur(depo)):
        satirlar.append("MERKEZ: " + not_)
    merkez = merkez_bul(depo)
    if merkez is not None:
        eski = eskiyenler(merkez, surum)
        if eski:
            satirlar.append(f"MERKEZ: kopya eski ({len(eski)} dosya). Güncellemek için volkan-merkez'de: "
                            f"python araclar/dagitim.py uygula {depo}")
    if not satirlar:
        satirlar.append(f"MERKEZ: kurallar {surum.get('kaynak_commit', '?')[:7]} ({surum.get('tarih', '?')[:10]}), "
                        "kancalar sağlam. Önce .merkez/KURALLAR.md; bu deponun kuralları üstündür.")
    return satirlar


def main(argv: list[str] | None = None) -> int:
    for akis in (sys.stdout, sys.stderr):
        if hasattr(akis, "reconfigure"):
            akis.reconfigure(encoding="utf-8", errors="replace")
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] not in (["kanca"], ["durum"]):
        print("Kullanım: python .merkez/araclar/merkez_kanca.py kanca | durum", file=sys.stderr)
        return 2
    depo = Path(os.environ.get("CLAUDE_PROJECT_DIR") or KOK.parent)
    try:
        print("\n".join(denetim(depo, depo / ".merkez")))
    except Exception as hata:  # noqa: BLE001 - kanca işi hiçbir koşulda bozmaz
        print(f"MERKEZ: denetim çalışmadı ({type(hata).__name__})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
