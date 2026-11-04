#!/usr/bin/env python3
"""Kişisel profil okuyucu: ölçülebilir tercihlerin tek makine dosyası (`yerel/profil.json`).

Kullanım:
  python3 araclar/profil.py --goster [--profil yol] [--alan eee] [--ders <ders>]   birleşik profili basar (hangi değer nereden geldi)
  python3 araclar/profil.py --dogrula [--profil yol]                               dosyayı denetler (bilinmeyen anahtar, yanlış tür = hata)
  python3 araclar/profil.py --kendini-dene

Profil dosyası kullanıcının proje klasöründe durur ve depoya GİRMEZ (kurulum/yerel-profil-sablonu.json şablondur).
Arama sırası: --profil > AI_DERS_PROFIL > ./yerel/profil.json > ./yerel/denetim.json > /mnt/project-files/yerel/profil.json
> /mnt/project-files/yerel/denetim.json. `denetim.json` eski addır; aynı anahtarları okur (geçiş süresince).
Katman sırası (sonraki öncekini ezer): depo varsayılanı < alan (alanlar/<alan>/alan.json "profil") < profil dosyası < komut satırı.
Tek kaynak bu dosyadır: anlatim_testi_ek.py profili buradan okur, anahtar listesi burada durur.
"""
import json, os, re, sys

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)
PROJE = "/mnt/project-files"


# ── anahtarlar: ad -> (tür, açıklama). Tür: "bool" "int" "str" "liste" "aralik" ya da izinli değerler kümesi ──
ANAHTAR = {
    "kod": ("kod", "ayar kodu (ör. A1B3C3...); yerel/ayarlar.md 'Kod:' satırının makine kopyası"),
    "terim_dili": ({"C1", "C2", "C3"}, "terim dili: C2 İngilizce (Türkçe); C1/C3 Türkçe (İngilizce)"),
    "terim_her_gecis": ("bool", "terim her geçişte mi yazılır"),
    "terim_muaf": ("liste", "terim denetiminin saymayacağı sözcükler"),
    "emoji": ("str", "kişisel emoji (ör. serisi sınırlı olan)"),
    "emoji_seri": ("aralik", "emoji yalnız bu uzunlukta seri yazılır (ör. 3-4)"),
    "emoji_adet": ("aralik", "bir mesajdaki toplam emoji adedi (alt-üst)"),
    "widget_emoji_yasak": ("liste", "widget içinde bulunamayacak emojiler"),
    "mini_test_soru": ("int", "her mini testteki soru sayısı"),
    "mini_test_yeri": ({"her_alt_baslik", "konu_sonu", "yok"}, "mini test nerede"),
    "tam_test": ("bool", "konu sonunda tam test var mı"),
    "test_dil": ({"en-tr", "tr", "en"}, "test soruları ve şıklarının dili"),
    "karisik_test": ("bool", "mini test soruları karışık konulardan, konu adı ipucu yok"),
    "kaynak_gosterim": ({"D1", "D2", "D3"}, "kaynak gösterimi (ayar kodundaki D)"),
    "tema": (None, "widget teması: gorsel/motor/tema-<ad>.json ya da yerel/tema.json; 'karma' eski W25 şablonları"),
    "devir_esik": ("int", "devir eşiği (Claude mesajı)"),
    "cift_aralik": ("aralik", "çift boşluk payı hata sınırı (yüzde, alt-üst)"),
    "izin": ("liste", "düz kesir sayılmayacak ek yazımlar"),
    "sozluk": ("liste", "ek terim sözlüğü yolları (proje klasörüne göre)"),
}

# Depo varsayılanı: kişisiz. Yalnız YENİ anahtarlara değer verilir; eski denetim anahtarları eksikse
# anlatim_testi.py kendi varsayılanını kullanır (davranış değişmez).
VARSAYILAN = {
    "mini_test_yeri": "her_alt_baslik",
    "tam_test": True,
    "kaynak_gosterim": "D1",
    "tema": "neobrutalism",
    "devir_esik": 10,
}


def bul(yol=None):
    """Profil dosyasının yolu (yoksa None)."""
    cwd = os.path.join(os.getcwd(), "yerel")
    adaylar = [yol, os.environ.get("AI_DERS_PROFIL"),
               os.path.join(cwd, "profil.json"), os.path.join(cwd, "denetim.json"),
               os.path.join(PROJE, "yerel", "profil.json"), os.path.join(PROJE, "yerel", "denetim.json")]
    for a in adaylar:
        if a and os.path.isfile(a):
            return a
    return None


def aralik(v):
    """'3-4' ya da [3, 4] ya da 3 -> (3, 4)."""
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return int(v[0]), int(v[1])
    a, _, b = str(v).partition("-")
    return int(a), int(b or a)


def _aralik_mi(v):
    try:
        a, b = aralik(v)
        return a <= b
    except (ValueError, TypeError):
        return False


def dogrula(p, kaynak="profil"):
    """Sözlük -> hata listesi. Bilinmeyen anahtar (alt çizgiyle başlayanlar not sayılır) ve yanlış tür hatadır."""
    hata = []
    if not isinstance(p, dict):
        return [f"{kaynak}: JSON bir sözlük değil"]
    for k, v in p.items():
        if k.startswith("_"):
            continue
        if k not in ANAHTAR:
            yakin = [a for a in ANAHTAR if a[:4] == k[:4]]
            hata.append(f"{kaynak}: bilinmeyen anahtar '{k}'" + (f" (yakın: {', '.join(yakin)})" if yakin else ""))
            continue
        tur = ANAHTAR[k][0]
        ok = True
        if tur == "bool":
            ok = isinstance(v, bool)
        elif tur == "int":
            ok = isinstance(v, int) and not isinstance(v, bool) and v >= 0
        elif tur == "str":
            ok = isinstance(v, str) and v != ""
        elif tur == "liste":
            ok = isinstance(v, list) and all(isinstance(x, str) for x in v)
        elif tur == "aralik":
            ok = _aralik_mi(v)
        elif tur == "kod":
            ok = isinstance(v, str) and re.fullmatch(r"([A-Z]\d+)+(/[\w.\-]*)?", v.replace(" ", "").upper()) is not None
        elif isinstance(tur, set):
            ok = v in tur
        elif tur is None:
            ok = isinstance(v, str) and v != ""
        if not ok:
            hata.append(f"{kaynak}: '{k}' değeri geçersiz: {v!r}" + (f" (izinli: {', '.join(sorted(tur))})" if isinstance(tur, set) else ""))
    return hata


def _dosya(yol):
    try:
        return json.load(open(yol, encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SystemExit(f"profil okunamadı ({yol}): {e}")


def alan_katmani(alan):
    """alanlar/<alan>/alan.json içindeki 'profil' sözlüğü (yoksa boş)."""
    p = os.path.join(KOK, "alanlar", alan, "alan.json") if alan else ""
    if p and os.path.isfile(p):
        return (json.load(open(p, encoding="utf-8")).get("profil") or {})
    return {}


def birlestir(yol=None, alan="", cli=None):
    """Katmanları birleştirir -> (değerler, kaynaklar). kaynaklar: anahtar -> 'varsayılan' | 'alan' | 'profil' | 'komut'."""
    deger, kaynak = {}, {}

    def ekle(katman, ad):
        for k, v in katman.items():
            if not k.startswith("_"):
                deger[k], kaynak[k] = v, ad
    ekle(VARSAYILAN, "varsayılan")
    a = alan_katmani(alan)
    h = dogrula(a, f"alanlar/{alan}/alan.json profil")
    if h:
        raise SystemExit("\n".join(h))
    ekle(a, "alan")
    if yol:
        p = _dosya(yol)
        h = dogrula(p, yol)
        if h:
            raise SystemExit("\n".join(h))
        ekle(p, "profil")
    if cli:
        h = dogrula(cli, "komut satırı")
        if h:
            raise SystemExit("\n".join(h))
        ekle(cli, "komut")
    return deger, kaynak


def ayara_cevir(deger, yol=None):
    """Birleşik değerler -> anlatim_testi'nin ayar sözlüğü (eski profil_oku ile aynı anahtarlar ve türler)."""
    kok = os.path.dirname(os.path.dirname(os.path.abspath(yol))) if yol else PROJE   # yerel/'in üstü = proje klasörü
    ayar = {"profil_yolu": yol, "proje_kok": kok}
    for k in ("emoji", "terim_dili", "terim_her_gecis", "mini_test_soru", "test_dil", "karisik_test", "widget_emoji_yasak", "terim_muaf",
              "mini_test_yeri", "tam_test", "kaynak_gosterim", "tema", "devir_esik", "kod"):
        if k in deger:
            ayar[k] = deger[k]
    if "emoji_seri" in deger:
        v = deger["emoji_seri"]
        ayar["emoji_seri"] = [int(x) for x in (v if isinstance(v, list) else str(v).replace("-", ",").split(","))]
    if "emoji_adet" in deger:
        ayar["emoji_adet"] = aralik(deger["emoji_adet"])
    if "cift_aralik" in deger:
        ayar["cift_aralik"] = aralik(deger["cift_aralik"])
    if "izin" in deger:
        ayar["izin"] = set(deger["izin"])
    ayar["sozluk_yollari"] = [y if os.path.isabs(y) else os.path.join(kok, y) for y in deger.get("sozluk", [])]
    return ayar


def oku(yol=None, alan="", cli=None):
    """Tek giriş noktası: profil dosyası (yoksa yalnız varsayılan) -> anlatim_testi ayar sözlüğü.
    Dosya yoksa eski davranış korunur: boş sözlük (kişisel kural yok)."""
    if not yol:
        return {}
    deger, _ = birlestir(yol, alan, cli)
    return ayara_cevir(deger, yol)


def goster(yol, alan, cli):
    deger, kaynak = birlestir(yol, alan, cli)
    print("Profil dosyası: " + (yol or "yok (yalnız depo varsayılanı)") + (f" · alan: {alan}" if alan else ""))
    for k in ANAHTAR:
        if k in deger:
            print(f"  {k:20} {json.dumps(deger[k], ensure_ascii=False):30} [{kaynak[k]}]")
    eksik = [k for k in ANAHTAR if k not in deger]
    if eksik:
        print("  (değeri yok, araç kendi varsayılanını kullanır: " + ", ".join(eksik) + ")")


# ── kendini deneme ──
def kendini_dene():
    import tempfile
    sorun = []

    def beklenen(ad, kosul):
        print(("geçti" if kosul else "BAŞARISIZ") + " · " + ad)
        if not kosul:
            sorun.append(ad)
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "yerel"))
        yol = os.path.join(d, "yerel", "profil.json")
        json.dump({"_aciklama": "not", "terim_dili": "C2", "emoji": "*", "emoji_seri": "3-4", "mini_test_soru": 2, "test_dil": "en-tr"}, open(yol, "w"))
        a = oku(yol)
        beklenen("eski anahtarlar aynı türde okunur", a["emoji_seri"] == [3, 4] and a["mini_test_soru"] == 2 and a["terim_dili"] == "C2")
        beklenen("proje klasörü yerel/'in üstü", a["proje_kok"] == os.path.abspath(d))
        beklenen("yeni anahtarlara depo varsayılanı gelir", a["devir_esik"] == 10 and a["tam_test"] is True)
        beklenen("alt çizgili anahtar not sayılır", dogrula({"_not": 1, "tam_test": False}) == [])
        beklenen("bilinmeyen anahtar hata", len(dogrula({"mini_test_sayisi": 2})) == 1)
        beklenen("yanlış tür hata", len(dogrula({"mini_test_soru": "iki", "tam_test": "evet"})) == 2)
        beklenen("izinli küme dışı hata", len(dogrula({"terim_dili": "C9"})) == 1)
        beklenen("ters aralık hata", len(dogrula({"emoji_seri": "4-3"})) == 1)
        beklenen("kod biçimi", dogrula({"kod": "A1B3C3"}) == [] and len(dogrula({"kod": "abc"})) == 1)
        d2, k2 = birlestir(yol, cli={"devir_esik": 8})
        beklenen("komut satırı profili ezer", d2["devir_esik"] == 8 and k2["devir_esik"] == "komut" and k2["terim_dili"] == "profil")
        eski = os.path.join(d, "yerel", "denetim.json")
        os.rename(yol, eski)
        old = os.environ.pop("AI_DERS_PROFIL", None)
        cwd = os.getcwd()
        os.chdir(d)
        try:
            beklenen("denetim.json (eski ad) bulunur", bul() == os.path.join(d, "yerel", "denetim.json"))
        finally:
            os.chdir(cwd)
            if old:
                os.environ["AI_DERS_PROFIL"] = old
        try:
            json.dump({"bilinmeyen": 1}, open(yol, "w"))
            oku(yol)
            beklenen("bilinmeyen anahtarlı dosya okunamaz", False)
        except SystemExit:
            beklenen("bilinmeyen anahtarlı dosya okunamaz", True)
    print("KENDİNİ DENEME " + ("GEÇTİ" if not sorun else f"BAŞARISIZ ({len(sorun)})"))
    return 1 if sorun else 0


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profil")
    ap.add_argument("--alan", default="")
    ap.add_argument("--goster", action="store_true")
    ap.add_argument("--dogrula", action="store_true")
    ap.add_argument("--kendini-dene", action="store_true")
    a = ap.parse_args()
    if a.kendini_dene:
        sys.exit(kendini_dene())
    yol = bul(a.profil)
    if a.profil and not yol:
        sys.exit(f"profil bulunamadı: {a.profil}")
    if a.dogrula:
        if not yol:
            sys.exit("profil dosyası bulunamadı")
        h = dogrula(_dosya(yol), yol)
        print("\n".join(h) if h else f"{yol}: geçerli")
        sys.exit(1 if h else 0)
    goster(yol, a.alan.lower(), None)


if __name__ == "__main__":
    main()
