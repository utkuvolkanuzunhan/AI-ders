#!/usr/bin/env python3
"""Karma çeviri aracı: PDF / PowerPoint / Word -> sayfa numaralı Markdown (pdf-metin/<ad>.md).

Önce kod çevirir (Microsoft MarkItDown; model hiç okumaz, token harcamaz). Sonra yalnız modelin
görmesi gereken sayfaları işaretler: tablo, grafik/şekil/diyagram, görsel, metni boş ya da bozuk sayfa.
Model yalnız o sayfaların resmine bakıp `[[MODEL-OKU ...]]` satırını mantık diliyle yazılmış şekil/tablo ile değiştirir.

Kullanım (pdf-cevirici rolü; ayrıntı: gorevler/pdf-cevir.md):
  pip install 'markitdown[pdf,pptx,docx]'                                  # bir kez
  python3 araclar/pdf_cevir.py cevir <dosya> --cikti dersler/<ders>/pdf-metin/<ad>.md [--baslik "<ad>"] [--resim <klasör>]
  python3 araclar/pdf_cevir.py dogrula dersler/<ders>/pdf-metin/<ad>.md   # bitince zorunlu; yarım ya da hatalıysa çıkış kodu 1
  python3 araclar/pdf_cevir.py indeks dersler/<ders>/pdf-metin/<ad>.md    # indeks.md için sayfa başına başlık taslağı
  python3 araclar/pdf_cevir.py --kendini-dene                              # araç mantığını dener (dosya ve MarkItDown gerekmez)

Sayfa işaretleri araclar/kaynak.py'nin okuduğu `[[SAYFA <basılı> | pdf <sıra>]]` biçimindedir. Basılı numara sayfanın
kenarındaki (alt/üst) tek başına sayıdan bulunur, ardışıklığı ve sabit farkı kodla doğrulanır; bulunamayan `~n`
(komşulardan çıkarıldı) ya da `?` olur. PowerPoint'te slayt sırası, Word'de bölüm sırası numaradır.
Fotoğraf slaytlar (metin katmanı yok) tamamen "metin yok" sayılır: OCR yoktur, bu sayfaları model okur.
"""
import argparse, io, os, re, shutil, subprocess, sys, tempfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaynak import ISARET  # noqa: E402

# --- eşikler (sayfayı modele göstermenin ölçüsü) ---
MIN_METIN = 20          # bundan az karakter: metin yok (PDF)
MIN_GORSEL_KENAR = 40   # pt; bundan küçük görsel (logo, simge) sayılmaz
MIN_GORSEL_ORAN = 0.03  # sayfanın bu kadarını kaplayan görsel
MIN_EGRI = 8            # bu kadar eğri: grafik
MIN_CIZIM = 12          # çizgi + dikdörtgen (zemin hariç): şekil/diyagram
MIN_DAGINIK = 6         # tek harflik satır (dikey eksen yazısı) sayısı
ALT_BANT = 0.85        # sayfa numarası araması: alt %15
UST_BANT = 0.10        # üst %10
MODEL_ISARETI = "[[MODEL-OKU"

ROMA = re.compile(r"(?=[ivxlcdm]{1,6}$)m{0,3}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})")


def hata(mesaj, kod=2):
    sys.stderr.write(mesaj.strip() + "\n")
    sys.exit(kod)


# ============ saf mantık (dosya gerekmez; --kendini-dene bunları dener) ============

def temizle(t):
    """MarkItDown çıktısını sade bırakır: satır sonu boşlukları, form feed, 3+ boş satır. İçerik değişmez."""
    t = (t or "").replace("\x0c", "\n").replace("\r\n", "\n").replace("\r", "\n")
    t = "\n".join(s.rstrip() for s in t.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def md_tablo_sayisi(t):
    return len(re.findall(r"^\|[ \-:|]+\|\s*$", t, re.M))


def bos_baslik_var(t):
    """Markdown tablonun başlık satırında boş hücre var mı (bozuk ayrıştırma işareti)."""
    s = t.split("\n")
    for i, satir in enumerate(s[1:], 1):
        if re.match(r"^\|[ \-:|]+\|\s*$", satir) and re.search(r"\|\s*\|", s[i - 1]):
            return True
    return False


def isaretle(oz, metin, min_metin=MIN_METIN):
    """Sayfa özelliklerinden 'model görmeli' nedenlerini çıkarır. Boş liste: kodla bitti.
    oz: gorsel_oran, egri, cizgi, dikdortgen, tablo (algılanan tablo sayısı), gorsel_var (pptx/docx için).
    min_metin: PDF'te 20; slayt/Word'de başlık tek başına geçerli olduğundan 3 (yalnız tam boşları yakalar)."""
    n = []
    govde = (metin or "").strip()
    satirlar = [s.strip() for s in govde.split("\n")]
    if len(govde) < min_metin:
        n.append("metin yok ya da çok az (fotoğraf/taranmış sayfa olabilir)")
    if oz.get("gorsel_oran", 0) >= MIN_GORSEL_ORAN or oz.get("gorsel_var"):
        oran = oz.get("gorsel_oran", 0)
        n.append("görsel" + (f" (sayfanın %{round(100 * oran)}'si)" if oran else ""))
    daginik = sum(1 for s in satirlar if len(s) == 1)
    cizim = oz.get("cizgi", 0) + max(oz.get("dikdortgen", 0) - 1, 0)
    if oz.get("egri", 0) >= MIN_EGRI or daginik >= MIN_DAGINIK:
        n.append("grafik/şekil (eğriler ya da dağınık eksen yazısı)")
    elif oz.get("tablo", 0):
        temiz = md_tablo_sayisi(govde) == oz["tablo"] and not bos_baslik_var(govde)
        n.append("tablo (temiz görünüyor, yine de resimden doğrula)" if temiz else "tablo (bozuk çıkmış olabilir)")
    elif cizim >= MIN_CIZIM:
        n.append("şekil/diyagram (çok çizim öğesi)")
    if "(cid:" in govde or re.search("[\ue000-\uf8ff\ufffd]", govde):
        n.append("bozuk yazı ya da formül karakteri")
    return n


def numara_adaylari(kelimeler, yuk):
    """Sayfa kenarındaki (alt %15, üst %10) tek başına sayı ya da küçük roma rakamları. En kenara yakın önce.
    kelimeler: [{text, top, bottom}] (pdfplumber extract_words biçimi)."""
    alt, ust = [], []
    for k in kelimeler:
        t = k["text"].strip().strip("-–—•|·").strip()
        m = re.fullmatch(r"(\d{1,4})(?:\s*/\s*\d{1,4})?", t)
        aday = m.group(1) if m else (t if ROMA.fullmatch(t) else None)
        if not aday:
            continue
        if k["top"] >= ALT_BANT * yuk:
            alt.append((k["bottom"], aday))
        elif k["bottom"] <= UST_BANT * yuk:
            ust.append((-k["top"], aday))
    alt.sort(reverse=True)
    ust.sort(reverse=True)
    return list(dict.fromkeys([a for _, a in alt] + [a for _, a in ust]))


def numaralari_coz(adaylar):
    """Sayfa başına aday listesinden basılı numaraları çıkarır ve doğrular.
    -> (liste[(basılı, durum, not)], mod). durum: tam | cikarildi | bilinmiyor | sira. mod: basili | sira.
    Sabit fark k (basılı = pdf − k) en çok oyu alan değerdir; fark ortada değişirse sonraki sayfa da destekliyorsa kabul edilir."""
    n = len(adaylar)
    K = [{i - int(a) for a in ad if a.isdigit()} for i, ad in enumerate(adaylar, 1)]
    oy = Counter(k for ks in K for k in ks)
    cur = max(oy, key=lambda k: (oy[k], -abs(k))) if oy else None
    if cur is None or oy[cur] < max(2, 0.3 * n):
        return [(str(i), "sira", None) for i in range(1, n + 1)], "sira"
    sonuc = []
    for i in range(n):
        ks, ad, sira = K[i], adaylar[i], i + 1
        if cur in ks:
            sonuc.append((str(sira - cur), "tam", None))
            continue
        yeni = [k for k in sorted(ks) if (i + 1 < n and k in K[i + 1]) or (i + 2 < n and k in K[i + 2])]
        if yeni:
            cur = yeni[0]
            sonuc.append((str(sira - cur), "tam", f"numara farkı değişti: basılı = pdf − {cur}"))
            continue
        roma = [a for a in ad if not a.isdigit()]
        if not ks and roma:
            sonuc.append((roma[0], "tam", None))
            continue
        if ks:
            sonuc.append(("?", "bilinmiyor",
                          f"kenardaki sayı {'/'.join(sorted(a for a in ad if a.isdigit()))} beklenen {sira - cur} ile uyuşmuyor"))
            continue
        tahmin = sira - cur
        sonuc.append((f"~{tahmin}", "cikarildi", None) if tahmin >= 1 else ("?", "bilinmiyor", None))
    return sonuc, "basili"


def sayfa_araligi(liste):
    """[1,2,3,7,9,10] -> '1–3, 7, 9–10'"""
    cikti, i = [], 0
    while i < len(liste):
        j = i
        while j + 1 < len(liste) and liste[j + 1] == liste[j] + 1:
            j += 1
        cikti.append(str(liste[i]) if i == j else f"{liste[i]}–{liste[j]}")
        i = j + 1
    return ", ".join(cikti)


def _fark_yaz(k):
    return "basılı = pdf sırası" if k == 0 else (f"basılı = pdf − {k}" if k > 0 else f"basılı = pdf + {-k}")


def esleme_satiri(sonuc, mod, tur="sayfa"):
    """Dosya başındaki 'sayfa eşlemesi' satırı."""
    if tur != "sayfa":
        return f"numara: {tur} sırası (basılı sayfa numarası yok; {tur} sırası kaynak numarasıdır)"
    if mod == "sira":
        return "numara: sıra (kaynakta basılı sayfa numarası bulunamadı; kaynak olarak pdf sırası kullanılır)"
    parca, onceki, bas = [], None, None
    for i, (b, _, _) in enumerate(sonuc, 1):
        s = b.lstrip("~")
        k = i - int(s) if s.isdigit() else None
        if k is None:
            continue
        if k != onceki:
            if onceki is not None:
                parca.append(f"{_fark_yaz(onceki)} (s.{bas}–{son})")
            onceki, bas = k, s
        son = s
    if onceki is not None:
        parca.append(f"{_fark_yaz(onceki)} (s.{bas}–{son})")
    soru = sum(1 for b, _, _ in sonuc if b == "?")
    return "sayfa eşlemesi: " + "; ".join(parca) + (f" · KONTROL: {soru} sayfada numara belirsiz (?)" if soru else ", araç doğruladı")


def numara_satirini_sil(metin, aday):
    """Sayfa metninin son ya da ilk satırı yalnız sayfa numarasıysa siler (numara işarette durur; ortadaki sayıya dokunmaz)."""
    s = metin.split("\n")
    kalip = re.compile(rf"^\s*[-–—]?\s*(?:(?:page|sayfa|s\.)\s*)?{re.escape(aday)}(?:\s*/\s*\d+)?\s*[-–—]?\s*$", re.I)
    dolu = [i for i, x in enumerate(s) if x.strip()]
    for i in dict.fromkeys(dolu[-1:] + dolu[:1]):
        if kalip.match(s[i]):
            del s[i]
            break
    return "\n".join(s).strip()


def isaret_satiri(basili, sira, not_=None):
    return f"[[SAYFA {basili} | pdf {sira}" + (f" | not: {not_}" if not_ else "") + "]]"


def md_yaz(baslik, sayfalar, esleme, arac):
    """Sayfa listesinden dosya metnini kurar. sayfa: {sira, basili, not_, metin, nedenler}."""
    model = [str(s["sira"]) for s in sayfalar if s["nedenler"]]
    ust = [f"# {baslik} ({len(sayfalar)} sayfa)", esleme,
           f"çeviri: {arac}; model okuması yalnız şekil, grafik, tablo ve metinsiz sayfalarda (pdf {', '.join(model) or 'yok'})", ""]
    govde = []
    for s in sayfalar:
        parca = [isaret_satiri(s["basili"], s["sira"], s["not_"])]
        if s["nedenler"]:
            parca.append(f"{MODEL_ISARETI} | neden: {'; '.join(s['nedenler'])}]]")
        if s["metin"]:
            parca.append(s["metin"])
        govde.append("\n".join(parca))
    return "\n".join(ust) + "\n\n".join(govde) + "\n"


def dogrula_metin(t):
    """Çevrilmiş dosyayı denetler. -> (hatalar, uyarilar, ozet)."""
    hatalar, uyarilar = [], []
    isaretler = [(m.start(), m.group(1).strip(), int(m.group(2))) for m in ISARET.finditer(t)]
    if not isaretler:
        return ["dosyada [[SAYFA <basılı> | pdf <sıra>]] işareti yok"], [], ""
    bekleyen = [m.start() for m in re.finditer(re.escape(MODEL_ISARETI), t)]
    if bekleyen:
        sayfalar = []
        for pos in bekleyen:
            onceki = [x for x in isaretler if x[0] < pos]
            sayfalar.append(str(onceki[-1][2]) if onceki else "?")
        hatalar.append(f"model okuması bekleyen sayfa var (pdf {', '.join(sayfalar)}): resme bakıp [[MODEL-OKU ...]] satırını sil, şekil/tablo ekle")
    if re.search(r"^YARIM:", t, re.M):
        hatalar.append("dosya YARIM işaretli")
    sira = [p for _, _, p in isaretler]
    if sira != list(range(1, len(sira) + 1)):
        hatalar.append(f"pdf sırası 1..{len(sira)} ardışık değil: {sira[:12]}...")
    ks = []
    for _, b, p in isaretler:
        s = b.lstrip("~")
        if b == "?":
            uyarilar.append(f"pdf {p}: basılı numara belirsiz (?)")
        elif s.isdigit():
            ks.append(p - int(s))
    # fark değişimi not: ile açıklanmış mı
    onceki = None
    for m in ISARET.finditer(t):
        b, p = m.group(1).strip().lstrip("~"), int(m.group(2))
        if not b.isdigit():
            continue
        k = p - int(b)
        if onceki is not None and k != onceki and "not:" not in m.group(0):
            uyarilar.append(f"pdf {p}: numara farkı {onceki} → {k} değişti, işarete 'not:' ile nedenini yaz")
        onceki = k
    bos = []
    for i, (pos, _, p) in enumerate(isaretler):
        son = isaretler[i + 1][0] if i + 1 < len(isaretler) else len(t)
        govde = t[pos:son].split("\n", 1)[1] if "\n" in t[pos:son] else ""
        if len(govde.strip()) < 20:
            bos.append(str(p))
    if bos:
        uyarilar.append(f"gövdesi boş ya da çok kısa sayfa (pdf {', '.join(bos)}): gerçekten boş mu, metin/şekil eksik mi bak")
    if "(cid:" in t or re.search("[\ue000-\uf8ff\ufffd]", t):
        uyarilar.append("bozuk yazı karakteri kalmış ((cid:..), özel alan ya da \ufffd)")
    ozet = f"{len(isaretler)} sayfa" + (f", fark k={Counter(ks).most_common(1)[0][0]}" if ks else "")
    return hatalar, uyarilar, ozet


def indeks_taslagi(t):
    """Her sayfanın ilk anlamlı satırı (slaytta başlık). Model bunları konu aralıklarına toplar."""
    satirlar = []
    isaretler = list(ISARET.finditer(t))
    for i, m in enumerate(isaretler):
        son = isaretler[i + 1].start() if i + 1 < len(isaretler) else len(t)
        ilk = ""
        for s in t[m.end():son].split("\n"):
            s = s.strip()
            if s and not s.startswith(MODEL_ISARETI):
                ilk = re.sub(r"^#+\s*", "", s)[:80]
                break
        satirlar.append(f"- s.{m.group(1).strip() or '?'} (pdf {m.group(2)}): {ilk}")
    return "\n".join(satirlar)


# ============ dosya okuma (MarkItDown, pdfplumber, pypdfium2, python-pptx) ============

def markitdown_al():
    try:
        import markitdown
        return markitdown.MarkItDown(), getattr(markitdown, "__version__", "")
    except ImportError:
        hata("MarkItDown kurulu değil. Bir kez çalıştır:\n  pip install 'markitdown[pdf,pptx,docx]'\nKurulamıyorsa gorevler/pdf-cevir.md'deki 'MarkItDown olmadan' yolunu uygula.")


def pdf_ozellik(pg):
    """pdfplumber sayfasından sayfa özellikleri ve numara adayları."""
    w, h = float(pg.width), float(pg.height)
    gorsel = 0.0
    for im in pg.images:
        gw, gh = im["x1"] - im["x0"], im["bottom"] - im["top"]
        if gw >= MIN_GORSEL_KENAR and gh >= MIN_GORSEL_KENAR:
            gorsel += gw * gh
    egri, cizgi, dik = len(pg.curves), len(pg.lines), len(pg.rects)
    tablo = 0
    if cizgi + dik >= 6:
        try:
            for tb in pg.find_tables():
                if len(tb.rows) >= 2 and max(len(r.cells) for r in tb.rows) >= 2:
                    tablo += 1
        except Exception:
            pass
    kelimeler = pg.extract_words(x_tolerance=2, y_tolerance=2)
    oz = {"gorsel_oran": min(gorsel / (w * h), 1.0), "egri": egri, "cizgi": cizgi, "dikdortgen": dik, "tablo": tablo}
    return oz, numara_adaylari(kelimeler, h)


def pdf_sayfalari(yol, md):
    import pdfplumber
    import pypdfium2 as pdfium
    kaynak = pdfium.PdfDocument(yol)
    plum = pdfplumber.open(yol)
    sayfalar, adaylar = [], []
    n = len(kaynak)
    for i in range(n):
        yeni = pdfium.PdfDocument.new()
        yeni.import_pages(kaynak, [i])
        b = io.BytesIO()
        yeni.save(b)
        b.seek(0)
        ek = []
        try:
            metin = temizle(md.convert_stream(b, file_extension=".pdf").text_content)
        except Exception as e:  # tek sayfa hatası tüm çeviriyi durdurmasın
            metin, ek = "", [f"MarkItDown bu sayfada hata verdi ({type(e).__name__})"]
        pg = plum.pages[i]
        oz, ad = pdf_ozellik(pg)
        try:
            pg.flush_cache()
        except Exception:
            pass
        sayfalar.append({"sira": i + 1, "metin": metin, "nedenler": isaretle(oz, metin) + ek})
        adaylar.append(ad)
        if (i + 1) % 25 == 0:
            sys.stderr.write(f"  {i + 1}/{n} sayfa\n")
    sonuc, mod = numaralari_coz(adaylar)
    for s, (b, d, not_), ad in zip(sayfalar, sonuc, adaylar):
        s["basili"], s["not_"] = b, not_
        if d == "tam" and b in ad:
            s["metin"] = numara_satirini_sil(s["metin"], b)
        elif d == "bilinmiyor":
            s["nedenler"].append("basılı numara belirsiz: resimden bak (yoksa ? kalsın)")
    return sayfalar, esleme_satiri(sonuc, mod)


def pptx_ozellikleri(yol):
    """Slayt başına şekil sayıları (python-pptx)."""
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE as T
    sonuc = []
    for slayt in Presentation(yol).slides:
        c = Counter()

        def gez(sekiller):
            for s in sekiller:
                tip = getattr(s, "shape_type", None)
                if tip == T.GROUP:
                    c["grup"] += 1
                    gez(s.shapes)
                elif tip == T.PICTURE:
                    c["resim"] += 1
                elif getattr(s, "has_chart", False) and s.has_chart:
                    c["grafik"] += 1
                elif getattr(s, "has_table", False) and s.has_table:
                    c["tablo"] += 1
                elif tip in (T.FREEFORM, T.AUTO_SHAPE, T.LINE):
                    c["sekil"] += 1
        gez(slayt.shapes)
        sonuc.append(c)
    return sonuc


def pptx_sayfalari(yol, md):
    r = md.convert(yol).text_content
    parcalar = re.split(r"<!--\s*Slide number:\s*(\d+)\s*-->", r)
    metinler = {int(parcalar[i]): temizle(parcalar[i + 1]) for i in range(1, len(parcalar) - 1, 2)}
    oz = pptx_ozellikleri(yol)
    sayfalar = []
    for i in range(1, len(oz) + 1):
        c, metin = oz[i - 1], metinler.get(i, "")
        ozel = {"gorsel_var": c["resim"] > 0, "egri": 0, "cizgi": 0, "dikdortgen": 0,
                "tablo": c["tablo"]}
        # pptx tablosu nesne modelinden gelir (hücre yapısı kesin); yalnız bozuksa göster
        nedenler = [x for x in isaretle(ozel, metin, 3) if not x.startswith("tablo (temiz")]
        if c["grafik"]:
            nedenler.append("grafik (veri metne çıktı, görünüşü resimden doğrula)")
        if c["grup"] + c["sekil"] >= 8:
            nedenler.append("diyagram/şekil (çok sayıda çizim öğesi)")
        sayfalar.append({"sira": i, "basili": str(i), "not_": None, "metin": metin, "nedenler": nedenler})
    return sayfalar, esleme_satiri([], "sira", "slayt")


def docx_sayfalari(yol, md):
    """Word'de sayfa yoktur: başlıklara göre (yoksa ~2500 karakterlik parçalara) bölümlere bölünür."""
    t = temizle(md.convert(yol).text_content)
    bolumler = re.split(r"\n(?=#{1,2} )", t) if re.search(r"^#{1,2} ", t, re.M) else []
    if len(bolumler) < 2:
        bolumler, simdi = [], ""
        for p in t.split("\n\n"):
            if simdi and len(simdi) + len(p) > 2500:
                bolumler.append(simdi)
                simdi = ""
            simdi += ("\n\n" if simdi else "") + p
        if simdi:
            bolumler.append(simdi)
    sayfalar = []
    for i, b in enumerate(bolumler, 1):
        oz = {"gorsel_var": "![" in b, "egri": 0, "cizgi": 0, "dikdortgen": 0, "tablo": md_tablo_sayisi(b)}
        n = isaretle(oz, b, 3)
        # Word tablosu da nesne modelinden gelir (hücre yapısı kesin); yalnız bozuksa göster
        n = [x for x in n if not x.startswith("tablo (temiz")]
        sayfalar.append({"sira": i, "basili": str(i), "not_": None, "metin": b, "nedenler": n})
    return sayfalar, esleme_satiri([], "sira", "bölüm")


def resim_uret(yol, sayfalar, klasor):
    """Model görmeli sayfaların PNG'sini üretir. -> {sira: dosya}. PowerPoint soffice ile PDF'e çevrilir; Word'de resim yok."""
    secili = [s["sira"] for s in sayfalar if s["nedenler"]]
    if not secili:
        return {}
    pdf = yol
    if yol.lower().endswith((".pptx", ".ppt")):
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if not soffice:
            sys.stderr.write("  uyarı: soffice yok, slayt resmi üretilemedi (slaytları PDF'e çevirip PDF yolunu kullan)\n")
            return {}
        gecici = tempfile.mkdtemp(prefix="pdf-cevir-")
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", gecici, yol],
                       check=False, capture_output=True, timeout=300)
        pdf = os.path.join(gecici, os.path.splitext(os.path.basename(yol))[0] + ".pdf")
        if not os.path.exists(pdf):
            sys.stderr.write("  uyarı: slayt PDF'e çevrilemedi, resim yok\n")
            return {}
    elif not yol.lower().endswith(".pdf"):
        return {}
    import pypdfium2 as pdfium
    os.makedirs(klasor, exist_ok=True)
    belge = pdfium.PdfDocument(pdf)
    cikti = {}
    for sira in secili:
        if sira - 1 >= len(belge):
            continue
        dosya = os.path.join(klasor, f"s{sira:03d}.png")
        belge[sira - 1].render(scale=1.4).to_pil().save(dosya)
        cikti[sira] = dosya
    return cikti


# ============ komutlar ============

def komut_cevir(a):
    yol = a.dosya
    if not os.path.exists(yol):
        hata(f"Dosya yok: {yol}")
    md, surum = markitdown_al()
    uzanti = os.path.splitext(yol)[1].lower()
    if uzanti == ".pdf":
        sayfalar, esleme = pdf_sayfalari(yol, md)
    elif uzanti == ".pptx":
        sayfalar, esleme = pptx_sayfalari(yol, md)
    elif uzanti == ".docx":
        sayfalar, esleme = docx_sayfalari(yol, md)
    else:
        hata(f"Desteklenmeyen biçim: {uzanti} (pdf, pptx, docx). Eski biçimleri (ppt, doc) önce PDF'e çevir.")
    baslik = a.baslik or os.path.splitext(os.path.basename(yol))[0]
    os.makedirs(os.path.dirname(os.path.abspath(a.cikti)), exist_ok=True)
    with open(a.cikti, "w", encoding="utf-8") as f:
        f.write(md_yaz(baslik, sayfalar, esleme, f"MarkItDown {surum}".strip() + " (kod)"))
    klasor = a.resim or os.path.join(tempfile.gettempdir(), "pdf-cevir-" + re.sub(r"[^\w.-]+", "_", baslik))
    resimler = resim_uret(yol, sayfalar, klasor)
    model = [s for s in sayfalar if s["nedenler"]]
    n = len(sayfalar)
    print(f"{os.path.basename(yol)}: {n} sayfa kodla çevrildi → {a.cikti}")
    print(esleme)
    print(f"Model okuyacak: {len(model)}/{n} sayfa (model okuması ~%{round(100 * (n - len(model)) / n)} az)")
    if len(model) <= 12:
        for s in model:
            print(f"  pdf {s['sira']}: {'; '.join(s['nedenler'])}" + (f" → {resimler[s['sira']]}" if s["sira"] in resimler else ""))
    else:  # çok sayfa: nedene göre grupla
        gruplar = {}
        for s in model:
            gruplar.setdefault("; ".join(x.split(" (")[0] for x in s["nedenler"]), []).append(s["sira"])
        for neden, sirasi in gruplar.items():
            print(f"  {neden}: pdf {sayfa_araligi(sirasi)} ({len(sirasi)} sayfa)")
        if resimler:
            print(f"  resimler: {os.path.dirname(next(iter(resimler.values())))}/s<pdf>.png")
        if len(model) > 0.8 * n:
            print("  Not: sayfaların çoğu fotoğraf/taranmış; kod burada tasarruf sağlamaz, model okur.")
    if model:
        print("\nSıradaki: işaretli her sayfanın resmine bak (Read), dosyadaki [[MODEL-OKU ...]] satırını sil ve yerine "
              "[ŞEKİL ...] / [TABLO ...] yaz, yanlış çıkan yazıyı düzelt. Bitince: pdf_cevir.py dogrula " + a.cikti)
        if not resimler and uzanti == ".docx":
            print("Not: Word'de sayfa resmi yok. Görselli bölümler için dosyayı önce PDF'e çevir "
                  "(soffice --headless --convert-to pdf <dosya>) ve PDF olarak çevir.")
        elif not resimler:
            print("Not: resim üretilemedi; kaynağı PDF'e çevirip sayfa resimlerini kendin üret (pypdfium2 render).")
    else:
        print("\nModel okuması gerekmedi. Sıradaki: pdf_cevir.py dogrula " + a.cikti)


def komut_dogrula(a):
    t = open(a.md, encoding="utf-8").read()
    hatalar, uyarilar, ozet = dogrula_metin(t)
    for u in uyarilar:
        print("UYARI:", u)
    for h in hatalar:
        print("HATA:", h)
    if hatalar:
        sys.exit(1)
    print(f"TAMAM: {ozet}" + (" (uyarıları gözden geçir)" if uyarilar else ""))


def komut_indeks(a):
    print(indeks_taslagi(open(a.md, encoding="utf-8").read()))


def kendini_dene():
    """Saf mantığı sentetik veriyle dener. Başarısız olursa çıkış kodu 1."""
    hatali = []

    def kontrol(ad, kosul):
        if not kosul:
            hatali.append(ad)
    # numara adayları: slayt sağ altı, üst başlıkta sayı, ortada sayı
    kel = [{"text": "5", "top": 505, "bottom": 518}, {"text": "42", "top": 200, "bottom": 215},
           {"text": "Page", "top": 510, "bottom": 520}]
    kontrol("numara adayı yalnız kenardan", numara_adaylari(kel, 540) == ["5"])
    kontrol("12/38 biçimi", numara_adaylari([{"text": "12/38", "top": 520, "bottom": 530}], 540) == ["12"])
    kontrol("roma rakamı", numara_adaylari([{"text": "xii", "top": 520, "bottom": 530}], 540) == ["xii"])
    kontrol("büyük harf roma sayılmaz", numara_adaylari([{"text": "I", "top": 520, "bottom": 530}], 540) == [])
    # sabit fark, eksik sayfa, ayrışan sayfa
    # kapak numarasız, 5. sayfada numara yok, 7. sayfada yıl gibi alakasız sayı; fark k=−1 (basılı = pdf + 1)
    s, mod = numaralari_coz([[], ["2"], ["3"], ["4"], [], ["6"], ["2024"], ["8"]])
    kontrol("mod basili", mod == "basili")
    kontrol("kapak ~1 olarak çıkarılır", s[0] == ("~1", "cikarildi", None))
    kontrol("eksik sayfa komşudan", s[4] == ("~5", "cikarildi", None))
    kontrol("uyuşmayan sayı ?", s[6][0] == "?" and s[6][1] == "bilinmiyor")
    kontrol("tam sayfa", s[1] == ("2", "tam", None))
    # numara hiç yok -> sıra
    s2, mod2 = numaralari_coz([[], [], []])
    kontrol("numarasız dosya sıra", mod2 == "sira" and s2[2][0] == "3")
    # fark değişimi (ek sayfa): 1,2,3,[ek sayfa numarasız],4 -> pdf5 basılı 4 (k=1), önceki k=0
    s3, _ = numaralari_coz([["1"], ["2"], ["3"], [], ["4"], ["5"], ["6"]])
    kontrol("fark değişimi not alır", s3[4][2] and "değişti" in s3[4][2] and s3[4][0] == "4")
    # işaret satırı kaynak.py ile okunur
    isr = isaret_satiri("~23", 27, "ek sayfa")
    m = ISARET.match(isr)
    kontrol("işaret kaynak.py ile okunur", bool(m) and m.group(1) == "~23" and m.group(2) == "27")
    # numara satırını silme
    kontrol("numara satırı silinir", numara_satirini_sil("Başlık\nmetin\n11", "11") == "Başlık\nmetin")
    kontrol("ortadaki sayı silinmez", numara_satirini_sil("Q\n11\ncevap 4\nbitti", "11") == "Q\n11\ncevap 4\nbitti")
    # işaretleme kuralları
    kontrol("düz sayfa temiz", isaretle({"egri": 0, "cizgi": 0, "dikdortgen": 1, "tablo": 0, "gorsel_oran": 0}, "Başlık\n" + "metin " * 20) == [])
    kontrol("boş sayfa işaretlenir", any("metin yok" in x for x in isaretle({}, "")))
    kontrol("slayt başlığı tek başına geçer", isaretle({}, "# Başlık", 3) == [])
    kontrol("grafik işaretlenir", any("grafik" in x for x in isaretle({"egri": 20}, "x " * 40)))
    kontrol("görsel işaretlenir", any("görsel" in x for x in isaretle({"gorsel_oran": 0.5}, "x " * 40)))
    kontrol("dikey eksen yazısı", any("grafik" in x for x in isaretle({}, "uzun metin " * 5 + "\n" + "\n".join("abcdefg"))))
    tablo = "Başlık metni burada\n| A | B |\n| - | - |\n| 1 | 2 |"
    kontrol("temiz tablo", any("temiz" in x for x in isaretle({"tablo": 1}, tablo)))
    kontrol("bozuk tablo", any("bozuk" in x for x in isaretle({"tablo": 1}, tablo + "\n| X | Y |\n| - | - |\n| 3 | 4 |")))
    kontrol("bozuk yazı", any("bozuk yazı" in x for x in isaretle({}, "metin (cid:12) " * 5)))
    # dosya yaz + doğrula + indeks
    sayfalar = [{"sira": 1, "basili": "~1", "not_": None, "metin": "Kapak başlığı ve bir iki cümle daha", "nedenler": []},
                {"sira": 2, "basili": "2", "not_": None, "metin": "Konu bir\n" + "metin " * 10, "nedenler": ["tablo (temiz)"]}]
    dosya = md_yaz("deneme", sayfalar, esleme_satiri([("~1", "cikarildi", None), ("2", "tam", None)], "basili"), "deneme")
    h, u, _ = dogrula_metin(dosya)
    kontrol("bekleyen model okuması hata verir", any("model okuması bekleyen" in x for x in h))
    kontrol("kaynak.py bekleyeni görür", MODEL_ISARETI in dosya)
    tamam = re.sub(r"^\[\[MODEL-OKU.*\n", "", dosya, flags=re.M)
    h2, u2, _ = dogrula_metin(tamam)
    kontrol("tamamlanmış dosya geçer", not h2)
    kontrol("indeks taslağı", "s.2 (pdf 2): Konu bir" in indeks_taslagi(tamam))
    kontrol("sayfa aralığı", sayfa_araligi([1, 2, 3, 7, 9, 10]) == "1–3, 7, 9–10")
    kontrol("başlık satırı", esleme_satiri([("1", "tam", None), ("2", "tam", None)], "basili").startswith("sayfa eşlemesi: basılı = pdf sırası (s.1–2)"))
    if hatali:
        print("BAŞARISIZ:", "; ".join(hatali))
        sys.exit(1)
    print("pdf_cevir.py: kendini deneme geçti")


def main():
    if "--kendini-dene" in sys.argv[1:]:
        return kendini_dene()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    alt = ap.add_subparsers(dest="komut", required=True)
    c = alt.add_parser("cevir", help="dosyayı kodla çevir, model görmeli sayfaları işaretle")
    c.add_argument("dosya")
    c.add_argument("--cikti", required=True, help="dersler/<ders>/pdf-metin/<ad>.md")
    c.add_argument("--baslik", default="", help="dosya başlığı (varsayılan: dosya adı)")
    c.add_argument("--resim", default="", help="işaretli sayfaların resim klasörü (varsayılan: geçici klasör)")
    c.set_defaults(f=komut_cevir)
    d = alt.add_parser("dogrula", help="çevrilmiş dosyayı denetle (yarımsa çıkış kodu 1)")
    d.add_argument("md")
    d.set_defaults(f=komut_dogrula)
    i = alt.add_parser("indeks", help="indeks.md için sayfa başına başlık taslağı")
    i.add_argument("md")
    i.set_defaults(f=komut_indeks)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
