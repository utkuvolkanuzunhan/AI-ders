#!/usr/bin/env python3
"""Anlatım mesajı testi: her anlatım mesajı göndermeden önce bu testten geçer.

  python3 araclar/anlatim_testi.py mesaj.md [mesaj2.md | dizin ...]   ayrıntılı rapor
  ... --rapor              sohbete yazılacak en çok 2 satırlık özet
  ... --ilk                konunun ilk mesajı (## Kısa Cevap + hedef cümlesi aranır)
  ... --idari              idari mesaj (en çok 2 satır)
  ... --emoji 🙉 --emoji-adet 3-4   toplam emoji adedi (kişisel ayar; yerel/ayarlar.md'den gelir)
  ... --izin a/b,c/d       düz kesir sayılmayacak ek yazımlar
  ... --cift-aralik 20-70  tüm mesajlarda çift boşluk payı için hata sınırı (yüzde; en az 10 geçiş varsa)
  ... --profil yerel/denetim.json   kişisel ayarlar (emoji, terim dili, mini test sayısı...); verilmezse AI_DERS_PROFIL, ./yerel/denetim.json,
                           /mnt/project-files/yerel/denetim.json sırasıyla aranır; komut satırı profili geçer
  ... --terim C2 --ders <ders> [--sozluk dosya]   terim dili denetimi (C2: İngilizce (Türkçe); C1/C3: Türkçe (İngilizce)); sözlük dersten ya da dosyadan
  ... --emoji-seri 3-4     emoji yalnız bu uzunlukta seri yazılır (tek/çift 🙉 yok); widget içinde yasak (profil: widget_emoji_yasak)
  ... --test-turu mini|tam --konu "<adım adı>"   .html (W10/W24) ve .json soru dosyası: dil, konu ipucu, cevap dağılımı, mini test sayısı
  python3 araclar/anlatim_testi.py --kendini-dene                     kuralların kendi denemesi

Her .md/.txt dosyası sohbete gönderilecek mesajın metnidir; widget (.html) ve soru verisi (.json) de verilebilir (ek kurallar:
anlatim_testi_ek.py). Çıkış kodu: 0 hata yok, 1 hata var, 2 kullanım hatası.
Kurallar tek yerde durur, burada kopyalanmaz: cekirdek/temel.md §3–§4 ve claude-sorunlari/formuller.md. Bulgu kodları:
  F = formül (F01–F14), B = boşluk (B01–B13), S = metin biçimi (S01–S12); kod, kuralın hangi maddesine bağlı olduğunu söyler.
  T = terim dili, E = emoji serisi, W = widget, Q = test soruları (ek kurallar: anlatim_testi_ek.py).
Boşluk: tek boşluk = boş satır; çift boşluk = boş satır, yalnız ⠀ (U+2800) satırı, boş satır.
Metne `[widget]` satırı koyarsan o yer widget sınırı sayılır (önü ve sonu çift boşluk); mesajı gönderirken o satırı sil.
"""
import argparse, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anlatim_testi_ek as EK  # noqa: E402  (terim dili, emoji serisi, test soruları, widget)

BR = "\u2800"
H, U = "HATA", "UYARI"

# ---- birim ve izin listeleri -------------------------------------------------
BIRIM = set("J kJ MJ GJ cal kcal mol mmol g kg mg ng µg μg L mL µL μL m cm mm km dm s min h sa dk sn K W kW MW GW N Pa kPa MPa "
            "bar atm rad Hz V mV A mA C ppm Wh kWh ay yıl gün adet TL".split())
IZINLI_KESIR = {"ve/veya", "ya/da", "ve/ya", "and/or", "w/v", "v/v", "w/w", "I/O", "A/B", "TCP/IP", "24/7", "m/z", "O/W", "W/O",
                "evet/hayır", "doğru/yanlış"}
YASAK_KOMUT = r"Large|LARGE|large|Huge|huge|boldsymbol|mathbf|boxed|color|displaystyle|qquad|quad|left|right"
HTML_ETIKET = re.compile(r"</?(sub|sup|small|br|b|i|u|span|div|p|font|center)\b[^>]*>", re.I)
LISTE = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
MINITEST = re.compile(r"(?i)\bmini\s*test")
KISALTMA = re.compile(r"\b(ör|vb|vs|yak|bkz|Şek|Çiz|Tab|No|Dr|Prof|sn|dk|yy|Bkz|Kcal|kcal)\.")
KESIR = re.compile(
    r"(?<![\w/\\:.\-])"
    r"([A-Za-zΑ-Ωα-ωÇĞİÖŞÜçğıöşü][A-Za-z0-9Α-Ωα-ω₀-₉ₐ-ₜ’'′]{0,4}|\d+(?:[.,]\d+)?)"
    r"\s?/\s?"
    r"([A-Za-zΑ-Ωα-ωÇĞİÖŞÜçğıöşü][A-Za-z0-9Α-Ωα-ω₀-₉ₐ-ₜ’'′]{0,4}|\d+(?:[.,]\d+)?)"
    r"(?![\w/])")


class Sonuc:
    def __init__(s, ad):
        s.ad = ad
        s.bulgu = []          # (düzey, kod, satır, mesaj)
        s.tek = s.cift = 0    # sayılan geçişler
        s.kritik = s.kritik_ok = 0
        s.kavram = s.kavram_cift = 0
        s.emoji = 0
        s.terim = None        # terim dili ölçümü {toplam, uyumlu}

    def ekle(s, duzey, kod, satir, mesaj):
        s.bulgu.append((duzey, kod, satir, mesaj))

    def hata(s):
        return sum(1 for b in s.bulgu if b[0] == H)

    def uyari(s):
        return sum(1 for b in s.bulgu if b[0] == U)


# ---- boşluk türü ---------------------------------------------------------------
def ayirac_mi(satir):
    t = satir.strip(" \t\r")
    return t == "" or t == BR or (t != "" and set(t) <= {BR, "\u00a0", "\u200b", "\u3164"})


def ayirac_harf(satir):
    t = satir.strip(" \t\r")
    if t == "":
        return "b"
    if t == BR:
        return "B"
    return "X"


def aralik_turu(sep):
    if not sep:
        return "bitisik"
    j = "".join(ayirac_harf(x) for x in sep)
    return {"b": "tek", "bBb": "cift"}.get(j, "gecersiz")


# ---- bloklara ayır -----------------------------------------------------------------
def bloklara_ayir(satirlar):
    """[(tur, bas(1 tabanlı), satirlar, onceki_ayirac)], sondaki_ayirac"""
    bl, sep, i, n = [], [], 0, len(satirlar)

    def yeni(tur, bas, sat):
        bl.append([tur, bas + 1, sat, sep[:]])

    while i < n:
        s = satirlar[i]
        if ayirac_mi(s):
            sep.append(s)
            i += 1
            continue
        st = s.strip()
        if st.startswith("```"):
            j = i + 1
            while j < n and not satirlar[j].strip().startswith("```"):
                j += 1
            yeni("kod", i, satirlar[i:j + 1])
            i = j + 1
        elif st.startswith("$$"):
            j = i
            if st.count("$$") < 2:
                j = i + 1
                while j < n and "$$" not in satirlar[j]:
                    j += 1
            yeni("formul", i, satirlar[i:j + 1])
            i = j + 1
        elif re.match(r"#{1,6}\s", st):
            yeni("baslik", i, [s])
            i += 1
        elif st == "[widget]":
            yeni("widget", i, [s])
            i += 1
        elif st.startswith("|"):
            j = i
            while j < n and satirlar[j].strip().startswith("|"):
                j += 1
            yeni("tablo", i, satirlar[i:j])
            i = j
        elif LISTE.match(s):
            j = i
            while j < n and not ayirac_mi(satirlar[j]) and not re.match(r"#{1,6}\s", satirlar[j].strip()) \
                    and not satirlar[j].strip().startswith(("$$", "```")):
                j += 1
            # açık liste: tek boş satırla bölünmüş maddeler aynı liste
            if bl and bl[-1][0] == "liste" and aralik_turu(sep) == "tek":
                bl[-1][2] += satirlar[i:j]
            else:
                yeni("liste", i, satirlar[i:j])
            i = j
        else:
            j = i
            while j < n and not ayirac_mi(satirlar[j]):
                t = satirlar[j].strip()
                if j > i and (re.match(r"#{1,6}\s", t) or t.startswith(("$$", "```", "|")) or LISTE.match(satirlar[j]) or t == "[widget]"):
                    break
                j += 1
            yeni("paragraf", i, satirlar[i:j])
            i = j
        sep = []
    return bl, sep


# ---- matematik ---------------------------------------------------------------------
def maskele(metin):
    """Matematikleri çıkarır: ('blok'|'satir', içerik, satır_no0) listesi; kalan metinde blok=\\x00, satır içi=\\x01."""
    mat = []

    def degistir(desen, metin, isaret, tur, flags=0):
        out, son = [], 0
        for m in re.finditer(desen, metin, flags):
            out.append(metin[son:m.start()])
            mat.append((tur, m.group(1), metin.count("\n", 0, m.start())))
            out.append(isaret + "\n" * m.group(0).count("\n"))
            son = m.end()
        out.append(metin[son:])
        return "".join(out)

    k = degistir(r"\$\$(.+?)\$\$", metin, "\x00", "blok", re.S)
    k = degistir(r"(?<![\\$])\$([^$\n]+?)(?<!\\)\$", k, "\x01", "satir")
    return mat, k


def parantez_oku(t, i):
    """t[i]=='{' ise eşleşen '}' dizinini ve içeriği döndür."""
    d = 0
    for j in range(i, len(t)):
        if t[j] == "{":
            d += 1
        elif t[j] == "}":
            d -= 1
            if d == 0:
                return j, t[i + 1:j]
    return -1, t[i + 1:]


def matematik_kontrol(m, tur, satir, S, ham=False):
    t = re.sub(r"\\text\{[^{}]*\}", r"\\text{}", m)
    yasak = sorted(set(re.findall(r"\\(" + YASAK_KOMUT + r")\b", t)))
    if yasak:
        S.ekle(H, "F01", satir, "formülde " + " ".join("\\" + k for k in yasak) + " yazma (sohbette ham kod görünür; claude-sorunlari/formuller.md kural 2)")
    if re.search(r"\\[,;!]", t):
        S.ekle(U, "F12", satir, "formülde \\, \\; \\! boşluk komutu teyit bekliyor: bitişik yaz ya da \\cdot kullan")
    if re.search(r"(?<!\\)[_^](?!\{)", t):
        S.ekle(H, "F02", satir, "indis/üs süslü parantezsiz (P_X değil P_{X}, x^{2}); kural 3")
    u = re.sub(r"\\[{}]", "", t)
    if u.count("{") != u.count("}"):
        S.ekle(H, "F07", satir, "süslü parantez dengesiz: formül çizilmez, ham kod görünür")
    for mm in re.finditer(r"\\(?:d|t)?frac\{", t):
        i = mm.end() - 1
        s1, a = parantez_oku(t, i)
        if s1 < 0:
            continue
        b = ""
        if s1 + 1 < len(t) and t[s1 + 1] == "{":
            s2, b = parantez_oku(t, s1 + 1)
        else:
            s2 = s1
        if re.search(r"\\(?:d|t)?frac\b", a + b):
            S.ekle(H, "F03", satir, "kesrin içinde kesir: ara değeri ayrı blokta tanımla (kural 4)")
        if re.match(r"\s*\\times\s*100\b", t[s2 + 1:]):
            S.ekle(H, "F04", satir, "kesirden sonra \\times 100: çarpanı payın içine al (kural 4)")
    if "\\\\" in t:
        if "\\begin" in t:
            S.ekle(U, "F12", satir, "çok satırlı blok (aligned/matris) teyit bekliyor: ilk kullanışta görünüşü sor")
        else:
            S.ekle(H, "F06", satir, "bir blokta tek denklem: her denklemi ayrı $$ bloğuna yaz (kural 1)")
    elif re.search(r"\\begin\{(aligned|align|matrix|bmatrix|pmatrix|cases|array|split|gathered)\}", t):
        S.ekle(U, "F12", satir, "aligned/matris bloğu teyit bekliyor: tek örnekte görüldü, ilk kullanışta görünüşü sor")
    if "/" in t:
        S.ekle(H, "F08", satir, "formülde düz kesir (a/b): \\dfrac{pay}{payda} yaz; birim ise \\text{J/mol}")
    if re.search(r"(?<!\\)%", t):
        S.ekle(U, "F13", satir, "formülde çıplak % işareti yorum sayılabilir: \\% yaz")
    if tur == "satir" and re.match(r"\s*\d", t):
        S.ekle(U, "F12", satir, "satır içi formül rakamla başlıyor (${2}\\times 3$ biçimi daha güvenli); teyit bekliyor")


# ---- metin kontrolleri ---------------------------------------------------------------
def cumle_say(p):
    p = re.sub(r"\x00|\x01", "X", p)
    p = re.sub(r"\*\*|__|`", "", p)
    p = KISALTMA.sub(lambda m: m.group(0)[:-1] + "’", p)
    p = re.sub(r"(\d)\.(\d)", r"\1’\2", p)
    p = re.sub(r"\b(\d+)\.\s+(?=[a-zçğıöşü])", r"\1’ ", p)
    return len(re.findall(r"[.!?…]+[\"”)\]*]*(?:\s+(?=[A-ZÇĞİÖŞÜ0-9*(\"“])|\s*$)", p.strip()))


def duz_kesir(satir_metni, izin):
    s = re.sub(r"`[^`]*`", " ", satir_metni)
    s = re.sub(r"https?://\S+|\S+\.(?:md|py|json|html|js|pdf)\b", " ", s)
    s = re.sub(r"\x00|\x01", " ", s)
    bulunan = []
    for m in KESIR.finditer(s):
        a, b = m.group(1), m.group(2)
        ifade = f"{a}/{b}"
        if ifade in izin or ifade in IZINLI_KESIR:
            continue
        ta, tb = re.sub(r"[0-9²³]+$", "", a), re.sub(r"[0-9²³]+$", "", b)
        if ta in BIRIM and (tb in BIRIM or re.fullmatch(r"\d+", b)):   # mg/100 g gibi
            continue
        bulunan.append(ifade)
    return bulunan


def baslik_kontrol(metin, satir, S):
    t = re.sub(r"^#{1,6}\s*", "", metin)
    t = re.sub(r"\x00|\x01", " ", t)
    for tok in re.findall(r"[^\s/–—]+", t):
        tok = tok.lstrip("([“\"'*_`")
        if len(tok) >= 2 and tok[0].isalpha() and tok[0] == tok[0].lower() and tok == tok[0] + tok[1:].lower() and not any(c.isdigit() for c in tok):
            S.ekle(H, "S02", satir, f"başlıkta \"{tok}\" küçük harfle başlıyor: her kelimenin baş harfi büyük (i→İ, ı→I); cekirdek §3")
            break


def incele(ad, metin, ayar=None):
    ayar = ayar or {}
    S = Sonuc(ad)
    metin = metin.replace("\r\n", "\n").replace("\r", "\n")
    satirlar = metin.split("\n")
    for no, s in enumerate(satirlar, 1):
        if "\u00a0" in s:
            S.ekle(H, "B08", no, "U+00A0 (bölünmez boşluk) kullanma; çift boşluk için yalnız ⠀ (U+2800) satırı (cekirdek §3)")
    bl, son_sep = bloklara_ayir(satirlar)
    if not bl:
        S.ekle(H, "S00", 1, "mesaj boş")
        return S
    if bl[0][3]:
        S.ekle(U, "B10", 1, "mesaj boşlukla başlıyor: baştaki boş ve ⠀ satırlarını sil")
    if son_sep:
        S.ekle(U, "B10", len(satirlar), "mesaj boşlukla bitiyor: sondaki boş ve ⠀ satırlarını sil")

    idari = ayar.get("idari")
    govde = "\n".join("\n".join(b[2]) for b in bl if b[0] not in ("kod",))

    # --- boşluk düzeni ----------------------------------------------------------------
    n = len(bl)
    tur = [None] * n          # blok i'den önceki aralığın türü
    for i in range(n):
        tur[i] = aralik_turu(bl[i][3])
        if tur[i] == "gecersiz" and i > 0:
            j = "".join(ayirac_harf(x) for x in bl[i][3])
            neden = ("arka arkaya boş satır boşluk yaratmaz; çift boşluk için boş, ⠀, boş" if set(j) == {"b"} else
                     "arka arkaya iki ⠀ satırı" if j.count("B") >= 2 else
                     "⠀ satırının önü ve arkası boş satır olmalı (boş, ⠀, boş)")
            S.ekle(H, "B07", bl[i][1] - len(bl[i][3]), f"geçersiz boşluk düzeni: {neden} (cekirdek §3)")

    def blok_metni(b):
        return " ".join(x.strip() for x in b[2])

    gerek = [dict() for _ in range(n)]   # i. aralık için {tür: (kod, mesaj)}

    def iste(i, turu, kod, msj):
        if 0 < i < n:
            gerek[i].setdefault(turu, (kod, msj))

    for i, b in enumerate(bl):
        t0 = b[0]
        if t0 == "baslik":
            iste(i, "cift", "B01", "başlığın önünde çift boşluk (boş, ⠀, boş) olmalı")
            iste(i + 1, "tek", "B02", "başlığın altında tek boşluk olmalı (bitişik ya da çift değil)")
        elif t0 == "formul":
            iste(i, "cift", "B03", "formül bloğunun üstünde çift boşluk olmalı")
            iste(i + 1, "cift", "B04", "formül bloğunun altında çift boşluk olmalı")
        elif t0 == "widget":
            iste(i, "cift", "B11", "widget öncesi çift boşluk olmalı")
            iste(i + 1, "cift", "B11", "widget sonrası çift boşluk olmalı")
        if t0 in ("baslik", "paragraf") and MINITEST.search(blok_metni(b)[:60]):
            iste(i, "cift", "B05", "mini test başında çift boşluk olmalı")

    for i in range(1, n):
        if not gerek[i]:
            continue
        # başlık altı kuralı, formül/widget üstü isteğiyle çakışırsa başlık kazanır
        turu = "tek" if "tek" in gerek[i] else "cift"
        kod, msj = gerek[i][turu]
        S.kritik += 1
        if tur[i] == turu:
            S.kritik_ok += 1
        elif tur[i] != "gecersiz":
            S.ekle(H, kod, bl[i][1], msj)

    # liste başlığı ile ilk maddesi arasında boşluk olmaz
    for i in range(1, n):
        if bl[i][0] == "liste" and bl[i - 1][0] == "paragraf":
            onc = blok_metni(bl[i - 1])
            baslik_gibi = onc.endswith(":") or re.search(r":\*\*$", onc)
            if baslik_gibi and tur[i] in ("tek", "cift"):
                S.ekle(H, "B12", bl[i][1], "liste başlığı ile ilk maddesi arasında boşluk olmaz (cekirdek §3)")
            elif tur[i] == "bitisik" and not baslik_gibi:
                S.ekle(U, "B13", bl[i][1], "liste başlıksız bitişik: liste başlığı iki nokta ile bitmeli")
    # sayım (liste başlığı bağı ve geçersizler hariç)
    for i in range(1, n):
        if tur[i] == "tek":
            S.tek += 1
        elif tur[i] == "cift":
            S.cift += 1
    # yeni kavram açılışları (kalın terimle başlayan paragraf): bilgi amaçlı
    for i in range(1, n):
        if bl[i][0] == "paragraf":
            m = re.match(r"\*\*([^*]+)\*\*(?=\s*[\s(,—-]|$)", blok_metni(bl[i]))
            if m and not m.group(1).rstrip().endswith((":", ".")) and len(m.group(1).split()) <= 6 and len(blok_metni(bl[i])) > len(m.group(0)) + 10:
                S.kavram += 1
                if tur[i] == "cift":
                    S.kavram_cift += 1

    # --- içerik kontrolleri ---------------------------------------------------------------
    mat, kalan = maskele(govde)
    kal_sat = kalan.split("\n")
    # satır numarası eşlemesi: govde, kod blokları çıkarıldığı için blok başlangıcıyla eşleşir
    harita = []
    for b in bl:
        if b[0] == "kod":
            continue
        for k in range(len(b[2])):
            harita.append(b[1] + k)

    def gercek(k):
        return harita[k] if 0 <= k < len(harita) else (harita[-1] if harita else 1)

    for tur_m, ic, k in mat:
        matematik_kontrol(ic, tur_m, gercek(k), S)
    for k, s in enumerate(kal_sat):
        if re.search(r"\\\$", s) or "$" in re.sub(r"\\\$", "", s):
            S.ekle(H, "F05", gercek(k), "tek kalan $ ya da \\$: para birimi için $ yazma, \"50 dolar\" yaz (kural 5)")
        s2 = re.sub(r"`[^`]*`", "", s)
        if re.search(r"\\[A-Za-z]+|[_^]\{", s2):
            S.ekle(H, "F09", gercek(k), "formül dışında ham LaTeX (\\komut, _{ }, ^{ }): formülü $...$ ya da $$...$$ içine al")
        for f in duz_kesir(s2, ayar.get("izin", set())):
            S.ekle(H, "F10", gercek(k), f"düz metin kesir \"{f}\": gerçek pay/payda yaz, örn. $\\dfrac{{pay}}{{payda}}$ (cekirdek §4); birim ise bu uyarı çıkmaz")
        if "\x01'" in s2 or "\x01’" in s2:
            S.ekle(U, "F12", gercek(k), "satır içi formülden hemen sonra kesme işareti: \"$X$ matrisinin\" gibi yaz (teyit bekliyor)")
        if HTML_ETIKET.search(s2):
            S.ekle(H, "S01", gercek(k), "sohbet HTML etiketi göstermez (<sub> <sup> <small> <br> ...); küçültme widget içinde yapılır (cekirdek §3)")
    # blok formülün kendi satırında olması
    for b in bl:
        if b[0] == "formul":
            ic = "\n".join(b[2]).strip()
            m = re.match(r"\$\$(.+?)\$\$(.*)$", ic, re.S)
            if not m or m.group(2).strip():
                S.ekle(H, "F11", b[1], "blok formül kendi satırlarında olmalı: $$ ... $$ sonrasında metin kalmamalı")
        elif b[0] in ("paragraf", "liste", "tablo"):
            if re.search(r"\$\$", "\n".join(b[2])):
                S.ekle(H, "F11", b[1], "blok formül ($$) cümlenin içinde: kendi satırına al, üstüne ve altına boşluk koy")
    # formülün ardından sembol listesi
    for i, b in enumerate(bl):
        if b[0] == "formul":
            sonraki = bl[i + 1:i + 3]
            if not any(x[0] == "liste" for x in sonraki):
                S.ekle(U, "F14", b[1], "formülden sonra her sembolün anlamı madde madde yok (cekirdek §4: amaç cümlesi, formül, semboller)")
            if i == 0 or bl[i - 1][0] == "baslik":
                S.ekle(U, "F14", b[1], "formülün önünde amaç cümlesi yok (cekirdek §4)")

    # --- biçim kontrolleri -----------------------------------------------------------------
    for b in bl:
        if b[0] == "baslik":
            baslik_kontrol(b[2][0], b[1], S)
    if not idari:
        for b in bl:
            if b[0] == "paragraf":
                c = cumle_say(blok_metni(b))
                if c >= 4:
                    S.ekle(H, "S03", b[1], f"paragraf {c} cümle: paragraflar 1–2 cümle, metin duvarı yok (cekirdek §3)")
                elif c == 3:
                    S.ekle(U, "S03", b[1], "paragraf 3 cümle: 1–2 cümleye indir (cekirdek §3)")
        uzun = len(re.sub(r"\s+", " ", re.sub(r"\x00|\x01", "X", kalan)))
        if uzun > 1600:
            S.ekle(U, "S03", 1, f"mesaj {uzun} karakter: tek adım kısa metindir, böl ya da kısalt (cekirdek §2)")
        kal = re.findall(r"\*\*([^*]+)\*\*", kalan)
        if len(kal) > 10:
            S.ekle(U, "S06", 1, f"{len(kal)} kalın ifade: kalın yalnız önemli kavram ve tek genel kural cümlesi (cekirdek §3)")
        for k_ in kal:
            if len(k_) > 200:
                S.ekle(U, "S06", 1, "çok uzun kalın metin: genel kural cümlesi tek cümle olmalı")
        for k, s in enumerate(kal_sat):
            if not s.lstrip().startswith("#") and re.search(r"(?i)\b(slayt|slide|sayfa|sf)\.?\s*\d+|^\W*kaynak\s*:", s):
                S.ekle(U, "S04", gercek(k), "kaynak/sayfa bilgisi metne karışmış: yeri Ekstra düğmesi (ayar D, cekirdek §3)")
            if re.search(r"(?i)\b(rozet|seviye atla|oynayarak keşfet|xp)\b", s):
                S.ekle(U, "S05", gercek(k), "puan/rozet/oyunlaştırma yok (cekirdek §1)")
    else:
        dolu = [x for x in satirlar if x.strip()]
        if len(dolu) > 2:
            S.ekle(H, "S08", 1, f"idari mesaj {len(dolu)} satır: en çok 2 satır (cekirdek §1)")
        if any(b[0] == "baslik" for b in bl):
            S.ekle(U, "S08", 1, "idari mesajda başlık olmaz")
    harf = len(re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşü]", kalan))
    if harf >= 150 and not re.search(r"[çğıöşüÇĞİÖŞÜ]", kalan) and len(re.findall(r"\b(ve|bir|için|olarak|ile|bu)\b", kalan)) >= 3:
        S.ekle(U, "S10", 1, "Türkçe metinde hiç ç ğ ı ö ş ü yok: karakterler düşmüş (ASCII'ye dönmüş) olabilir")
    if ayar.get("ilk"):
        ilk = next((x.strip() for x in satirlar if x.strip()), "")
        if ilk != "## Kısa Cevap":
            S.ekle(H, "S07", 1, "ilk mesaj \"## Kısa Cevap\" ile başlamalı (gorevler/konu-anlat.md)")
        if not re.search(r"(?i)sonunda.{0,160}(abileceksin|ebileceksin)", govde, re.S):
            S.ekle(U, "S07", 1, "hedef cümlesi yok: \"Bu blok sonunda ... hesaplayabileceksin\" (gorevler/konu-anlat.md)")
    if not idari:
        adimlar = [b for b in bl if b[0] == "baslik" and re.search(r"\bAdım\s+\d+", b[2][0])]
        if len(adimlar) >= 2:
            S.ekle(U, "S11", adimlar[1][1], "bir mesaj = tek adım: ikinci adım başlığı yeni mesajda olmalı (cekirdek §2)")
        for b in adimlar:
            if re.match(r"#{1,6}\s+Adım\b", b[2][0]) and not re.match(r"#{1,6}\s+Adım\s+\d+:\s+\S", b[2][0]):
                S.ekle(H, "S12", b[1], "adım başlığı \"## Adım n: Başlık\" biçiminde olmalı (cekirdek §3)")
    if ayar.get("emoji"):
        S.emoji = kalan.count(ayar["emoji"])
        for d, k, no, m in EK.emoji_bulgulari(kalan, ayar):
            S.ekle(d, k, gercek(no - 1) if no else 0, m)
    if ayar.get("sozluk"):
        tb, S.terim = EK.terim_bulgulari(EK.duz_metin(kalan), ayar["sozluk"], EK.terim_mod(ayar, ayar.get("kod_c", "3")),
                                         bool(ayar.get("terim_her_gecis")), ayar.get("terim_muaf", []))
        for d, k, no, m in tb:
            S.ekle(d, k, gercek(no - 1) if no else 0, m)
    return S


def toplu(sonuclar, ayar):
    """Tüm mesajlar için çift boşluk payı ve emoji adedi."""
    cik = []
    tek = sum(s.tek for s in sonuclar)
    cift = sum(s.cift for s in sonuclar)
    top = tek + cift
    pay = 100.0 * cift / top if top else None
    lo, hi = ayar.get("cift_aralik", (20, 70))
    if pay is not None and top >= 10:
        if pay < lo:
            cik.append((H, "B09", f"çift boşluk payı %{pay:.0f} (tek {tek}, çift {cift}): çok az; önemli geçişlerin ~%40'ı çift olmalı (cekirdek §3). Sınır %{lo}–%{hi}"))
        elif pay > hi:
            cik.append((H, "B09", f"çift boşluk payı %{pay:.0f} (tek {tek}, çift {cift}): çok fazla; genel geçişler tek boşluk (cekirdek §3). Sınır %{lo}–%{hi}"))
        elif pay < 30 or pay > 55:
            cik.append((U, "B09", f"çift boşluk payı %{pay:.0f}: hedef ~%40 (30–55 arası rahat)"))
    kav = sum(s.kavram for s in sonuclar)
    kcf = sum(s.kavram_cift for s in sonuclar)
    if kav >= 3 and kcf * 100 < 25 * kav:
        cik.append((U, "B06", f"{kav} yeni kavram açılışından yalnız {kcf}'i çift boşlukla başlıyor: yeni kavramın önüne çift boşluk koy (cekirdek §3)"))
    if ayar.get("emoji") and ayar.get("emoji_adet"):
        lo2, hi2 = ayar["emoji_adet"]
        top_e = sum(s.emoji for s in sonuclar)
        if not (lo2 <= top_e <= hi2):
            cik.append((H, "S09", f"{ayar['emoji']} toplam {top_e} adet; istenen {lo2}–{hi2}"))
    return cik, tek, cift, pay, kav, kcf


# ---- rapor -----------------------------------------------------------------------------------
def yaz_ayrintili(sonuclar, tcik, tek, cift, pay):
    for s in sonuclar:
        terim = f" · terim uyumu {s.terim['uyumlu']}/{s.terim['toplam']} (%{100 * s.terim['uyumlu'] // s.terim['toplam']})" if s.terim and s.terim.get("toplam") else ""
        print(f"{s.ad}: {s.hata()} hata, {s.uyari()} uyarı · geçiş tek {s.tek}, çift {s.cift} · kritik yer {s.kritik}, uygun {s.kritik_ok}{terim}")
        for d, k, no, m in sorted(s.bulgu, key=lambda x: (x[2], x[1])):
            print(f"  {d} {k} satır {no}: {m}")
    for d, k, m in tcik:
        print(f"TOPLU {d} {k}: {m}")
    if pay is not None:
        kt = sum(s.kritik for s in sonuclar)
        ko = sum(s.kritik_ok for s in sonuclar)
        print(f"BOŞLUK: {tek + cift} geçiş, tek {tek} (%{100 - pay:.0f}), çift {cift} (%{pay:.0f}); kritik yer {kt}, uygun {ko}" +
              (f" (%{100 * ko / kt:.0f})" if kt else ""))


def rapor_satirlari(sonuclar, tcik, tek, cift, pay):
    h = sum(s.hata() for s in sonuclar) + sum(1 for x in tcik if x[0] == H)
    u = sum(s.uyari() for s in sonuclar) + sum(1 for x in tcik if x[0] == U)
    bosluk = f" · boşluk tek %{100 - pay:.0f} / çift %{pay:.0f}" if pay is not None else ""
    tt = sum(s.terim["toplam"] for s in sonuclar if s.terim)
    tu = sum(s.terim["uyumlu"] for s in sonuclar if s.terim)
    terim = f" · terim %{100 * tu // tt}" if tt else ""
    l1 = f"Anlatım kontrolü: {len(sonuclar)} mesaj, {h} hata, {u} uyarı{bosluk}{terim}."
    ilk = []
    for s in sonuclar:
        for d, k, no, m in s.bulgu:
            if d == H and f"{s.ad} s.{no} {k}" not in ilk:
                ilk.append(f"{s.ad} s.{no} {k}")
    for d, k, m in tcik:
        if d == H:
            ilk.append(k)
    l2 = ("Hatalar: " + "; ".join(ilk[:4]) + (f" (+{len(ilk) - 4})" if len(ilk) > 4 else "") + ".") if ilk else "Hata yok."
    return l1, l2, h


# ---- kendini deneme -----------------------------------------------------------------------------
TEK = "\n\n"
CIFT = "\n\n" + BR + "\n\n"


def _iyi_mesaj():
    return (
        "## Adım 2: Arrhenius Denklemi" + TEK +
        "Hız sabiti sıcaklıkla üstel artar. Bu yüzden küçük bir ısı artışı hızı çok değiştirir." + TEK +
        "**Aktivasyon enerjisi** (activation energy), tepkimenin başlaması için aşılması gereken enerji engelidir." + TEK +
        "Engel ne kadar yüksekse hız o kadar yavaştır." + CIFT +
        "Hız sabiti şu denklemle hesaplanır:" + CIFT +
        "$$k = A e^{-\\dfrac{E_{a}}{RT}}$$" + CIFT +
        "Burada:\n- $k$: hız sabiti\n- $A$: çarpan\n- $T$: sıcaklık (K)\n- $E_{a}$ değeri J/mol cinsindendir" + TEK +
        "Birimi kontrol et: J/mol ve m/s gibi birimler düz yazılabilir." + CIFT +
        "## Adım 3: Örnek Hesap" + TEK +
        "Önce sıcaklığı Kelvin'e çevir." + TEK +
        "Sonra değerleri yerine koy.")


def _denemeler():
    G = _iyi_mesaj
    # (ad, metin, ayar, olması gereken kodlar, olmaması gereken kodlar)
    D = [
        ("iyi mesaj hatasız", G(), {}, [], ["F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "F10", "F11", "B01", "B02", "B03", "B04", "B07", "B08", "B12", "S01", "S02", "S03"]),
        ("F01 yasak komut", "Metin.\n\n$$\\Large \\boldsymbol{x}$$", {}, ["F01"], []),
        ("F01 \\leftarrow serbest", "Oku:\n\n$x \\leftarrow y$", {}, [], ["F01"]),
        ("F02 süslüsüz indis", "Kısa $P_X$ olsun.", {}, ["F02"], []),
        ("F03 iç içe kesir", "Metin.\n\n$$\\dfrac{\\dfrac{a}{b}}{c}$$", {}, ["F03"], []),
        ("F04 çarpan dışarıda", "Metin.\n\n$$\\dfrac{a}{b} \\times 100$$", {}, ["F04"], []),
        ("F05 para birimi", "Fiyat 50$ olur.", {}, ["F05"], []),
        ("F05 ters bölü dolar", "Fiyat \\$50 olur.", {}, ["F05"], []),
        ("F06 çok denklem", "Metin.\n\n$$a = b \\\\ c = d$$", {}, ["F06"], []),
        ("F07 parantez", "Kısa $\\dfrac{a}{b$ olsun.", {}, ["F07"], []),
        ("F08 formülde düz kesir", "Kısa $a/b$ olsun.", {}, ["F08"], []),
        ("F08 text içinde birim serbest", "Kısa $E = 5\\ \\text{J/mol}$ olsun.", {}, [], ["F08"]),
        ("F09 çıplak latex", "Burada \\dfrac{a}{b} var.", {}, ["F09"], []),
        ("F10 düz kesir k2/k1", "Oran k2/k1 artar.", {}, ["F10"], []),
        ("F10 düz kesir 1/T", "Grafik 1/T eksenindedir.", {}, ["F10"], []),
        ("F10 birim serbest", "Değer 40 kJ/mol ve 3 m/s olsun.", {}, [], ["F10"]),
        ("F10 ve/veya serbest", "Su ve/veya yağ olabilir.", {}, [], ["F10"]),
        ("F10 izin ekle", "Ca/Mg oranı sabit.", {"izin": {"Ca/Mg"}}, [], ["F10"]),
        ("F11 blok cümle içinde", "Bak $$x=1$$ burada.", {}, ["F11"], []),
        ("F12 \\, komutu", "Kısa $a\\,b$ olsun.", {}, ["F12"], []),
        ("F14 formül sonrası liste yok", "Amaç cümlesi." + CIFT + "$$k = A$$" + CIFT + "Bitti.", {}, ["F14"], []),
        ("B01 başlık önü tek", "Giriş." + TEK + "## Adım 2: Hız", {}, ["B01"], []),
        ("B02 başlık altı çift", "## Adım 2: Hız" + CIFT + "Metin.", {}, ["B02"], []),
        ("B02 başlık altı bitişik", "## Adım 2: Hız\nMetin.", {}, ["B02"], []),
        ("B03 formül önü tek", "Amaç." + TEK + "$$k = A$$" + CIFT + "Burada:\n- $k$: hız", {}, ["B03"], []),
        ("B04 formül altı tek", "Amaç." + CIFT + "$$k = A$$" + TEK + "Burada:\n- $k$: hız", {}, ["B04"], []),
        ("B05 mini test önü tek", "Metin." + TEK + "**Mini Test**" + TEK + "Soru.", {}, ["B05"], []),
        ("B07 iki ⠀", "Birinci." + "\n\n" + BR + "\n\n" + BR + "\n\n" + "İkinci.", {}, ["B07"], []),
        ("B07 ⠀ yapışık", "Birinci.\n" + BR + "\nİkinci.", {}, ["B07"], []),
        ("B07 yığılmış boş satır", "Birinci.\n\n\n\nİkinci.", {}, ["B07"], []),
        ("B08 NBSP", "Metin\u00a0burada.", {}, ["B08"], []),
        ("B10 boşlukla başlıyor", "\n\nMetin.", {}, ["B10"], []),
        ("B12 liste başlığı ayrı", "Sıra:" + TEK + "- bir\n- iki", {}, ["B12"], []),
        ("S01 html", "Metin<br>burada.", {}, ["S01"], []),
        ("S02 küçük harfli başlık", "## adım 2: denklem", {}, ["S02"], []),
        ("S02 pH serbest", "## Adım 2: pH Ölçümü", {}, [], ["S02"]),
        ("S03 uzun paragraf", "Bir. İki. Üç. Dört. Beş.", {}, ["S03"], []),
        ("S03 kısaltma cümle değil", "Örneğin süt, yağ vb. maddeleri içerir. Bu, 3.5 gram demektir.", {}, [], ["S03"]),
        ("S04 sayfa", "Bu bilgi sayfa 12'de yazar.", {}, ["S04"], []),
        ("S04 alan başlığında slayt serbest", "## Ünite 2 · Slayt 3 · Adım 1: Matris Çarpımı", {}, [], ["S04", "S02"]),
        ("S07 ilk mesaj", "## Adım 1: Giriş", {"ilk": True}, ["S07"], []),
        ("S07 ilk mesaj doğru", "## Kısa Cevap" + TEK + "Bu blok sonunda hızı hesaplayabileceksin.", {"ilk": True}, [], ["S07"]),
        ("S08 idari uzun", "Bir.\nİki.\nÜç.", {"idari": True}, ["S08"], []),
        ("S10 ASCII Türkçe", "Bu konu icin bir ornek vereceyiz ve bu bir olarak ile bu surecte hizi gosterir " * 4, {}, ["S10"], []),
    ]
    return D


def kendini_dene():
    basarisiz = 0
    for ad, metin, ayar, olmali, olmamali in _denemeler():
        S = incele(ad, metin, ayar)
        kodlar = {b[1] for b in S.bulgu}
        sorun = [k for k in olmali if k not in kodlar] + [f"fazladan {k}" for k in olmamali if k in kodlar]
        if ad == "iyi mesaj hatasız" and S.hata():
            sorun.append("iyi mesajda hata çıktı: " + "; ".join(f"{b[1]}@{b[2]}" for b in S.bulgu if b[0] == H))
        if sorun:
            basarisiz += 1
            print(f"BAŞARISIZ · {ad}: {', '.join(sorun)}")
            for b in S.bulgu:
                print("    ", b)
        else:
            print(f"geçti · {ad}")
    # toplu: uç değerler
    harfler = "ABCDEFGHIJKL"   # 12 paragraf = 11 geçiş
    tek_cok = [incele("t", TEK.join(h + "." for h in harfler))]
    cift_cok = [incele("c", CIFT.join(h + "." for h in harfler))]
    iyi = [incele("i", "".join(h + "." + (CIFT if k in (1, 3, 6, 9) else TEK) for k, h in enumerate(harfler[:-1])) + harfler[-1] + ".")]
    for ad, ss, beklenen in (("toplu: hepsi tek (%0 çift) hata", tek_cok, True), ("toplu: hepsi çift (%100) hata", cift_cok, True), ("toplu: %40 civarı geçer", iyi, False)):
        c = toplu(ss, {})[0]
        var = any(x[0] == H and x[1] == "B09" for x in c)
        if var != beklenen:
            basarisiz += 1
            print(f"BAŞARISIZ · {ad}: {c}")
        else:
            print(f"geçti · {ad}")
    c = toplu([incele("e", "Metin 🙉 ve 🙉.", {"emoji": "🙉"})], {"emoji": "🙉", "emoji_adet": (3, 4)})[0]
    if not any(x[1] == "S09" for x in c):
        basarisiz += 1
        print("BAŞARISIZ · emoji adedi")
    else:
        print("geçti · emoji adedi sınırı")
    basarisiz += EK.kendini_dene()
    print(("KENDİNİ DENEME BAŞARISIZ: " + str(basarisiz)) if basarisiz else "KENDİNİ DENEME GEÇTİ")
    return 1 if basarisiz else 0


def aralik_oku(s, ad):
    try:
        a, b = s.split("-") if "-" in s else (s, s)
        return int(a), int(b)
    except ValueError:
        print(f"{ad}: \"{s}\" okunamadı (örnek 3-4)", file=sys.stderr)
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description="Anlatım mesajı testi (cekirdek §3–§4 + claude-sorunlari/formuller.md)")
    ap.add_argument("dosyalar", nargs="*", help="mesaj dosyaları, dizinler ya da - (stdin)")
    ap.add_argument("--rapor", action="store_true", help="sohbete yazılacak en çok 2 satırlık özet")
    ap.add_argument("--ilk", action="store_true")
    ap.add_argument("--idari", action="store_true")
    ap.add_argument("--emoji")
    ap.add_argument("--emoji-adet", default="")
    ap.add_argument("--izin", default="")
    ap.add_argument("--cift-aralik", default=None)
    ap.add_argument("--profil")
    ap.add_argument("--terim", choices=["C1", "C2", "C3"])
    ap.add_argument("--ders", default="")
    ap.add_argument("--sozluk", action="append", default=[])
    ap.add_argument("--kod", default="")
    ap.add_argument("--emoji-seri", default="")
    ap.add_argument("--test-turu", default="oto", choices=["oto", "mini", "tam"])
    ap.add_argument("--konu", action="append", default=[])
    ap.add_argument("--siki", action="store_true", help="uyarılar da hata sayılır")
    ap.add_argument("--kendini-dene", action="store_true")
    a = ap.parse_args()
    if a.kendini_dene:
        sys.exit(kendini_dene())
    if not a.dosyalar:
        ap.print_usage(sys.stderr)
        sys.exit(2)
    if a.profil and not os.path.isfile(a.profil):
        print(f"profil bulunamadı: {a.profil}", file=sys.stderr)
        sys.exit(2)
    ayar = EK.profil_oku(EK.profil_bul(a.profil))      # kişisel profil (yerel/denetim.json); komut satırı onu geçer
    ayar.update({"ilk": a.ilk, "idari": a.idari, "test_turu": a.test_turu})
    ayar.setdefault("izin", set())
    ayar["izin"] = set(ayar["izin"]) | {x.strip() for x in a.izin.split(",") if x.strip()}
    if a.emoji:
        ayar["emoji"] = a.emoji
    if a.cift_aralik:
        ayar["cift_aralik"] = aralik_oku(a.cift_aralik, "--cift-aralik")
    ayar.setdefault("cift_aralik", (20, 70))
    if a.emoji and a.emoji_adet:
        ayar["emoji_adet"] = aralik_oku(a.emoji_adet, "--emoji-adet")
    if a.emoji_seri:
        ayar["emoji_seri"] = list(aralik_oku(a.emoji_seri, "--emoji-seri"))
    if a.terim:
        ayar["terim_dili"] = a.terim
    ayar["kod_c"] = EK.kod_c(a.kod, ayar)
    if a.ders or a.sozluk or ayar.get("sozluk_yollari"):
        ayar["sozluk"] = EK.sozluk_topla(a.sozluk + EK.sozluk_yollari(a.ders, ayar))
        if not ayar["sozluk"]:
            print("UYARI: terim sözlüğü bulunamadı (--ders / --sozluk / profil); terim denetimi atlandı", file=sys.stderr)
    yollar = []
    for d in a.dosyalar:
        if d == "-":
            yollar.append("-")
        elif os.path.isdir(d):
            yollar += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith((".md", ".txt", ".html"))]
        else:
            yollar.append(d)
    if not yollar:
        print("mesaj dosyası bulunamadı", file=sys.stderr)
        sys.exit(2)
    sonuclar = []
    for y in yollar:
        try:
            metin = sys.stdin.read() if y == "-" else open(y, encoding="utf-8").read()
        except OSError as e:
            print(f"okunamadı: {y} ({e})", file=sys.stderr)
            sys.exit(2)
        ad = "stdin" if y == "-" else os.path.basename(y)
        uz = os.path.splitext(y)[1].lower()
        if uz in (".html", ".htm", ".json"):
            S = Sonuc(ad)
            for b in EK.dosya_bulgulari(uz, metin, ayar, ayar.get("sozluk"), a.konu, a.test_turu):
                S.ekle(*b)
            sonuclar.append(S)
        else:
            sonuclar.append(incele(ad, metin, ayar))
    tcik, tek, cift, pay, kav, kcf = toplu(sonuclar, ayar)
    if a.rapor:
        l1, l2, h = rapor_satirlari(sonuclar, tcik, tek, cift, pay)
        print(l1)
        print(l2)
    else:
        print("Profil: " + (ayar["profil_yolu"] if ayar.get("profil_yolu") else "yok (yalnız depo kuralları; kişisel kurallar için yerel/denetim.json)"))
        yaz_ayrintili(sonuclar, tcik, tek, cift, pay)
        h = sum(s.hata() for s in sonuclar) + sum(1 for x in tcik if x[0] == H)
        print("SONUÇ: " + ("GEÇTİ" if h == 0 else f"{h} HATA"))
    if a.siki:
        h += sum(s.uyari() for s in sonuclar) + sum(1 for x in tcik if x[0] == U)
    sys.exit(1 if h else 0)


if __name__ == "__main__":
    main()
