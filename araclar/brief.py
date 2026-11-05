#!/usr/bin/env python3
"""Koordinatör brief denetimi: sohbet AÇILMADAN ÖNCE brief taslağına uygulanır (PDF ayrımını zorlayan ikinci anahtar).

  python3 araclar/brief.py --rol pdf-cevirici --brief taslak.txt [--ek dosya.pdf]… [--acik-ceviri ders/dosya]… [--proje /yol]
  python3 araclar/brief.py --duzelt <sohbet-bağlantısı>      # var olan sohbete tek mesaj taslağı; yeni sohbet açılmaz
  python3 araclar/brief.py --kendini-dene

Kodlar:
  B1 HATA  PDF/slayt/görsel (--ek ya da brief'te .pdf/.pptx/.png/.jpg yolu) var ve rol pdf-cevirici değil -> çıkış kodu 3, yönlendirme basılır
           (çoktan seçmeli soru dosyası için rol soru-seti serbest)
  B2 HATA  rol pdf-cevirici ve brief çeviri dışı iş taşıyor (plan, anlatım, test/soru hazırla, özet, "ayrıca", "ardından") -> çıkış kodu 1;
           izin verilen tek ek: bitince `Rol: unite` anlatım sohbeti isteği
  B3 UYARI aynı kaynak için pdf-metin/ altında metin var ya da --acik-ceviri listesinde -> yeni çeviri sohbeti açma
  B4       --duzelt: yeni brief değil, var olan sohbete tek mesaj taslağı basılır
  B0 UYARI brief ilk satırı "AI-ders oku. Rol: <rol>. …" ile başlamıyor
Sınır: araç koordinatörün çalıştırmasına bağlıdır, zorlayıcı kapı değil, ikinci anahtardır.
"""
import argparse
import os
import re
import sys

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)
sys.path.insert(0, BURASI)
from kaynak import ham_mi  # noqa: E402

HAM_YOL = re.compile(r"[^\s\"'<>()]+\.(?:pdf|pptx?|png|jpe?g|heic|gif|webp)\b", re.I)
IS_SOZ = re.compile(
    r"\bplan\w*|\banlat\w*|\banlatım\w*|\bözet\w*|\bayrıca\b|\bardından\b|\bsonrasında\b|\bve\s+sonra\b|"
    r"\b(?:test|sınav|soru)\w*\s+(?:hazırla|yap|üret|çıkar)\w*|\b(?:hazırla|yap|üret)\w*\s+(?:test|sınav|soru)\w*|\bçalışma\s+planı\b|\bnot\s+çıkar\w*",
    re.I)
IZINLI = re.compile(r"anlatım\s+sohbeti|rol:\s*unite|rol\s+unite", re.I)


def kucuk(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


def slug(ad):
    ad = os.path.splitext(os.path.basename(ad))[0]
    ad = kucuk(ad).translate(str.maketrans({"ı": "i", "ğ": "g", "ü": "u", "ş": "s", "ö": "o", "ç": "c"}))
    return re.sub(r"[^a-z0-9]+", "-", ad).strip("-")


def brief_ders(brief):
    m = re.search(r"Ders:\s*([A-Za-z0-9\-]+)", brief)
    return m.group(1).lower() if m else ""


def cevrilmis_mi(ders, dosya, proje):
    """pdf-metin altında dosyanın adıyla (slug) eşleşen metin var mı."""
    sl = slug(dosya)
    d = os.path.join(proje, "dersler", ders, "pdf-metin") if ders else ""
    if d and os.path.isdir(d):
        for f in os.listdir(d):
            if f.endswith(".md") and slug(f) == sl:
                return True
    return False


def denetle(rol, brief, ekler=(), acik=(), proje=""):
    """-> (bulgular [(HATA|UYARI, kod, metin)], çıkış kodu)."""
    b, kod = [], 0
    proje = proje or os.environ.get("AI_DERS_PROJE") or "/mnt/project-files"
    ilk = brief.strip().splitlines()[0] if brief.strip() else ""
    if not re.match(r"AI-ders oku\.\s*Rol:\s*[\w\-]+", ilk):
        b.append(("UYARI", "B0", "brief ilk satırı \"AI-ders oku. Rol: <rol>. Ders: <ders>, <ünite/konu>. Kod: <kod>.\" ile başlamalı"))
    anahtarli = [m.group(1).strip() for m in re.finditer(r"(?:Dosya|Kaynak):\s*(.+?\.(?:pdf|pptx?|png|jpe?g|heic|gif|webp))\b", brief, re.I)]   # boşluklu dosya adı
    ham = [e for e in ekler if ham_mi(e)] + anahtarli + [y for y in HAM_YOL.findall(brief) if not any(y in a for a in anahtarli)]
    ham = list(dict.fromkeys(ham))
    if ham and rol not in ("pdf-cevirici", "soru-seti"):
        b.append(("HATA", "B1", f"{', '.join(ham)} çevrilmemiş kaynak ve rol {rol}; bu sohbet açılmaz. Önce Rol: pdf-cevirici sohbeti aç, metin hazır olunca metin yoluyla ayrı anlatım sohbeti"))
        kod = 3
    if rol == "pdf-cevirici":
        govde = "\n".join(s for s in brief.splitlines() if not IZINLI.search(s))
        govde = IZINLI.sub(" ", govde)
        bulunan = sorted({m.group(0).strip() for m in IS_SOZ.finditer(kucuk(govde))})
        if bulunan:
            b.append(("HATA", "B2", f"çeviri sohbetinin brief'inde çeviri dışı iş var ({', '.join(bulunan)}). Çeviri sohbeti yalnız çevirir; başka işi ayrı sohbete ver. Bitince anlatım sohbeti isteği zaten rolün işi"))
            kod = kod or 1
    ders = brief_ders(brief)
    for yol in ham:
        sl = slug(yol)
        if cevrilmis_mi(ders, yol, proje):
            b.append(("UYARI", "B3", f"{os.path.basename(yol)} için pdf-metin/ altında metin var; yeni çeviri sohbeti açma, metni kullan"))
        elif any(slug(a.split("/")[-1]) == sl for a in acik):
            b.append(("UYARI", "B3", f"{os.path.basename(yol)} zaten çevriliyor (açık çeviri sohbeti var); ikinci çeviri sohbeti açma"))
    return b, kod


def duzelt_taslak(baglanti):
    return (f"Var olan sohbete TEK mesaj: {baglanti}\n\n"
            "YENİ SOHBET AÇMA. Düzeltme, o sohbete gidecek bir mesajdır; yeni brief ya da ikinci çeviri sohbeti açmak çeviriyi sahipsiz bırakır.\n"
            "Mesaj taslağı: \"Düzeltme: <ne yanlıştı>. Doğrusu: <ne olmalı>. Kaldığın yerden devam et; yeni sohbet açılmadı.\"")


def yazdir(b):
    for sev, kod, m in b:
        print(f"  {sev} {kod}: {m}")


def kendini_dene():
    import tempfile
    sorun = []

    def dene(ad, kosul):
        print(("geçti" if kosul else "BAŞARISIZ") + " · " + ad)
        if not kosul:
            sorun.append(ad)
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "dersler", "technical-english-1", "pdf-metin"))
        open(os.path.join(d, "dersler", "technical-english-1", "pdf-metin", "technical-english-5.md"), "w").write("[[SAYFA 1 | pdf 1]]\nx")
        temiz = "AI-ders oku. Rol: pdf-cevirici. Ders: food-chemistry-1, Gıda Kimyası 6. Kod: A1B3C3D1E3F1G2H1I1J2.\nDosya: /mnt/project-files/uploads/gida-kimyasi-6.pdf\nKonu: indeksteki ilk konu."
        b, k = denetle("pdf-cevirici", temiz, proje=d)
        dene("temiz çeviri brief'i geçer (bulgu yok, çıkış 0)", k == 0 and not [x for x in b if x[0] == "HATA"])
        b, k = denetle("unite", "AI-ders oku. Rol: unite. Ders: x, y. Kod: A1.", ["slayt.pdf"], proje=d)
        dene("B1: rol unite + .pdf eki -> çıkış 3", k == 3 and any(x[1] == "B1" for x in b))
        b, k = denetle("unite", "AI-ders oku. Rol: unite. Ders: x, y. Kod: A1.\nKaynak: uploads/slayt.pptx", proje=d)
        dene("B1: brief metnindeki .pptx yolu da yakalanır", k == 3)
        b, k = denetle("soru-seti", "AI-ders oku. Rol: soru-seti. Ders: x. Kod: A1.\nKaynak: uploads/sorular.pdf", proje=d)
        dene("B1: soru-seti rolü serbest", k == 0)
        b, k = denetle("pdf-cevirici", "AI-ders oku. Rol: pdf-cevirici. Ders: technical-english-1, Unit 5. Kod: A1.\nDosya: uploads/te5.pdf\nÇevir ve ayrıca 12 soruluk plan hazırla.", proje=d)
        dene("B2: 've planı da yap' -> HATA, çıkış 1", k == 1 and any(x[1] == "B2" for x in b))
        b, k = denetle("pdf-cevirici", "AI-ders oku. Rol: pdf-cevirici. Ders: x, y. Kod: A1.\nDosya: uploads/a.pdf\nÇevirdikten sonra konuyu anlat.", proje=d)
        dene("B2: 'konuyu anlat' -> HATA", k == 1)
        b, k = denetle("pdf-cevirici", temiz + "\nBitince koordinatörden Rol: unite anlatım sohbeti iste.", proje=d)
        dene("B2: bitince Rol: unite anlatım sohbeti isteği serbest", k == 0 and not [x for x in b if x[1] == "B2"])
        b, k = denetle("pdf-cevirici", "AI-ders oku. Rol: pdf-cevirici. Ders: technical-english-1, Unit 5. Kod: A1.\nDosya: uploads/Technical English 5.pdf", proje=d)
        dene("B3: metni zaten var -> UYARI", any(x[1] == "B3" for x in b) and k == 0)
        b, k = denetle("pdf-cevirici", "AI-ders oku. Rol: pdf-cevirici. Ders: x, y. Kod: A1.\nDosya: uploads/Yeni Ders 3.pdf", acik=["x/yeni-ders-3"], proje=d)
        dene("B3: açık çeviri sohbeti listesinde -> UYARI", any(x[1] == "B3" for x in b))
        b, k = denetle("pdf-cevirici", "Çevir şunu", proje=d)
        dene("B0: ilk satır biçimi UYARI", any(x[1] == "B0" for x in b))
    t = duzelt_taslak("https://claude.ai/code/x")
    dene("B4: düzeltme taslağı yeni sohbet açılmamasını söyler", "YENİ SOHBET AÇMA" in t)
    print("KENDİNİ DENEME " + ("GEÇTİ" if not sorun else "BAŞARISIZ: " + ", ".join(sorun)))
    return 1 if sorun else 0


def ana(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rol")
    ap.add_argument("--brief", help="brief taslağı dosyası (sohbet açılmadan önce)")
    ap.add_argument("--ek", action="append", default=[])
    ap.add_argument("--acik-ceviri", action="append", default=[], help="şu an çevrilen kaynak: <ders>/<dosya adı>")
    ap.add_argument("--proje", default="")
    ap.add_argument("--duzelt", help="var olan sohbetin bağlantısı: yeni brief yerine tek mesaj taslağı")
    ap.add_argument("--kendini-dene", action="store_true")
    a = ap.parse_args(argv)
    if a.kendini_dene:
        return kendini_dene()
    if a.duzelt:
        print(duzelt_taslak(a.duzelt))
        return 0
    if not a.rol or not a.brief:
        ap.error("--rol ve --brief gerekli (ya da --duzelt)")
    brief = open(a.brief, encoding="utf-8").read()
    b, kod = denetle(a.rol, brief, a.ek, a.acik_ceviri, a.proje)
    if not b:
        print("brief temiz: sohbet açılabilir")
        return 0
    yazdir(b)
    if kod == 3:
        print("\n" + open(os.path.join(KOK, "gorevler", "pdf-yonlendir.md"), encoding="utf-8").read())
    elif kod:
        print("\nSohbet AÇMA; brief'i düzelt.")
    return kod


if __name__ == "__main__":
    sys.exit(ana())
