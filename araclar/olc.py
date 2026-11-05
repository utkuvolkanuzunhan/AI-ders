#!/usr/bin/env python3
"""Okuma ölçer: bir sohbetin zorunlu okumasını KB ve yaklaşık token olarak basar.

Kullanım:
  python3 araclar/olc.py --rol unite --ders food-chemistry-1
  python3 araclar/olc.py --rol unite --ders food-chemistry-1 --proje /yol/proje --talimat talimat.txt --memory MEMORY.md
  python3 araclar/olc.py --rol unite --ders food-chemistry-1 --bolumler     # paketin bölüm bölüm dökümü
  python3 araclar/olc.py --rol unite --ders food-chemistry-1 --en-fazla 120  # toplam KB sınırı; aşılırsa çıkış kodu 1
  python3 araclar/olc.py --kendini-dene

Ne sayar (hepsi sohbetin açılışta okuduğu şeyler):
  paket           araclar/paket.py çıktısı (çekirdek + rol + görevler + seçenekler + alan)
  CLAUDE.md       proje klasöründeki başlangıç haritası
  ayarlar.md      yerel/ayarlar.md
  widget.md       yerel/widget.md
  profil.json     yerel/profil.json (yoksa eski adı denetim.json)
  tema.json       yerel/tema.json
  hafiza.md       dersler/<ders>/hafiza.md
  talimat, memory --talimat / --memory ile verilen dosyalar (proje talimatı ve proje hafıza dizini; araç bunları kendisi bulamaz)

Token tahmini yaklaşıktır: Türkçe/İngilizce karışık metinde ~3,2 karakter = 1 token alınır (karakter sayısı, bayt değil).
Dosya yoksa satırda "yok" yazılır ve toplama girmez. Proje klasörü: --proje, yoksa AI_DERS_PROJE, yoksa /mnt/project-files.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KARAKTER_TOKEN = 3.2


def token(metin):
    return int(round(len(metin) / KARAKTER_TOKEN, -1))


def oku(yol):
    with open(yol, encoding="utf-8", errors="replace") as f:
        return f.read()


def paket_cikti(rol, ders, kod="", alan=""):
    kom = [sys.executable, os.path.join(KOK, "araclar", "paket.py"), "--rol", rol]
    if ders:
        kom += ["--ders", ders]
    if kod:
        kom += ["--kod", kod]
    if alan:
        kom += ["--alan", alan]
    r = subprocess.run(kom, capture_output=True, text=True, cwd=KOK)
    if r.returncode != 0:
        raise RuntimeError("paket.py çıkış kodu %d: %s" % (r.returncode, (r.stderr or r.stdout).strip()[:300]))
    return r.stdout


def paket_bolumleri(metin):
    """Paketi en üst başlıklara (# ...) böler -> [(başlık, bayt)]. Kod bloklarındaki # satırları sayılmaz."""
    out, ad, say, kod = [], "(başlangıç)", 0, False
    for satir in metin.splitlines(keepends=True):
        if satir.lstrip().startswith("```"):
            kod = not kod
        if not kod and re.match(r"# \S", satir):
            out.append((ad, say))
            ad, say = satir.strip()[2:], 0
        say += len(satir.encode("utf-8"))
    out.append((ad, say))
    return [(a, n) for a, n in out if n]


def kalemler(a):
    proje = a.proje or os.environ.get("AI_DERS_PROJE") or "/mnt/project-files"
    k = []
    kod = a.kod
    profil_yolu = os.path.join(proje, "yerel", "profil.json")
    eski_yolu = os.path.join(proje, "yerel", "denetim.json")
    if not kod and os.path.isfile(profil_yolu):
        try:
            kod = json.loads(oku(profil_yolu)).get("kod", "") or ""
        except ValueError:
            kod = ""
    paket = paket_cikti(a.rol, a.ders, kod, a.alan)
    k.append(("paket", "paket.py --rol %s%s" % (a.rol, " --ders " + a.ders if a.ders else ""), paket))
    dosyalar = [
        ("CLAUDE.md", os.path.join(proje, "CLAUDE.md")),
        ("ayarlar.md", os.path.join(proje, "yerel", "ayarlar.md")),
        ("widget.md", os.path.join(proje, "yerel", "widget.md")),
        ("profil.json", profil_yolu if os.path.isfile(profil_yolu) else eski_yolu),
        ("tema.json", os.path.join(proje, "yerel", "tema.json")),
    ]
    if a.ders:
        dosyalar.append(("hafiza.md", os.path.join(proje, "dersler", a.ders, "hafiza.md")))
    if a.talimat:
        dosyalar.append(("talimat", a.talimat))
    for m in a.memory or []:
        dosyalar.append(("memory", m))
    for ad, yol in dosyalar:
        k.append((ad, yol, oku(yol) if os.path.isfile(yol) else None))
    return k, paket


def tablo(k):
    sat = ["| Kalem | KB | ~token | Yol |", "|---|---:|---:|---|"]
    top_kb = top_t = 0.0
    for ad, yol, metin in k:
        if metin is None:
            sat.append("| %s | yok | yok | %s |" % (ad, os.path.basename(yol) if ad != "paket" else yol))
            continue
        kb = len(metin.encode("utf-8")) / 1024
        t = token(metin)
        top_kb += kb
        top_t += t
        sat.append("| %s | %.1f | %d | %s |" % (ad, kb, t, yol if ad == "paket" else os.path.basename(yol)))
    sat.append("| **Toplam** | **%.1f** | **%d** | |" % (top_kb, top_t))
    return "\n".join(sat), top_kb, top_t


def ana(argv=None):
    ap = argparse.ArgumentParser(description="Okuma ölçer: sohbetin zorunlu okumasını KB ve yaklaşık token olarak basar.")
    ap.add_argument("--rol", default="unite")
    ap.add_argument("--ders", default="")
    ap.add_argument("--kod", default="")
    ap.add_argument("--alan", default="")
    ap.add_argument("--proje", default="")
    ap.add_argument("--talimat", default="", help="proje talimatı dosyası (varsa)")
    ap.add_argument("--memory", action="append", help="proje hafıza dosyası (birden çok verilebilir)")
    ap.add_argument("--bolumler", action="store_true", help="paketi başlık başlık döker")
    ap.add_argument("--en-fazla", type=float, default=0, help="toplam KB sınırı; aşılırsa çıkış kodu 1")
    ap.add_argument("--kendini-dene", action="store_true")
    a = ap.parse_args(argv)
    if a.kendini_dene:
        return kendini_dene()
    try:
        k, paket = kalemler(a)
    except RuntimeError as e:
        print("olc.py: %s" % e, file=sys.stderr)
        return 2
    t, kb, tk = tablo(k)
    print(t)
    if a.bolumler:
        print("\nPaket bölümleri:\n\n| Bölüm | KB |\n|---|---:|")
        for ad, n in paket_bolumleri(paket):
            print("| %s | %.1f |" % (ad, n / 1024))
    if a.en_fazla and kb > a.en_fazla:
        print("\nSINIR AŞILDI: %.1f KB > %.1f KB" % (kb, a.en_fazla), file=sys.stderr)
        return 1
    return 0


def kendini_dene():
    sorun = []

    def dene(ad, ok):
        print(("geçti" if ok else "BAŞARISIZ") + " · " + ad)
        if not ok:
            sorun.append(ad)

    dene("token: 320 karakter ≈ 100 token", token("a" * 320) == 100)
    b = paket_bolumleri("giriş\n# A\nmetin\n```\n# yorum\n```\n# B\nx\n")
    dene("bölümler: kod bloğundaki # başlık sayılmaz", [x[0] for x in b] == ["(başlangıç)", "A", "B"])
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "yerel"))
        os.makedirs(os.path.join(d, "dersler", "food-chemistry-1"))
        open(os.path.join(d, "CLAUDE.md"), "w", encoding="utf-8").write("c" * 2048)
        open(os.path.join(d, "yerel", "ayarlar.md"), "w", encoding="utf-8").write("a" * 1024)
        r = subprocess.run([sys.executable, os.path.abspath(__file__), "--rol", "unite", "--ders", "food-chemistry-1", "--proje", d],
                           capture_output=True, text=True)
        dene("çalışır, çıkış kodu 0", r.returncode == 0)
        dene("var olan dosya KB ile, olmayan 'yok' ile basılır",
             "| CLAUDE.md | 2.0 |" in r.stdout and "| ayarlar.md | 1.0 |" in r.stdout and "| widget.md | yok |" in r.stdout)
        dene("paket satırı ve toplam var", "| paket |" in r.stdout and "| **Toplam** |" in r.stdout)
        r2 = subprocess.run([sys.executable, os.path.abspath(__file__), "--rol", "unite", "--ders", "food-chemistry-1", "--proje", d, "--en-fazla", "1"],
                            capture_output=True, text=True)
        dene("sınır aşılınca çıkış kodu 1", r2.returncode == 1)
        r3 = subprocess.run([sys.executable, os.path.abspath(__file__), "--rol", "olmayan-rol", "--proje", d], capture_output=True, text=True)
        dene("bilinmeyen rolde çıkış kodu 2", r3.returncode == 2)
    print("KENDİNİ DENEME " + ("BAŞARISIZ: " + ", ".join(sorun) if sorun else "GEÇTİ"))
    return 1 if sorun else 0


if __name__ == "__main__":
    sys.exit(ana())
