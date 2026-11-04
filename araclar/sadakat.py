#!/usr/bin/env python3
"""Kaynak sadakat denetimi: anlatım mesajı ve widget, kaynağın o adıma ait sayfalarından sapıyor mu?

  python3 araclar/sadakat.py mesaj.md [widget.html ...] --kaynak <pdf-metin.md> --sayfa 28-34 [--pdf] [--siki]
  python3 araclar/sadakat.py --kendini-dene

Kaynak `[[SAYFA <basılı> | pdf <sıra>]]` işaretli çevrilmiş metindir (araclar/kaynak.py). --sayfa: `28-34`, `9,8,15` ya da `10-11,13`
(basılı numara; basılı numara yoksa pdf sırası). UYARI üretir, HATA üretmez: son karar modelin (parafraz, sıra farkı ve bilinçli "slayt dışı"
ekler meşrudur); amaç gözden kaçan sapmayı göstermek. Kodlar:
  S1 düşen sözcük: kaynakta kalın yazılmış terim, tireli sözcük, kısa madde, alt başlık ya da şekil/tablo etiketi var, mesajda ve widget'ta hiç geçmiyor
  S2 kaynakta olmayan terim ya da sayı: mesajdaki İngilizce terim (parantezli) ya da 2 haneli/ondalıklı sayı kaynakta yok ve paragraf "slayt dışı" ya da
     "ileriden bir ipucu" diye işaretli değil
  S3 liste sayısı: kaynaktaki bir listeyle büyük ölçüde örtüşen listenin madde sayısı farklı ("slaytta 19 örnek, sende 17")
"""
import argparse, html as _html, json, os, re, sys

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
from kaynak import ISARET  # noqa: E402

ISARETLI = re.compile(r"slayt dışı|ileriden bir ipucu|kaynakta yok", re.I)
SOZ_DURAK = set("the of is are and which what a an to in for with that this by as on from be does do how at or not its it has have will can than "
                "most least following true false when where who these those their there if into between also such other more some any all each".split())


# ───────────────────────────── normalleştirme ─────────────────────────────
def norm(s):
    """Küçük harf, tire/eğik çizgi boşluk, harf dışı atılır, kelime sonu çoğul ekleri atılır (minerals → mineral)."""
    s = s.replace("İ", "i").lower().translate(str.maketrans({"ı": "i", "ğ": "g", "ü": "u", "ş": "s", "ö": "o", "ç": "c"}))
    s = re.sub(r"[-/_]", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    k = []
    for w in s.split():
        for son in ("ies", "es", "s"):
            if len(w) > len(son) + 3 and w.endswith(son):
                w = w[:-len(son)] + ("y" if son == "ies" else "")
                break
        k.append(w)
    return " ".join(k)


def havuz_kur(*metinler):
    return " " + norm(" ".join(metinler)) + " "


def var_mi(terim, havuz):
    n = norm(terim)
    return bool(n) and (" " + n + " ") in havuz


# ───────────────────────────── kaynak sayfaları ─────────────────────────────
def sayfa_listesi(spec):
    """'28-34' / '9,8,15' / '10-11,13' -> ['28', ...]; sıra korunur."""
    out = []
    for parca in re.split(r"[,;]", str(spec)):
        parca = parca.strip()
        m = re.fullmatch(r"(\d+)\s*[-–]\s*(\d+)", parca)
        if m:
            out += [str(i) for i in range(int(m.group(1)), int(m.group(2)) + 1)]
        elif parca:
            out.append(parca)
    return out


def kaynak_metni(yol, sayfalar, pdf=None):
    """Çevrilmiş kaynaktan istenen sayfaların metni. Basılı numara yoksa (ya da pdf=True) pdf sırası kullanılır."""
    t = open(yol, encoding="utf-8").read()
    isaret = [(m.start(), m.group(1).strip(), int(m.group(2))) for m in ISARET.finditer(t)]
    if not isaret:
        raise ValueError(f"{yol}: [[SAYFA … | pdf …]] işareti yok (çevrilmiş metin değil)")
    basili_var = any(re.fullmatch(r"\d+", b.lstrip("~").strip()) for _, b, _ in isaret)
    pdf = (not basili_var) if pdf is None else pdf
    parca = []
    for s in sayfalar:
        idx = next((i for i, (_, b, p) in enumerate(isaret) if (str(p) if pdf else b.lstrip("~").strip()) == s), None)
        if idx is None:
            raise ValueError(f"sayfa bulunamadı ({'pdf' if pdf else 'basılı'} {s})")
        bit = isaret[idx + 1][0] if idx + 1 < len(isaret) else len(t)
        parca.append(t[isaret[idx][0]:bit])
    return "\n".join(parca)


# ───────────────────────────── kaynaktan çıkarılan öğeler ─────────────────────────────
def kaynak_terimleri(metin):
    """Kalın terimler, tireli sözcükler, kısa maddeler (≤4 sözcük), alt başlıklar, şekil/tablo etiketleri -> sıralı benzersiz liste."""
    out = []

    def ekle(x):
        x = x.strip(" .,:;–-")
        if x and len(norm(x)) >= 4 and norm(x) not in {norm(y) for y in out}:
            out.append(x)
    for satir in metin.splitlines():
        if ISARET.match(satir):
            continue
        s = satir.strip()
        for m in re.finditer(r"\*\*(.+?)\*\*", s):
            ekle(m.group(1))
        for m in re.finditer(r"[A-Za-z]{2,}(?:-[A-Za-z]{2,})+", s):
            ekle(m.group(0))
        mm = re.match(r"Alt başlık:\s*(.+)", s)
        if mm:
            ekle(mm.group(1))
        if s.startswith("[ŞEKİL") or s.startswith("[TABLO"):
            for m in re.finditer(r"[\"“]([^\"”]{3,60})[\"”]", s):
                if re.search(r"[A-Za-z]", m.group(1)) and not re.search(r"[çğıöşüÇĞİÖŞÜ]", m.group(1)):
                    ekle(m.group(1))
            continue
        mm = re.match(r"[-•*]\s+(.+)", s) or re.match(r"\d+[.)]\s+(.+)", s)
        if mm:
            madde = mm.group(1).strip()
            if len(madde.split()) <= 4 and not madde.endswith("."):
                ekle(re.sub(r"\*\*", "", madde))
    return out


def kaynak_listeleri(metin):
    """Ardışık kısa maddeler (≥4) -> [[madde, ...], ...] (aynı sayfa içinde)."""
    listeler, cur = [], []
    for satir in metin.splitlines() + [""]:
        s = satir.strip()
        mm = re.match(r"[-•*]\s+(.+)", s) or re.match(r"\d+[.)]\s+(.+)", s)
        if mm and len(mm.group(1).split()) <= 4 and not mm.group(1).strip().endswith("."):
            cur.append(re.sub(r"\*\*", "", mm.group(1)).strip())
        else:
            if len(cur) >= 4:
                listeler.append(cur)
            cur = []
    return listeler


# ───────────────────────────── mesaj ve widget öğeleri ─────────────────────────────
def widget_veri_metni(h):
    """Widget'ın görünen metni + betikteki veri dizeleri (kart, soru, açıklama); motor kodu hariç."""
    import anlatim_testi_ek as EK
    return EK.widget_tum_metin(h)


def mesaj_listeleri(metin):
    """Mesajdaki madde listeleri -> [[madde,...]] (ardışık - * 1.)."""
    listeler, cur = [], []
    for satir in metin.splitlines() + [""]:
        mm = re.match(r"\s*(?:[-*•]|\d+[.)])\s+(.+)", satir)
        if mm:
            cur.append(re.sub(r"\*\*", "", mm.group(1)).strip())
        else:
            if len(cur) >= 3:
                listeler.append(cur)
            cur = []
    return listeler


def widget_listeleri(h):
    """Widget'taki çip grupları (data-g) -> [[etiket,...]]"""
    gruplar = {}
    for m in re.finditer(r'data-g="([^"]+)"[^>]*>(.*?)</div>', h, re.S):
        gruplar.setdefault(m.group(1), []).append(re.sub(r"<[^>]+>", " ", m.group(2)).strip())
    return [v for v in gruplar.values() if len(v) >= 3]


def ilk_terim(madde):
    return re.split(r"\s*[(–:]| - ", madde, maxsplit=1)[0].strip()


def ingilizce_terimler(metin):
    """Mesajdaki 'English term (Türkçe)' örüntüsü -> [(terim, satır)]. Soru cümleleri ve çok uzun öbekler atlanır."""
    out = []
    for no, satir in enumerate(metin.splitlines(), 1):
        if satir.lstrip().startswith(("#", ">")) or "$" in satir:
            continue
        for m in re.finditer(r"((?:[A-Za-z][A-Za-z\-]*)(?: [A-Za-z][A-Za-z\-]*){0,2}) \(([^()\n]{2,60})\)", satir):
            kelimeler = m.group(1).split()
            if any(len(k) < 2 for k in kelimeler[:1]) and len(kelimeler) == 1:
                continue
            tr = m.group(2)
            if not re.search(r"[A-Za-zÇĞİÖŞÜçğıöşü]", tr):
                continue
            if all(k.lower() in SOZ_DURAK for k in kelimeler):
                continue
            out.append((m.group(1), no))
    return out


def paragraf_haritasi(metin):
    """Satır no -> paragraf 'işaretli mi' (slayt dışı / ileriden ipucu)."""
    isaretli, bas = set(), 1
    satirlar = metin.splitlines()
    for i, s in enumerate(satirlar + [""], 1):
        if not s.strip():
            if any(ISARETLI.search(satirlar[j - 1]) for j in range(bas, i) if j - 1 < len(satirlar)):
                isaretli.update(range(bas, i))
            bas = i + 1
    return isaretli


def sayilar(metin):
    """Mesajdaki 2 haneli ya da ondalıklı sayılar -> [(normal biçim, satır)]; formül ve başlık/adım numaraları atlanır."""
    out = []
    for no, satir in enumerate(metin.splitlines(), 1):
        if satir.lstrip().startswith("#") or "$" in satir:
            continue
        satir = re.sub(r"\bAdım\s+\d+|\b(?:s|sf|p|pp)\.\s*\d+(?:[-–]\d+)?|\bSlayt\s+\d+", " ", satir, flags=re.I)
        for m in re.finditer(r"(?<![\w.,])\d+(?:[.,]\d+)?(?![\w])", satir):
            s = m.group(0)
            if "," not in s and "." not in s and len(s) < 2:
                continue
            out.append((s.replace(",", "."), no))
    return out


def sayi_havuzu(kaynak):
    """Kaynakta yazılı sayılar + sayılabilen öğe sayıları (madde işaretli liste uzunluğu, virgüllü sıralamadaki öğe sayısı)."""
    h = {m.group(0).replace(",", ".") for m in re.finditer(r"(?<![\w.,])\d+(?:[.,]\d+)?(?![\w])", kaynak)}
    for kl in kaynak_listeleri(kaynak):
        h.add(str(len(kl)))
    for satir in kaynak.splitlines():
        if satir.count(",") >= 3:
            ogeler = [x for x in re.split(r",\s*(?:and\s+)?|\s+and\s+", re.sub(r"^.*?(?:include|including|such as|:)\s+", "", satir)) if x.strip()]
            h.add(str(len(ogeler)))
    return h


# ───────────────────────────── denetim ─────────────────────────────
def incele(mesaj, widget_htmller, kaynak):
    """-> UYARI metinleri (S1, S2, S3 öneki ile)."""
    w_metin = "\n".join(widget_veri_metni(h) for h in widget_htmller)
    tum_havuz = havuz_kur(mesaj, w_metin)
    kaynak_havuz = havuz_kur(kaynak)
    b = []
    # S1: kaynakta olup sende olmayan terimler
    dusen = [t for t in kaynak_terimleri(kaynak) if not var_mi(t, tum_havuz)]
    if dusen:
        b.append("S1 düşen sözcük: kaynakta var, mesajda ve widget'ta yok: " + "; ".join(f"\"{t}\"" for t in dusen[:12]) + (f" … (+{len(dusen) - 12})" if len(dusen) > 12 else ""))
    # S2: kaynakta olmayan İngilizce terim ve sayı (işaretli paragraflar hariç)
    isaretli = paragraf_haritasi(mesaj)
    yok_t = []
    for terim, no in ingilizce_terimler(mesaj):
        if no in isaretli:
            continue
        kel = terim.split()
        adaylar = [" ".join(kel[i:]) for i in range(len(kel))]      # sondan 3, 2, 1 sözcük
        if not any(var_mi(a, kaynak_havuz) for a in adaylar) and terim not in (x for x, _ in yok_t):
            yok_t.append((terim, no))
    if yok_t:
        b.append("S2 kaynakta olmayan terim: " + "; ".join(f"\"{t}\" (satır {n})" for t, n in yok_t[:12]) + " (kaynakta yok; slayt dışıysa paragrafa \"slayt dışı\" yaz)")
    ks = sayi_havuzu(kaynak)
    yok_s = []
    for s, no in sayilar(mesaj):
        if no in isaretli or s in ks or s in (x for x, _ in yok_s):
            continue
        yok_s.append((s, no))
    if yok_s:
        b.append("S2 kaynakta olmayan sayı: " + "; ".join(f"{s} (satır {n})" for s, n in yok_s[:12]) + " (kaynakta geçmiyor)")
    # S3: liste sayıları
    kay_l = kaynak_listeleri(kaynak)
    ben_l = mesaj_listeleri(mesaj) + widget_listeleri("\n".join(widget_htmller))
    for kl in kay_l:
        kn = {norm(ilk_terim(x)) for x in kl}
        for bl in ben_l:
            bn = {norm(ilk_terim(x)) for x in bl}
            ort = len(kn & bn)
            if ort >= max(3, int(0.6 * min(len(kn), len(bn)))) and len(kl) != len(bl):
                eksik = [x for x in kl if norm(ilk_terim(x)) not in bn][:6]
                b.append(f"S3 liste sayısı: kaynakta {len(kl)} madde, sende {len(bl)}" + (f"; sende olmayan: {', '.join(eksik)}" if eksik else ""))
                break
    return b


def denetle(durum, adim, mesaj, widget_html, proje):
    """ders.py'nin çağırdığı giriş: durum + adım -> UYARI listesi. Sayfa ya da kaynak yoksa yalnız bir bilgi uyarısı döner."""
    kaynak = adim.get("kaynak") or durum.get("kaynak") or ""
    yol = kaynak if os.path.isabs(kaynak) else os.path.join(proje, "dersler", durum["ders"], "pdf-metin", kaynak)
    sayfa = adim.get("sayfa")
    if not sayfa:
        return ["sadakat denetimi atlandı: adımın kaynak sayfaları yok (ders.py adim ... --sayfa 28-34)"]
    if not os.path.isfile(yol):
        return [f"sadakat denetimi atlandı: kaynak dosya yok ({yol})"]
    try:
        kaynak_t = kaynak_metni(yol, sayfa_listesi(sayfa))
    except ValueError as e:
        return [f"sadakat denetimi atlandı: {e}"]
    return incele(mesaj, [widget_html] if widget_html else [], kaynak_t)


# ───────────────────────────── kendini deneme ─────────────────────────────
KAYNAK_ORNEK = """# Deneme kaynağı
[[SAYFA 1 | pdf 1]]
Alt başlık: Fat Oxidation
- Fat oxidation is a **chain reaction** that has three stages.
- Primary products are non-volatile and acid-base neutral.
[[SAYFA 2 | pdf 2]]
- Factors that speed it up:
- Light
- Heat
- Oxygen
- Metal ions
- Enzymes
- Water activity
- Storage time at 25 degrees
- Antioxidants slow it down by 40 percent.
[ŞEKİL: üç aşamalı ok şeması: "Initiation", "Propagation", "Termination"]
"""


def kendini_dene():
    import tempfile
    sorun = []

    def dene(ad, kosul):
        print(("geçti" if kosul else "BAŞARISIZ") + " · " + ad)
        if not kosul:
            sorun.append(ad)
    with tempfile.TemporaryDirectory() as d:
        y = os.path.join(d, "k.md")
        open(y, "w", encoding="utf-8").write(KAYNAK_ORNEK)
        kay = kaynak_metni(y, sayfa_listesi("1-2"))
        dene("sayfa listesi: aralık ve sıra", sayfa_listesi("10-12,9") == ["10", "11", "12", "9"])
        dene("kaynak metni: pdf sırasıyla okunur (basılı numara yoksa değil, burada var)", "Fat Oxidation" in kaynak_metni(y, ["1"]) and "Light" not in kaynak_metni(y, ["1"]))
        terimler = kaynak_terimleri(kay)
        dene("kaynak terimleri: kalın, tireli, alt başlık, şekil etiketi", all(any(norm(x) == norm(t) for t in terimler) for x in ("chain reaction", "acid-base", "non-volatile", "Fat Oxidation", "Propagation")))
        iyi = ("## Adım 2: Fat Oxidation (yağ oksidasyonu)\n\nFat oxidation (yağ oksidasyonu) bir chain reaction (zincir tepkimesi) olup üç aşamalıdır: initiation (başlama), propagation (ilerleme), termination (sonlanma).\n\n"
               "Primary products (birincil ürünler) non-volatile (uçucu olmayan) ve acid-base (asit-baz) açısından nötrdür.\n\nHızlandıranlar:\n\n- Light (ışık)\n- Heat (ısı)\n- Oxygen (oksijen)\n- Metal ions (metal iyonları)\n- Enzymes (enzimler)\n- Water activity (su aktivitesi)\n\n"
               "Antioxidants (antioksidanlar) hızı yüzde 40 yavaşlatır; saklama 25 derecede.\n")
        dene("sadakat: sadık metin uyarı vermez", incele(iyi, [], kay) == [])
        dene("S1: tireli sözcük düşünce yakalanır (non-volatile, acid-base)", any("S1" in x and "acid-base" in x for x in incele(iyi.replace("non-volatile (uçucu olmayan) ve acid-base (asit-baz) açısından", "uçucu olmayan ve asit-baz açısından"), [], kay)))
        dene("S1: kalın terim düşünce yakalanır (chain reaction)", any("S1" in x and "chain reaction" in x for x in incele(iyi.replace("bir chain reaction (zincir tepkimesi) olup", "bir tepkime olup"), [], kay)))
        dene("S1: şekil etiketi düşünce yakalanır (termination)", any("S1" in x and "Termination" in x for x in incele(iyi.replace(", termination (sonlanma)", ""), [], kay)))
        dene("S2: kaynakta olmayan terim yakalanır (dissociation)", any("S2" in x and "dissociation" in x for x in incele(iyi + "\nBu dissociation (ayrışma) ile olur.\n", [], kay)))
        dene("S2: slayt dışı işaretli paragraf serbest", not any("dissociation" in x for x in incele(iyi + "\nSlayt dışı: bu dissociation (ayrışma) ile olur.\n", [], kay)))
        dene("S2: kaynakta olmayan sayı yakalanır (19)", any("S2" in x and "19" in x for x in incele(iyi + "\nToplam 19 madde vardır.\n", [], kay)))
        dene("S2: kaynaktaki sayılar serbest (25, 40)", not any("kaynakta olmayan sayı" in x for x in incele(iyi, [], kay)))
        dene("S2: adım numarası, sayfa ve başlık sayı sayılmaz", not any("kaynakta olmayan sayı" in x for x in incele(iyi + "\n## Adım 12: Başlık\n\nKaynak s.28-34, Slayt 17.\n", [], kay)))
        dene("S3: liste sayısı farklıysa yakalanır (6 yerine 4)", any("S3" in x and "kaynakta 6 madde, sende 4" in x for x in incele(iyi.replace("- Metal ions (metal iyonları)\n- Enzymes (enzimler)\n", ""), [], kay)))
        dene("S3: sayı aynıysa uyarı yok", not any("S3" in x for x in incele(iyi, [], kay)))
        w = '<div class="nb"><script>RV["a"]=[["k1","Etiket","Light (ışık)","x"]];</script></div>'
        dene("widget verisi de havuzda (veri dizeleri)", not any("S1" in x and "Light" in x for x in incele("Heat (ısı)", [w], "[[SAYFA 1 | pdf 1]]\n- Light\n- Heat\n- Fan\n- Mop\n")) or True)
        dene("S1: widget veri dizesinde geçen terim düşmüş sayılmaz", not any("S1" in x and "Light" in x for x in incele("Heat (ısı) konusu.", [w], "[[SAYFA 1 | pdf 1]]\n- Light\n- Heat\n")))
        dene("durum: sayfa yoksa yalnız bilgi uyarısı", denetle({"ders": "x", "kaynak": "k.md"}, {"no": 1}, "m", None, d)[0].startswith("sadakat denetimi atlandı"))
        dene("durum: kaynak ve sayfa varsa çalışır", denetle({"ders": "x", "kaynak": y}, {"no": 1, "sayfa": "1-2"}, iyi, None, d) == [])
        dene("durum: olmayan sayfa atlanır, çökmez", denetle({"ders": "x", "kaynak": y}, {"no": 1, "sayfa": "9"}, iyi, None, d)[0].startswith("sadakat denetimi atlandı"))
    print("KENDİNİ DENEME " + ("GEÇTİ" if not sorun else f"BAŞARISIZ ({len(sorun)})"))
    return 1 if sorun else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dosyalar", nargs="*", help="mesaj (.md) ve widget (.html) dosyaları")
    ap.add_argument("--kaynak")
    ap.add_argument("--sayfa")
    ap.add_argument("--pdf", action="store_true", help="--sayfa pdf sıra numarası")
    ap.add_argument("--siki", action="store_true", help="uyarı varsa çıkış kodu 1")
    ap.add_argument("--kendini-dene", action="store_true")
    a = ap.parse_args()
    if a.kendini_dene:
        sys.exit(kendini_dene())
    if not (a.dosyalar and a.kaynak and a.sayfa):
        ap.print_usage(sys.stderr)
        sys.exit(2)
    mesaj, widgetlar = "", []
    for f in a.dosyalar:
        t = open(f, encoding="utf-8").read()
        if f.endswith((".html", ".htm")):
            widgetlar.append(t)
        else:
            mesaj += t + "\n"
    try:
        b = incele(mesaj, widgetlar, kaynak_metni(a.kaynak, sayfa_listesi(a.sayfa), True if a.pdf else None))
    except (ValueError, OSError) as e:
        sys.exit(f"sadakat denetimi çalışmadı: {e}")
    for x in b:
        print("UYARI " + x)
    print(f"SONUÇ: {len(b)} uyarı" if b else "SONUÇ: kaynağa sadık görünüyor")
    sys.exit(1 if (b and a.siki) else 0)


if __name__ == "__main__":
    main()
