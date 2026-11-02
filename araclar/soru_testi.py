#!/usr/bin/env python3
"""Çoktan seçmeli soru seti: JSON -> post_widget'a hazır HTML (şablon W24).

Konu anlatımı DIŞINDA soru hazırlarken (yüklenen soru dosyası, deneme sınavı, "bana N soru hazırla") kullanılır.
Anlatım içindeki mini test W10'dur; bu araç ona değil, W24'e hizmet eder.

Kullanım:
  python3 araclar/soru_testi.py veri.json cikti.html            # widget HTML'i (post_widget'a aynen yapıştırılır)
  python3 araclar/soru_testi.py veri.json cikti.html --tek-sayfa  # tarayıcıda açılan tam sayfa (denemek için)
  python3 araclar/soru_testi.py veri.json --kontrol              # yalnız doğrula, dosya yazma
  python3 araclar/soru_testi.py --ornek                          # örnek veri JSON'unu yazdır
  python3 araclar/soru_testi.py --sablonu-yenile                 # W24 şablonundaki örneği ornek.json'dan yenile (sonra uret.py)

Seçenekler: --parca oto|0|N (oto: 20 soruya kadar tek, üstü en çok 15'erli eşit parçalar; 0: bölme; N: en çok N'şer),
            --gevsek (eksik "neden_yanlis" ve çeviri hata yerine uyarı olur).
Çok parçalı çıktıda dosya adına -1, -2 eklenir ve başlığa (1/2) yazılır.

Veri biçimi (JSON):
{
  "baslik": "Test başlığı", "alt_baslik": "tek satır açıklama",
  "mod": "iki" | "ogren" | "sinav",                 # varsayılan iki: açılışta Öğren / Sınav seçilir
  "yanlis_notu": "hepsi" | "secilen" | "yok",       # varsayılan hepsi: cevap verince her yanlış şıkta "neden yanlış"
  "kaynak": "ekstra" | "soru" | "ikisi",            # varsayılan ikisi: açıklamanın altında + sonda Ekstra tablosu
  "karistir": "hep" | "sorular" | "yok",            # varsayılan hep: soru ve şık sırası her başlangıçta karışır (sorular: yalnız sorular)
  "dil": "en-tr" | "tek",                            # en-tr: soru ve şık İngilizce, Türkçesi parantezde
  "sorular": [{
     "no": 1,                                         # kaynaktaki numara (yoksa sıra)
     "bolum": "Water activity",                       # isteğe bağlı: sonuçta bölüm çubukları
     "konu": "...", "konu_tr": "...",                 # isteğe bağlı kısa konu etiketi
     "soru": "EN soru", "soru_tr": "Türkçesi",
     "siklar": [{"metin": "EN şık", "tr": "Türkçesi", "neden_yanlis": "yanlış şıkta neden (doğruda YOK)", "sabit": false}, ...],  # 2-5 şık; "hepsi/hiçbiri" şıkka sabit: true
     "dogru": "B",                                    # kaynaktaki harf (ekranda karışınca harf değişir; açıklamada harf yazma)
     "aciklama": ["satır 1", "satır 2"],
     "kaynak": "Slayt 5-7",                           # isteğe bağlı (kaynak varsa her soruda yaz)
     "ipucu": "..."                                   # isteğe bağlı
  }]
}
Metin içi biçim: {pay|payda} gerçek kesir, ^{üs}, _{alt}, **kalın**. Düz metin kesir (a/b) yazma.
"""
import argparse, json, math, os, re, sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SABLON = os.path.join(KOK, "gorsel", "sablonlar", "W24-coktan-secmeli-test.html")
ORNEK = os.path.join(KOK, "gorsel", "soru-testi", "ornek.json")
ISARET = re.compile(r"/\*VERI\*/.*?/\*VERI_SON\*/", re.S)
BASLIK = re.compile(r"\A<!--.*?-->\s*", re.S)
HARF = "ABCDE"
EKSEN = {"mod": ("iki", "ogren", "sinav"), "yanlis_notu": ("hepsi", "secilen", "yok"),
         "kaynak": ("ekstra", "soru", "ikisi"), "dil": ("en-tr", "tek"), "karistir": ("hep", "sorular", "yok")}
KISA = {"iki": "i", "ogren": "o", "sinav": "s", "hepsi": "h", "secilen": "s", "yok": "y", "ekstra": "e", "soru": "s", "ikisi": "i",
        "hep": "h", "sorular": "s"}
# Karışınca anlamı bozulan şıklar ("hepsi", "hiçbiri") sabit:true olmalı; açıklama şık harfine gönderme yapmamalı
HEPSI = re.compile(r"\b(all|none|both|neither)\b[^.]*\b(above|these|them)\b|yukarıdaki|hepsi|hiçbiri|her ikisi|ikisi de", re.I)
HARFREF = re.compile(r"(?<![A-Za-zÇĞİÖŞÜçğıöşü])[A-E]\s*\)|(?<![A-Za-zÇĞİÖŞÜçğıöşü])[A-E]['’]?\s*(?:şık|option|choice)|(?:şık|option|choice|seçenek)\s+[A-E](?![A-Za-zÇĞİÖŞÜçğıöşü])", re.I)
TR_HARF = set("çğıöşüÇĞİÖŞÜ")
KELIME = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü]{4,}")  # sözcük sayılacak harf dizisi (yalnız sayı/sembol şıkları çeviri istemez)


def dogrula(d, gevsek):
    """-> (hatalar, uyarılar)"""
    hata, uyari = [], []
    soft = uyari if gevsek else hata
    if not isinstance(d, dict) or not isinstance(d.get("sorular"), list) or not d["sorular"]:
        return ["'sorular' boş ya da liste değil"], []
    if not str(d.get("baslik", "")).strip():
        hata.append("'baslik' boş")
    for a, ok in EKSEN.items():
        if d.get(a, ok[0]) not in ok:
            hata.append(f"'{a}' şunlardan biri olmalı: {', '.join(ok)}")
    ikidil = d.get("dil", "en-tr") == "en-tr"
    gorulen, dagilim, tr_toplam, tr_ozel, kaynaksiz = set(), {}, 0, 0, []
    for i, q in enumerate(d["sorular"], 1):
        n = q.get("no", i)
        et = f"soru {n}"
        if n in gorulen:
            hata.append(f"{et}: 'no' tekrar ediyor")
        gorulen.add(n)
        if not str(q.get("soru", "")).strip():
            hata.append(f"{et}: 'soru' boş")
        if ikidil:
            tr = str(q.get("soru_tr", "")).strip()
            if not tr:
                soft.append(f"{et}: 'soru_tr' (Türkçesi) boş")
            elif tr == str(q.get("soru", "")).strip():
                uyari.append(f"{et}: 'soru_tr' İngilizcesiyle aynı, çevrilmemiş olabilir")
            tr_toplam += len(tr)
            tr_ozel += sum(c in TR_HARF for c in tr)
        s = q.get("siklar")
        if not isinstance(s, list) or not 2 <= len(s) <= 5:
            hata.append(f"{et}: 'siklar' 2-5 şık olmalı")
            continue
        dg = str(q.get("dogru", "")).strip().upper()
        if len(dg) != 1 or dg not in HARF[:len(s)]:
            hata.append(f"{et}: 'dogru' {', '.join(HARF[:len(s)])} harflerinden biri olmalı (yazılan: {q.get('dogru')!r})")
            continue
        di = HARF.index(dg)
        dagilim[dg] = dagilim.get(dg, 0) + 1
        metinler = [str(x.get("metin", "")).strip() for x in s]
        if len(set(metinler)) != len(metinler):
            hata.append(f"{et}: aynı metinli şıklar var")
        for j, x in enumerate(s):
            m = metinler[j]
            if not m:
                hata.append(f"{et} şık {HARF[j]}: 'metin' boş")
            if ikidil:
                t = str(x.get("tr", "")).strip()
                if not t and KELIME.search(re.sub(r"[_^]\{[^}]*\}", "", m)):
                    soft.append(f"{et} şık {HARF[j]}: 'tr' boş (yalnız sayı/sembol şıklarda boş kalabilir)")
                elif t and t == m and KELIME.search(re.sub(r"[_^]\{[^}]*\}", "", m)):
                    uyari.append(f"{et} şık {HARF[j]}: 'tr' İngilizcesiyle aynı")
                tr_toplam += len(t)
                tr_ozel += sum(c in TR_HARF for c in t)
            if d.get("karistir", "hep") == "hep" and not x.get("sabit") and HEPSI.search(m + " " + str(x.get("tr", ""))):
                uyari.append(f"{et} şık {HARF[j]}: 'hepsi/hiçbiri' türü; karışınca anlamı bozulur, 'sabit': true yaz")
            neden = str(x.get("neden_yanlis", "")).strip()
            if j == di and neden:
                hata.append(f"{et} şık {HARF[j]}: doğru şıkta 'neden_yanlis' olmamalı")
            if j != di and not neden and d.get("yanlis_notu", "hepsi") != "yok":
                soft.append(f"{et} şık {HARF[j]}: yanlış şıkta 'neden_yanlis' yok")
        ac = q.get("aciklama")
        if isinstance(ac, str):
            ac = [ac]
        if d.get("karistir", "hep") != "yok":
            for metin in list(ac or []) + [str(x.get("neden_yanlis", "")) for x in s]:
                if HARFREF.search(metin):
                    soft.append(f"{et}: açıklama ya da not şık harfine gönderme yapıyor ('{HARFREF.search(metin).group(0).strip()}'); şıklar karışınca yanlış olur")
                    break
        if not ac or not all(str(a).strip() for a in ac):
            hata.append(f"{et}: 'aciklama' boş")
        if not str(q.get("kaynak", "")).strip():
            kaynaksiz.append(str(n))
    if tr_toplam > 300 and tr_ozel == 0:
        uyari.append("Türkçe metinde hiç ç ğ ı ö ş ü yok: karakterler düşmüş (ASCII'ye dönmüş) olabilir")
    if kaynaksiz and len(kaynaksiz) < len(d["sorular"]):
        uyari.append("kaynağı olmayan sorular: " + ", ".join(kaynaksiz))
    n = len(d["sorular"])
    if n >= 8 and dagilim and max(dagilim.values()) / n > 0.6:
        uyari.append(f"doğru cevaplar bir harfte toplanmış ({max(dagilim, key=dagilim.get)}: {max(dagilim.values())}/{n}); cevap anahtarını yeniden kontrol et")
    return hata, uyari


def donustur(d):
    """Okunur anahtarlı veri -> şablonun kısa anahtarlı verisi."""
    q = []
    for i, x in enumerate(d["sorular"], 1):
        ac = x["aciklama"] if isinstance(x["aciklama"], list) else [x["aciklama"]]
        o = [[str(s.get("metin", "")).strip(), str(s.get("tr", "")).strip(), str(s.get("neden_yanlis", "")).strip()] + ([1] if s.get("sabit") else []) for s in x["siklar"]]
        e = {"n": x.get("no", i), "e": str(x["soru"]).strip(), "r": str(x.get("soru_tr", "")).strip(), "o": o,
             "a": HARF.index(str(x["dogru"]).strip().upper()), "x": [str(a).strip() for a in ac]}
        for kisa, uzun in (("g", "bolum"), ("c", "konu"), ("ct", "konu_tr"), ("s", "kaynak"), ("h", "ipucu")):
            v = str(x.get(uzun, "")).strip()
            if v:
                e[kisa] = v
        q.append(e)
    return {"t": str(d["baslik"]).strip(), "s": str(d.get("alt_baslik", "")).strip(),
            "md": KISA[d.get("mod", "iki")], "nt": KISA[d.get("yanlis_notu", "hepsi")], "k": KISA[d.get("kaynak", "ikisi")],
            "kr": KISA[d.get("karistir", "hep")], "c": 1 if d.get("dil", "en-tr") == "en-tr" else 0, "q": q}


def bol(d, parca):
    n = len(d["sorular"])
    if parca == "0":
        return [d]
    ust = 15 if parca == "oto" else int(parca)
    if parca == "oto" and n <= 20 or ust <= 0 or n <= ust:
        return [d]
    k = math.ceil(n / ust)
    boy = math.ceil(n / k)
    out = []
    for i in range(k):
        c = dict(d)
        c["sorular"] = d["sorular"][i * boy:(i + 1) * boy]
        c["baslik"] = f"{d['baslik']} ({i + 1}/{k})"
        out.append(c)
    return out


def doldur(sablon, veri):
    js = json.dumps(veri, ensure_ascii=False, separators=(",", ":"))
    js = js.replace("</", "<\\/").replace("<!--", "<\\!--").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    if not ISARET.search(sablon):
        sys.exit("Şablonda /*VERI*/ … /*VERI_SON*/ işareti yok.")
    return ISARET.sub(lambda m: "/*VERI*/" + js + "/*VERI_SON*/", sablon, count=1)


def sarmala(html, baslik):
    b = baslik.replace("&", "&amp;").replace("<", "&lt;")
    return ("<!doctype html><html lang=\"tr\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{b}</title><style>html,body{{overflow:auto!important}}body{{margin:0;padding:10px;background:#fff;font-family:system-ui,-apple-system,sans-serif;font-size:16px}}"
            "@media(prefers-color-scheme:dark){body{background:#17212c}}</style></head><body>" + html + "</body></html>")


def yaz(yol, metin):
    with open(yol, "w", encoding="utf-8") as f:
        f.write(metin)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("veri", nargs="?")
    ap.add_argument("cikti", nargs="?")
    ap.add_argument("--tek-sayfa", action="store_true")
    ap.add_argument("--kontrol", action="store_true")
    ap.add_argument("--gevsek", action="store_true")
    ap.add_argument("--parca", default="oto")
    ap.add_argument("--ornek", action="store_true")
    ap.add_argument("--sablonu-yenile", action="store_true")
    a = ap.parse_args()
    if a.parca != "oto" and not a.parca.isdigit():
        sys.exit("--parca: oto, 0 ya da bir sayı olmalı")

    if a.ornek:
        sys.stdout.write(open(ORNEK, encoding="utf-8").read())
        return
    sab_ham = open(SABLON, encoding="utf-8").read()
    if a.sablonu_yenile:
        d = json.load(open(ORNEK, encoding="utf-8"))
        h, u = dogrula(d, False)
        if h:
            sys.exit("ornek.json hatalı:\n- " + "\n- ".join(h))
        yaz(SABLON, doldur(sab_ham, donustur(d)))
        print("W24 şablonundaki örnek yenilendi. Şimdi: python3 araclar/uret.py")
        return
    if not a.veri:
        ap.error("veri.json gerekli")
    try:
        d = json.load(open(a.veri, encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"JSON okunamadı: {e}")
    hata, uyari = dogrula(d, a.gevsek)
    for u in uyari:
        print("UYARI:", u, file=sys.stderr)
    if hata:
        print("HATA:\n- " + "\n- ".join(hata), file=sys.stderr)
        sys.exit(1)
    n = len(d["sorular"])
    if a.kontrol:
        print(f"Veri geçerli: {n} soru.")
        return
    if not a.cikti:
        ap.error("cikti.html gerekli (ya da --kontrol)")
    sab = BASLIK.sub("", sab_ham, count=1)
    parcalar = bol(d, a.parca)
    kok, uz = os.path.splitext(a.cikti)
    for i, p in enumerate(parcalar, 1):
        html = doldur(sab, donustur(p))
        if a.tek_sayfa:
            html = sarmala(html, p["baslik"])
        yol = a.cikti if len(parcalar) == 1 else f"{kok}-{i}{uz}"
        yaz(yol, html)
        kb = len(html.encode("utf-8")) / 1024
        print(f"{yol}: {len(p['sorular'])} soru, {kb:.0f} KB")
        if kb > 45 and a.parca == "0":
            print("UYARI: 45 KB üstü widget iPad'de ağır olabilir; --parca oto ile böl", file=sys.stderr)


if __name__ == "__main__":
    main()
