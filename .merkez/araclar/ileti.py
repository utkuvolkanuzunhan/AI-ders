#!/usr/bin/env python3
"""Commit iletisi kuralı ve git eşitleme kancaları.

Yazım tarifi: mimari/is-tarifleri/ileti.md

Volkan'ın kuralı (2026-11-17): her ajan işe başlamadan çeker (pull), bitince gönderir (push); her commit iletisi ne istendiğini,
ne yapıldığını ve ikisi arasındaki farkı birkaç Türkçe cümleyle özetler.

Kullanım:
  python araclar/ileti.py denetle <ileti-dosyasi>   # .githooks/commit-msg çağırır; kural dışı ileti 1 ile reddedilir
  python araclar/ileti.py basla                      # Claude Code SessionStart: uzak dal ilerideyse "önce çek" uyarısı
  python araclar/ileti.py bitir                      # Claude Code Stop: gönderilmemiş commit varsa durmayı bir kez engeller

İleti biçimi (başlık satırından sonra, her biri kendi satırında başlar):
  İstenen: <bir iki cümle>
  Yapılan: <bir iki cümle>
  Fark: <istenenden sapma; yoksa "Yok." ya da "Fark yok.">
Birleştirme ("Merge ...") ve geri alma ("Revert ...") iletileri ile `fixup!`/`squash!` muaf. Kancalar işi hiçbir koşulda bozmaz.
Yalnızca standart kitaplık.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ALANLAR = (("İstenen", "Istenen"), ("Yapılan", "Yapilan"), ("Fark",))
MUAF = re.compile(r"^(Merge |Revert |fixup! |squash! |amend! )")
EN_AZ_HARF = 3          # alan metninde en az bu kadar harf (boş ya da "-" geçmez)
GIT_SURESI = 4          # sn: kancada ağ beklemesi tavanı


def _satirlar(metin: str) -> list[str]:
    return [s for s in metin.splitlines() if not s.startswith("#")]


def denetle(metin: str) -> list[str]:
    """Eksik ya da boş alanların listesi. Boş liste: ileti kurala uyar."""
    satirlar = _satirlar(metin)
    govde = "\n".join(satirlar).strip()
    if not govde:
        return ["ileti boş"]
    if MUAF.match(govde):
        return []
    sorunlar = []
    for adlar in ALANLAR:
        desen = re.compile(r"^\s*(?:" + "|".join(re.escape(a) for a in adlar) + r")\s*:\s*(.*)$", re.IGNORECASE)
        bulunan = next((m for s in satirlar[1:] if (m := desen.match(s))), None)
        if bulunan is None:
            sorunlar.append(f"'{adlar[0]}:' satırı yok")
        elif len(re.findall(r"[^\W\d_]", bulunan.group(1))) < EN_AZ_HARF:
            sorunlar.append(f"'{adlar[0]}:' boş")
    return sorunlar


def _git(*arg: str, sure: int = GIT_SURESI) -> str | None:
    try:
        s = subprocess.run(["git", *arg], capture_output=True, text=True, timeout=sure)
    except (OSError, subprocess.SubprocessError):
        return None
    return s.stdout.strip() if s.returncode == 0 else None


def ileri_geri() -> tuple[int, int] | None:
    """(yerelde olup uzakta olmayan, uzakta olup yerelde olmayan) commit sayısı; üst dal yoksa None."""
    sayi = _git("rev-list", "--left-right", "--count", "HEAD...@{upstream}")
    if not sayi:
        return None
    try:
        ileri, geri = (int(x) for x in sayi.split())
    except ValueError:
        return None
    return ileri, geri


def basla() -> str:
    """SessionStart metni: önce çek."""
    _git("fetch", "--quiet")
    durum = ileri_geri()
    dal = _git("rev-parse", "--abbrev-ref", "HEAD") or "?"
    if durum is None:
        return f"Eşitleme: '{dal}' dalının uzak karşılığı yok. İşe başlamadan doğru dalda olduğundan emin ol; bitince `git push -u origin {dal}`."
    ileri, geri = durum
    if geri:
        return f"EŞİTLEME: '{dal}' uzak daldan {geri} commit geride. İşe başlamadan `git pull --ff-only` çalıştır."
    if ileri:
        return f"Eşitleme: '{dal}' dalında gönderilmemiş {ileri} commit var. Bitince `git push`."
    return ""


def bitir(veri: dict) -> dict | None:
    """Stop: gönderilmemiş commit varsa durmayı bir kez engeller (stop_hook_active iken yeniden engellemez)."""
    if veri.get("stop_hook_active"):
        return None
    durum = ileri_geri()
    if durum is None or durum[0] == 0:
        return None
    return {"decision": "block",
            "reason": f"Gönderilmemiş {durum[0]} commit var. Kural: iş bitince `git push` (zorla gönderme yok). "
                      "Gönderemiyorsan nedenini yanıtında yaz."}


def main(argv: list[str] | None = None) -> int:
    for akis in (sys.stdout, sys.stderr):
        if hasattr(akis, "reconfigure"):
            akis.reconfigure(encoding="utf-8", errors="replace")
    argv = list(sys.argv[1:] if argv is None else argv)
    komut = argv[0] if argv else ""
    if komut == "denetle" and len(argv) == 2:
        try:
            metin = Path(argv[1]).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return 0  # ileti okunamıyorsa git kendi hatasını verir
        sorunlar = denetle(metin)
        if sorunlar:
            print("commit-msg: ileti kurala uymuyor (" + "; ".join(sorunlar) + ").\n"
                  "Başlıktan sonra üç satır gerekir:\n"
                  "  İstenen: <ne istendi, bir iki cümle>\n  Yapılan: <ne yapıldı, bir iki cümle>\n"
                  "  Fark: <istenenden sapma ya da 'Yok.'>", file=sys.stderr)
            return 1
        return 0
    if komut in ("basla", "bitir"):
        cikti = ""
        try:
            if os.environ.get("CLAUDE_PROJECT_DIR"):
                os.chdir(os.environ["CLAUDE_PROJECT_DIR"])
            if komut == "basla":
                cikti = basla()
            else:
                veri = json.loads(sys.stdin.read() or "{}")
                ret = bitir(veri if isinstance(veri, dict) else {})
                cikti = json.dumps(ret, ensure_ascii=False) if ret else ""
        except Exception:  # noqa: BLE001 - kanca oturumu bozmaz
            cikti = ""
        if cikti:
            print(cikti)
        return 0
    print("Kullanım: python araclar/ileti.py denetle <dosya> | basla | bitir", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
