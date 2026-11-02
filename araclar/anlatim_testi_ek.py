#!/usr/bin/env python3
"""anlatim_testi.py'nin ek kuralları: terim dili, 🙉 serisi, test soruları, widget dosyası, kişisel profil.

Doğrudan çalıştırılmaz; `anlatim_testi.py` içe aktarır. Kendi denemeleri `python3 araclar/anlatim_testi.py --kendini-dene` ile çalışır.
Bulgu: (düzey, kod, satır, mesaj), anlatim_testi.Sonuc.bulgu ile aynı biçim. Kodlar:
  T = terim dili (cekirdek/temel.md + secenekler/C + kişisel profil "terim_dili"), E = emoji, W = widget (gorsel/stil.md),
  Q = test soruları (kişisel tercihler: İngilizce + parantezde Türkçe, konu ipucu yok, mini test sayısı; gorevler/soru-sor.md).
Kişisel tercihler depoya yazılmaz: kullanıcının proje klasöründeki yerel/denetim.json profilinden gelir (şablon: kurulum/yerel-denetim-sablonu.json).
"""
import collections, json, os, re

H, U = "HATA", "UYARI"
BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)
HARF = "A-Za-zÇĞİÖŞÜçğıöşü"
_TR = str.maketrans({"I": "ı", "İ": "i"})
_EN = str.maketrans({"İ": "i"})


def tr_kucuk(s):
    return s.translate(_TR).lower()


def en_kucuk(s):
    return s.translate(_EN).lower()


def satir_no(t, pos):
    return t.count("\n", 0, pos) + 1


# ───────────────────────────── kişisel profil ─────────────────────────────
def profil_bul(yol=None):
    """--profil > AI_DERS_PROFIL > ./yerel/denetim.json > /mnt/project-files/yerel/denetim.json."""
    for a in (yol, os.environ.get("AI_DERS_PROFIL"), os.path.join(os.getcwd(), "yerel", "denetim.json"), "/mnt/project-files/yerel/denetim.json"):
        if a and os.path.isfile(a):
            return a
    return None


def aralik(v):
    """'3-4' ya da [3, 4] ya da 3 -> (3, 4)."""
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return int(v[0]), int(v[1])
    a, _, b = str(v).partition("-")
    return int(a), int(b or a)


def profil_oku(yol):
    """Profil dosyası -> ayar sözlüğü (anlatim_testi ayar anahtarlarıyla) ve proje kökü."""
    if not yol:
        return {}
    try:
        p = json.load(open(yol, encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SystemExit(f"profil okunamadı ({yol}): {e}")
    kok = os.path.dirname(os.path.dirname(os.path.abspath(yol)))   # yerel/'in üstü = proje klasörü
    ayar = {"profil_yolu": yol, "proje_kok": kok}
    for k in ("emoji", "terim_dili", "terim_her_gecis", "mini_test_soru", "test_dil", "karisik_test", "widget_emoji_yasak", "terim_muaf"):
        if k in p:
            ayar[k] = p[k]
    if "emoji_seri" in p:
        ayar["emoji_seri"] = [int(x) for x in (p["emoji_seri"] if isinstance(p["emoji_seri"], list) else str(p["emoji_seri"]).replace("-", ",").split(","))]
    if "emoji_adet" in p:
        ayar["emoji_adet"] = aralik(p["emoji_adet"])
    if "cift_aralik" in p:
        ayar["cift_aralik"] = aralik(p["cift_aralik"])
    if "izin" in p:
        ayar["izin"] = set(p["izin"])
    ayar["sozluk_yollari"] = [y if os.path.isabs(y) else os.path.join(kok, y) for y in p.get("sozluk", [])]
    return ayar


def sozluk_yollari(ders, ayar):
    yollar = list(ayar.get("sozluk_yollari", []))
    if ders:
        yollar.append(os.path.join(KOK, "dersler", ders, "sozluk.md"))
        kok = ayar.get("proje_kok") or "/mnt/project-files"
        yollar.append(os.path.join(kok, "dersler", ders, "sozluk", "sozluk.json"))
    return yollar


# ───────────────────────────── terim dili ─────────────────────────────
def _anahtar(s):
    return re.sub(r"\s+", " ", re.sub(r"\s*\([^)]*\)", "", s)).strip()


def sozluk_yukle(yol):
    """.md tablo (Türkçe | İngilizce | Not) ya da .json (girdiler; yalnız alan='t' alan terimleri) -> [{'tr': [...], 'en': [...]}]."""
    ham = []
    if not yol or not os.path.exists(yol):
        return ham
    if yol.endswith(".json"):
        d = json.load(open(yol, encoding="utf-8"))
        for e in d.get("girdiler", []):
            if e.get("alan") != "t":
                continue
            ham.append(([x for it in e.get("tr", []) for x in re.split(r"[;/]", it)],
                        [e["en"]] + [b for b in e.get("bicimler", []) if not b.startswith("!")]))
    else:
        for l in open(yol, encoding="utf-8"):
            if not l.startswith("|"):
                continue
            h = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(h) >= 2 and not set(h[0]) <= set("-: ") and h[0].lower() not in ("türkçe", "turkce"):
                ham.append(([h[0]], [h[1]]))
    out = []
    for trs, ens in ham:
        trs = [t for t in (_anahtar(x) for x in trs) if len(t) >= 4]
        ens = [e for e in (_anahtar(x) for x in ens) if len(e) >= 3]
        # Türkçesi İngilizcesiyle aynı yazılan terim (protein) hangi dilde yazıldığı anlaşılmadığından denetlenmez
        trs = [t for t in trs if tr_kucuk(t) not in {en_kucuk(e) for e in ens}]
        if trs and ens:
            out.append({"tr": trs, "en": ens})
    return out


def sozluk_topla(yollar):
    gorulen, out = set(), []
    for y in yollar:
        for g in sozluk_yukle(y):
            k = (tuple(sorted(tr_kucuk(x) for x in g["tr"])), tuple(sorted(en_kucuk(x) for x in g["en"])))
            if k not in gorulen:
                gorulen.add(k)
                out.append(g)
    return out


def kod_c(kod, ayar):
    """Ayar kodundaki C rakamı: --kod > profil proje klasöründeki yerel/ayarlar.md 'Kod:' > depo varsayılanı (3)."""
    if not kod and ayar.get("proje_kok"):
        yol = os.path.join(ayar["proje_kok"], "yerel", "ayarlar.md")
        if os.path.isfile(yol):
            m = re.search(r"^Kod:\s*(\S+)", open(yol, encoding="utf-8").read(), re.M)
            kod = m.group(1) if m else ""
    m = re.search(r"C(\d)", (kod or "").upper())
    return m.group(1) if m else "3"


def terim_mod(ayar, kod_c="3"):
    m = str(ayar.get("terim_dili") or "C" + kod_c).upper()
    return m if m in ("C1", "C2", "C3") else "C3"


def terim_bulgulari(t, sozluk, mod, her_gecis, muaf=()):
    """Terimlerin yazılış sırasını denetler (t: biçim işaretleri temizlenmiş düz metin).
    C2: İngilizce (Türkçe), her_gecis ise her geçişte; C1/C3: Türkçe (İngilizce). -> (bulgular, ölçüm)"""
    bulgular, ok, say, ihlal = [], 0, 0, []
    low_tr, low_en = tr_kucuk(t), en_kucuk(t)
    if len(low_tr) != len(t) or len(low_en) != len(t):
        return bulgular, {"toplam": 0, "uyumlu": 0}
    muaf = {tr_kucuk(x) for x in muaf}
    olaylar = []
    for gi, g in enumerate(sozluk):
        for en in g["en"]:
            e = en_kucuk(en)
            if e in muaf or e not in low_en:
                continue
            for m in re.finditer(rf"(?<![{HARF}]){re.escape(e)}(?:s|es)?(?![{HARF}])", low_en):
                olaylar.append((m.start(), m.end(), "en", gi))
        for tr in g["tr"]:
            x = tr_kucuk(tr)
            if x in muaf or x not in low_tr:
                continue
            for m in re.finditer(rf"(?<![{HARF}]){re.escape(x)}[a-zçğıöşü]{{0,7}}(?![{HARF}])", low_tr):
                olaylar.append((m.start(), m.end(), "tr", gi))
    olaylar.sort(key=lambda o: (-(o[1] - o[0]), o[0]))     # çakışmada uzun terim kazanır
    kabul = []
    for o in olaylar:
        if not any(o[0] < k[1] and k[0] < o[1] for k in kabul):
            kabul.append(o)
    kabul.sort()
    paren = re.compile(r"\s*\(([^()\n]{1,120})\)")

    for s, e, dil, gi in kabul:
        g = sozluk[gi]
        pm = paren.match(t, e)
        ic = (tr_kucuk(pm.group(1)), en_kucuk(pm.group(1))) if pm else None
        idx = t.rfind("(", max(0, s - 130), s)
        onceki_tr = tr_kucuk(t[:idx].rstrip()) if idx != -1 and ")" not in t[idx:s] else ""
        onceki_en = en_kucuk(t[:idx].rstrip()) if onceki_tr else ""
        if dil == "en":
            if ic and any(tr_kucuk(x) in ic[0] for x in g["tr"]):
                durum = "en_tr"                     # İngilizce (Türkçe)
            elif onceki_tr and any(re.search(re.escape(tr_kucuk(x)) + r"[a-zçğıöşü]{0,7}$", onceki_tr) for x in g["tr"]):
                continue                            # "Türkçe (İngilizce)" çiftinin parantez içi yarısı: çifti baştaki terim temsil eder
            else:
                durum = "en_cirpak"
        else:
            if ic and any(en_kucuk(x) in ic[1] for x in g["en"]):
                durum = "tr_en"                     # Türkçe (İngilizce)
            elif onceki_en and any(re.search(re.escape(en_kucuk(x)) + r"(?:s|es)?$", onceki_en) for x in g["en"]):
                continue                            # "İngilizce (Türkçe)" çiftinin parantez içi yarısı
            else:
                durum = "tr_cirpak"
        say += 1
        ln, ad = satir_no(t, s), t[s:e].strip()
        ornek = f"{g['en'][0]} ({g['tr'][0]})" if mod == "C2" else f"{g['tr'][0]} ({g['en'][0]})"
        if mod == "C2":
            if durum == "en_tr":
                ok += 1
            elif durum == "tr_en":
                ihlal.append((H, "T01", ln, f"terim sırası ters: \"{ad}\" → \"{ornek}\" (İngilizce önce, Türkçesi parantezde)"))
            elif durum == "tr_cirpak":
                ihlal.append((H, "T02", ln, f"Türkçe terim tek başına: \"{ad}\" → \"{ornek}\" (terimler İngilizce yazılır, Türkçesi parantezde)"))
            elif her_gecis:
                ihlal.append((H, "T03", ln, f"İngilizce terimin Türkçesi yok: \"{ad}\" → \"{ornek}\" (her geçişte Türkçesi parantezde)"))
            else:
                ok += 1
        else:
            if durum == "tr_cirpak":
                ok += 1
            elif durum == "tr_en":
                ok += 1
            elif durum == "en_tr":
                ihlal.append((H, "T01", ln, f"terim sırası ters: \"{ad}\" → \"{ornek}\" (Türkçe önce, İngilizcesi parantezde)"))
            else:
                bulgular.append((U, "T04", ln, f"\"{ad}\" İngilizce yazılmış; ayar {mod}: Türkçe terim, İngilizcesi parantezde"))
    bulgular += ihlal[:12]
    if len(ihlal) > 12:
        bulgular.append((H, ihlal[0][1], 0, f"… ve {len(ihlal) - 12} terim ihlali daha"))
    return bulgular, {"toplam": say, "uyumlu": ok, "ihlal": len(ihlal)}


def duz_metin(t):
    """Biçim işaretlerini, formül yer tutucularını ve bağlantıları temizler (uzunluk korunur)."""
    t = re.sub(r"[\x00\x01]", " ", t)
    t = re.sub(r"https?://\S+", lambda m: " " * len(m.group(0)), t)
    return re.sub(r"[*_`]", " ", t)


# ───────────────────────────── emoji ─────────────────────────────
def emoji_bulgulari(t, ayar):
    """Kişisel emoji serisi: 🙉 yalnız `emoji_seri` uzunluğunda (ör. 3 ya da 4) yazılır; tek/çift ya da fazlası yok."""
    e, seri = ayar.get("emoji"), ayar.get("emoji_seri")
    b = []
    if not e or not seri:
        return b
    gruplar = [(m.start(), len(m.group(0)) // len(e)) for m in re.finditer("(?:" + re.escape(e) + ")+", t)]
    for pos, uz in gruplar:
        if uz not in seri:
            b.append((H, "E01", satir_no(t, pos), f"{e} × {uz}: yalnız {' veya '.join(map(str, seri))} tane yazılır (tek ya da çift {e} yok; yüksek ihtimal {min(seri)}, çok yüksek {max(seri)})"))
    if len(gruplar) > 4:
        b.append((U, "E02", 0, f"{len(gruplar)} yerde {e}: yalnız gerçekten kritik yerlerde, az sayıda"))
    return b


# ───────────────────────────── widget ─────────────────────────────
SCRIPT = re.compile(r"<script\b[^>]*>(.*?)</script>", re.S | re.I)
STIL = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S | re.I)


def widget_metni(html):
    g = SCRIPT.sub(" ", STIL.sub(" ", html))
    g = re.sub(r"<!--.*?-->", " ", g, flags=re.S)
    g = re.sub(r"<[^>]+>", " ", g)
    return g.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")


def widget_bulgulari(html, ayar):
    """Widget kuralları (gorsel/stil.md §4–§8): yalnız makinenin kesin görebildikleri."""
    b = []
    for m in re.finditer(r"<button\b", html, re.I):
        b.append((H, "W01", satir_no(html, m.start()), "<button> kullanma: sohbet kendi düğme stilini basıp rengini siliyor; <div role=\"button\" tabindex=\"0\"> yaz (gorsel/stil.md §5)"))
    for k in ("ResizeObserver", "setInterval"):
        for m in re.finditer(k, html):
            b.append((H, "W02", satir_no(html, m.start()), f"{k} kullanma: git-gel hatası yapıyor, yeniden boyutlandırma yalnız window.resize (gorsel/stil.md §8)"))
    for m in re.finditer(r"<script\b[^>]*\bsrc\s*=|<link\b[^>]*href\s*=\s*[\"']?https?:", html, re.I):
        b.append((H, "W03", satir_no(html, m.start()), "dış kütüphane ya da dış stil dosyası yok (gorsel/stil.md §8)"))
    for m in re.finditer(r"<(sup|sub)\b", html, re.I):
        b.append((U, "W04", satir_no(html, m.start()), f"<{m.group(1).lower()}> yerine üs/alt indis ayrı yukarı/aşağı yerde grid ile yapılır (gorsel/stil.md §6)"))
    if not re.search(r"overflow\s*:\s*hidden", html):
        b.append((U, "W05", 0, "html,body{overflow:hidden} yok (gorsel/stil.md §8)"))
    if "text-size-adjust" not in html:
        b.append((U, "W05", 0, "text-size-adjust:100% yok: telefon yan çevrilince yazı büyür (gorsel/stil.md §5)"))
    for m in re.finditer(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", html):
        if float(m.group(1)) < 13:
            b.append((U, "W06", satir_no(html, m.start()), f"yazı {m.group(1)} px: en küçük 13 px (gorsel/stil.md §5)"))
    for m in re.finditer(r"(?<![-\w])(color|background(?:-color)?)\s*:\s*#(?!(?:fff|ffffff|000|000000)\b)[0-9a-fA-F]{3,8}\b", html):
        b.append((U, "W07", satir_no(html, m.start()), f"\"{m.group(0)}\": yazı ve zemin için sabit hex yok, tema değişkeni kullan (gorsel/stil.md §4)"))
    for e in ayar.get("widget_emoji_yasak", []):
        if e in html:
            b.append((H, "E03", satir_no(html, html.index(e)), f"{e} widget'ın içine konmaz (yalnız mesaj metnine)"))
    return b


# ───────────────────────────── test soruları ─────────────────────────────
TR_SOZ = set("ve bir bu için ile mi mı mu mü hangi kaç ne olan olarak gibi daha çok en de da ise veya ancak değil midir nedir hangisi "
             "aşağıdaki hangisidir kadar sonra önce her bazı fakat çünkü yani yalnız yalnızca olur olmaz oranı oldu olduğu".split())
EN_SOZ = set("the of is are and which what a an to in for with that this by as on from be does do how at or not its it has have will can "
             "than most least following true false when where who whose these those their there if into between".split())
SAYFA_IPUCU = re.compile(r"\b(slayt|slide|sayfa|page|adım|step|ünite|unit|chapter|bölüm|section|şekil|figure|tablo|table)\s*\.?\s*\d+|\b(?:s|sf|p|pp)\.\s*\d+", re.I)


def dil_tahmin(s):
    k = re.findall(rf"[{HARF}]+", s)
    if len(k) < 3:
        return "?"
    tr = sum(1 for x in k if tr_kucuk(x) in TR_SOZ) + 2 * sum(1 for x in k if any(c in "çğıöşüÇĞİÖŞÜ" for c in x))
    en = sum(1 for x in k if en_kucuk(x) in EN_SOZ)
    return "tr" if tr > en and tr >= 1 else "en" if en > tr else "?"


def kelimeli_mi(s):
    return bool(re.search(r"[A-Za-zÇĞİÖŞÜçğıöşü]{4,}", re.sub(r"[_^]\{[^}]*\}", "", s)))


def en_tr_ayir(s):
    m = re.search(r"\(([^()]*)\)\s*[?.!:]?\s*$", s)
    return (s[:m.start()].strip(), m.group(1).strip()) if m and m.start() > 0 else (s.strip(), "")


def js_oku(src, i=0):
    """Basit JS sabiti (dizi, dize, sayı, true/false/null) ayrıştırıcı. -> (değer, bitiş)"""
    while src[i] in " \t\r\n":
        i += 1
    c = src[i]
    if c == "[":
        out, i = [], i + 1
        while True:
            while src[i] in " \t\r\n,":
                i += 1
            if src[i] == "]":
                return out, i + 1
            v, i = js_oku(src, i)
            out.append(v)
    if c in "'\"":
        q, i, buf = c, i + 1, []
        while src[i] != q:
            if src[i] == "\\":
                i += 1
                buf.append({"n": "\n", "t": "\t"}.get(src[i], src[i]))
            else:
                buf.append(src[i])
            i += 1
        return "".join(buf), i + 1
    m = re.compile(r"-?\d+(?:\.\d+)?|true|false|null").match(src, i)
    if not m:
        raise ValueError(src[i:i + 20])
    v = m.group(0)
    return (float(v) if "." in v else int(v)) if v[0] in "-0123456789" else {"true": True, "false": False, "null": None}[v], m.end()


def w10_sorular(html):
    """W10 mini test: `var Q=[[metin,[şıklar],doğru,açıklama,ipucu?],...]` -> sorular ya da None (W10 değil)."""
    m = re.search(r"\b(?:var|let|const)\s+Q\s*=\s*\[", html)
    if not m:
        return None
    try:
        dizi, _ = js_oku(html, m.end() - 1)
    except (ValueError, IndexError):
        return None
    out = []
    for i, q in enumerate(dizi, 1):
        if isinstance(q, list) and len(q) >= 4 and isinstance(q[0], str) and isinstance(q[1], list) and isinstance(q[2], int) and all(isinstance(x, str) for x in q[1]):
            out.append({"no": i, "soru": q[0], "soru_tr": "", "siklar": [{"metin": s, "tr": ""} for s in q[1]], "dogru": q[2], "aciklama": [q[3]],
                        "ipucu": q[4] if len(q) > 4 and isinstance(q[4], str) else "", "birlesik": True,
                        "bolum": q[5] if len(q) > 5 and isinstance(q[5], str) else ""})   # 6. eleman: görünmez konu etiketi (karışık soru denetimi)
    return out or None


def w24_html_sorular(html):
    m = re.search(r"/\*VERI\*/(.*?)/\*VERI_SON\*/", html, re.S)
    if not m:
        return None, "hep"
    try:
        v = json.loads(m.group(1))
    except ValueError:
        return None, "hep"
    return ([{"no": q.get("n"), "soru": q.get("e", ""), "soru_tr": q.get("r", ""), "siklar": [{"metin": o[0], "tr": o[1] if len(o) > 1 else ""} for o in q.get("o", [])],
              "dogru": q.get("a"), "aciklama": q.get("x", []), "ipucu": q.get("h", ""), "bolum": q.get("g", ""), "konu": q.get("c", "")} for q in v.get("q", [])],
            {"h": "hep", "s": "sorular", "y": "yok"}.get(v.get("kr"), "hep"))


def json_sorular(d):
    out = []
    for i, q in enumerate(d.get("sorular", []), 1):
        dg = str(q.get("dogru", "")).strip().upper()
        out.append({"no": q.get("no", i), "soru": q.get("soru", ""), "soru_tr": q.get("soru_tr", ""),
                    "siklar": [{"metin": s.get("metin", ""), "tr": s.get("tr", "")} for s in q.get("siklar", [])],
                    "dogru": "ABCDE".index(dg) if len(dg) == 1 and dg in "ABCDE" else None,
                    "aciklama": q["aciklama"] if isinstance(q.get("aciklama"), list) else [q.get("aciklama", "")],
                    "ipucu": q.get("ipucu", ""), "bolum": q.get("bolum", ""), "konu": q.get("konu", "")})
    return out


def soru_bulgulari(sorular, ayar, konu_adlari=(), tur="oto", karistir="hep"):
    """Test sorularını denetler (W10, W24 widget'ı ve W24 JSON ortak)."""
    B, n = [], len(sorular)
    if not n:
        return [(H, "Q13", 0, "soru bulunamadı")]
    say = ayar.get("mini_test_soru")
    if tur == "mini" and say and n != say:
        B.append((H, "Q01", 0, f"mini test {say} soru olmalı ({n} var)"))
    en_tr = ayar.get("test_dil") == "en-tr"
    dagilim, uzun_dogru, gorulen = collections.Counter(), 0, set()
    for q in sorular:
        et, sik = f"soru {q['no']}", q["siklar"]
        if len(sik) < 3:
            B.append((H, "Q02", 0, f"{et}: en az 3 şık gerek (tuzaklı sınav sorusu)"))
        if not isinstance(q["dogru"], int) or not 0 <= q["dogru"] < max(len(sik), 1):
            B.append((H, "Q03", 0, f"{et}: doğru cevap şık aralığında değil"))
            continue
        dagilim[q["dogru"]] += 1
        metinler = [(s["metin"] + " " + s["tr"]).strip() for s in sik]
        if len({en_kucuk(m) for m in metinler}) != len(metinler):
            B.append((H, "Q04", 0, f"{et}: aynı metinli şıklar var"))
        anahtar = en_kucuk(" ".join(q["soru"].split()))
        if anahtar in gorulen:
            B.append((H, "Q05", 0, f"{et}: aynı soru ikinci kez sorulmuş"))
        gorulen.add(anahtar)
        if not "".join(str(a) for a in q["aciklama"]).strip():
            B.append((H, "Q06", 0, f"{et}: açıklama boş"))
        if len(q["soru"]) < 25:
            B.append((U, "Q07", 0, f"{et}: çok kısa; sınav sorusu tek adımlı olmamalı"))
        gorunen = " ".join([q["soru"], q["soru_tr"], q["ipucu"]] + metinler)     # cevaptan önce görünen her şey
        m = SAYFA_IPUCU.search(gorunen)
        if m:
            B.append((H, "Q08", 0, f"{et}: \"{m.group(0)}\" konuyu ele verir; sayfa/slayt/adım numarası yalnız cevaptan sonra, açıklamada yazılır"))
        for ad in konu_adlari:
            if ad and en_kucuk(ad) in en_kucuk(gorunen):
                B.append((H, "Q08", 0, f"{et}: \"{ad}\" konu/adım adı soruda ya da şıkta geçiyor; soru konuyu ele vermemeli"))
        if en_tr:
            if q.get("birlesik"):
                for ad, s in [("soru", q["soru"])] + [(f"şık {chr(65 + j)}", x["metin"]) for j, x in enumerate(sik)]:
                    ing, trk = en_tr_ayir(s)
                    if not kelimeli_mi(ing):
                        continue
                    if not trk:
                        B.append((H, "Q09", 0, f"{et} {ad}: İngilizce yazılır, Türkçesi parantez içinde verilir; Türkçe yok"))
                    elif dil_tahmin(ing) == "tr":
                        B.append((H, "Q09", 0, f"{et} {ad}: ana metin Türkçe; İngilizce olmalı, Türkçesi parantezde"))
                    elif dil_tahmin(trk) == "en":
                        B.append((H, "Q09", 0, f"{et} {ad}: parantezdeki kısım İngilizce; Türkçe olmalı"))
            else:
                if dil_tahmin(q["soru"]) == "tr":
                    B.append((H, "Q09", 0, f"{et}: soru İngilizce yazılmalı (Türkçesi soru_tr'de)"))
                if kelimeli_mi(q["soru"]) and not str(q["soru_tr"]).strip():
                    B.append((H, "Q09", 0, f"{et}: Türkçe çeviri yok"))
                for j, s in enumerate(sik):
                    if kelimeli_mi(s["metin"]) and not str(s["tr"]).strip():
                        B.append((H, "Q09", 0, f"{et} şık {chr(65 + j)}: Türkçe çeviri yok"))
        if len(sik) == 4 and len(metinler[q["dogru"]]) == max(len(m) for m in metinler) and len({len(m) for m in metinler}) > 1:
            uzun_dogru += 1
    top = sum(dagilim.values())
    if top >= 3:
        harf, adet = dagilim.most_common(1)[0]
        if (top >= 4 and adet / top > 0.6) or adet == top:
            B.append((H, "Q10", 0, f"doğru cevaplar çoğunlukla aynı şıkta ({chr(65 + harf)}: {adet}/{top}); şık sırasını dağıt"))
    if top >= 5 and uzun_dogru / top > 0.7:
        B.append((U, "Q11", 0, f"doğru şık {uzun_dogru}/{top} soruda en uzun şık: çeldiricileri uzat, şık uzunluğu ipucu vermesin"))
    etiket = [str(q.get("bolum") or q.get("konu") or "") for q in sorular]
    mini = tur == "mini" or (tur == "oto" and n <= 4)
    if ayar.get("karisik_test") and n >= 2:
        # karışık sorular: soru hangi konudan olduğunu ele vermesin; konu etiketi görünmez veridir (W10 6. eleman, W24/JSON bolum)
        if not all(etiket):
            B.append((H, "Q15", 0, "karışık soru denetimi için her soruya konu etiketi yaz (W10: sorunun 6. elemanı, JSON: bolum); etiket ekranda görünmez"))
        elif mini and len(set(etiket)) < 2:
            B.append((H, "Q15", 0, f"mini testin {n} sorusu da aynı konudan ({etiket[0]}); sorular farklı konulardan karışık olmalı"))
        elif mini and konu_adlari and all(e in {en_kucuk(k) for k in konu_adlari} for e in map(en_kucuk, etiket)):
            B.append((H, "Q15", 0, "mini testin hepsi güncel konudan; en az biri önceki bir konudan olmalı (ilk başlıkta kaynağın uzak alt başlıklarından)"))
    if karistir == "yok" and all(etiket) and (tur == "tam" or (tur == "oto" and n >= 8)):
        for a, b, ea, eb in zip(sorular, sorular[1:], etiket, etiket[1:]):
            if ea == eb:
                B.append((H, "Q12", 0, f"soru {a['no']} ve {b['no']} art arda aynı konudan ({ea}); tam testte sorular karışık olmalı"))
    return B


def tekrarsiz(bulgular):
    """Aynı düzey, kod, satır ve iletiyi tek bulguda toplar ("×n")."""
    sayim = collections.OrderedDict()
    for b in bulgular:
        sayim[b] = sayim.get(b, 0) + 1
    return [(d, k, ln, m + (f" (×{n})" if n > 1 else "")) for (d, k, ln, m), n in sayim.items()]


# ───────────────────────────── dosya türleri (.html, .json) ─────────────────────────────
def dosya_bulgulari(uzanti, metin, ayar, sozluk=None, konu_adlari=(), test_turu="oto"):
    """Widget (.html) ya da soru verisi (.json) -> bulgular. Mesaj (.md) anlatim_testi.incele ile denetlenir."""
    b = []
    if uzanti in (".html", ".htm"):
        b += widget_bulgulari(metin, ayar)
        if sozluk:
            tb, _ = terim_bulgulari(duz_metin(widget_metni(metin)), sozluk, terim_mod(ayar), bool(ayar.get("terim_her_gecis")), ayar.get("terim_muaf", []))
            b += tb
        sorular, karistir = w10_sorular(metin), "yok"      # W10 şıkları ve soruları karıştırmaz; W24 çalışırken karıştırır
        if sorular is None:
            sorular, karistir = w24_html_sorular(metin)
        if sorular is not None:
            b += soru_bulgulari(sorular, ayar, konu_adlari, test_turu, karistir)
    elif uzanti == ".json":
        try:
            d = json.loads(metin)
        except ValueError as e:
            return [(H, "Q13", 0, f"JSON okunamadı: {e}")]
        import soru_testi
        hata, uyari = soru_testi.dogrula(d, gevsek=False) if isinstance(d, dict) else (["JSON bir sözlük değil"], [])
        b += [(H, "Q14", 0, x) for x in hata] + [(U, "Q14", 0, x) for x in uyari]
        if isinstance(d, dict) and isinstance(d.get("sorular"), list) and d["sorular"]:
            a2 = dict(ayar)
            if d.get("dil", "en-tr") == "en-tr" and not a2.get("test_dil"):
                a2["test_dil"] = "en-tr"
            b += soru_bulgulari(json_sorular(d), a2, konu_adlari, test_turu, d.get("karistir", "hep"))
    return tekrarsiz(b)


# ───────────────────────────── kendini deneme ─────────────────────────────
SOZ = [{"tr": ["su aktivitesi"], "en": ["water activity"]}, {"tr": ["bağlı su"], "en": ["bound water"]}, {"tr": ["serbest su"], "en": ["free water"]}]


def _w10(sorular):
    return "<div id=w></div><script>var Q=" + json.dumps(sorular, ensure_ascii=False) + ";</script>"


def _s(i, dogru):
    sik = [f"Option {chr(65 + j)} for question {i} (Soru {i} için seçenek {chr(65 + j)})" for j in range(4)]
    return [f"Which option is correct for question number {i}? (Soru {i} için hangi seçenek doğrudur?)", sik, dogru, f"Açıklama {i}."]


Q_IYI = [["Which food has the lowest water activity? (Hangi gıdanın su aktivitesi en düşüktür?)",
          ["Fresh milk (Taze süt)", "Raw meat (Çiğ et)", "Honey (Bal)", "Cooked rice (Pişmiş pirinç)"], 2, "Bal şekerce zengindir.", "Serbest su nerede az?"],
         ["Which statement about bound water is correct? (Bağlı su hakkında hangisi doğrudur?)",
          ["It freezes first (İlk o donar)", "It cannot act as a solvent (Çözücü olamaz)", "It is the same as total water (Toplam suyla aynıdır)", "It is always above 0.9 (Hep 0.9 üstündedir)"], 1, "Bağlı su çözücü değildir."]]
def _et(q, konu):
    """Soruya 6. eleman olarak görünmez konu etiketi ekler."""
    return list(q[:4]) + [q[4] if len(q) > 4 else "", konu]


C2 = {"terim_dili": "C2", "terim_her_gecis": True, "emoji": "🙉", "emoji_seri": [3, 4], "widget_emoji_yasak": ["🙉"], "mini_test_soru": 2, "test_dil": "en-tr"}


def _denemeler():
    """(ad, işlev, beklenen kodlar, olmaması gereken kodlar)"""
    def terim(metin, mod="C2", her=True):
        return terim_bulgulari(duz_metin(metin), SOZ, mod, her)[0]

    def widget(html, ayar=None, **kw):
        return dosya_bulgulari(".html", html, dict(C2, **(ayar or {})), None, **kw)

    def sor(q, ayar=None, **kw):
        return dosya_bulgulari(".html", _w10(q), dict(C2, **(ayar or {})), None, **kw)

    dagit = [_s(i, i % 4) for i in range(6)]
    return [
        ("T C2 doğru", lambda: terim("Water activity (su aktivitesi) önemlidir. **Bound water (bağlı su)** kapalıdır."), [], ["T01", "T02", "T03"]),
        ("T01 C2 ters sıra", lambda: terim("Su aktivitesi (water activity) önemlidir."), ["T01"], ["T02"]),
        ("T02 C2 Türkçe çıplak", lambda: terim("Bağlı su kapalıdır."), ["T02"], []),
        ("T02 C2 Türkçe çekimli", lambda: terim("Bağlı suyun miktarı artar."), ["T02"], []),
        ("T03 C2 İngilizce Türkçesiz (her geçiş)", lambda: terim("Water activity düştü."), ["T03"], []),
        ("T03 ilk geçiş modunda çıplak İngilizce serbest", lambda: terim("Water activity düştü.", her=False), [], ["T03", "T02"]),
        ("T C2 başlıkta da geçerli", lambda: terim("## Adım 1: Water Activity"), ["T03"], []),
        ("T01 C3 ters sıra", lambda: terim("Water activity (su aktivitesi) önemlidir.", "C3"), ["T01"], []),
        ("T C3 doğru", lambda: terim("Su aktivitesi (water activity) önemlidir.", "C3"), [], ["T01", "T02"]),
        ("T04 C3 İngilizce çıplak uyarı", lambda: terim("Water activity düştü.", "C3"), ["T04"], ["T01"]),
        ("T uç: hepsi ters", lambda: terim("\n".join("Su aktivitesi (water activity) bir." for _ in range(8))), ["T01"], []),
        ("E01 tek 🙉", lambda: emoji_bulgulari("Önemli 🙉 kural.", C2), ["E01"], []),
        ("E01 çift 🙉", lambda: emoji_bulgulari("Önemli 🙉🙉 kural.", C2), ["E01"], []),
        ("E01 beşli 🙉", lambda: emoji_bulgulari("Önemli 🙉🙉🙉🙉🙉 kural.", C2), ["E01"], []),
        ("E 3 ve 4 serbest", lambda: emoji_bulgulari("A 🙉🙉🙉 ve B 🙉🙉🙉🙉.", C2), [], ["E01"]),
        ("E03 widget içinde 🙉", lambda: widget("<div>soru 🙉</div>"), ["E03"], []),
        ("W01 button", lambda: widget("<button>x</button>"), ["W01"], []),
        ("W02 setInterval", lambda: widget("<script>setInterval(f,1)</script>"), ["W02"], []),
        ("W03 dış kütüphane", lambda: widget("<script src=\"https://x/y.js\"></script>"), ["W03"], []),
        ("W temiz widget", lambda: widget("<style>html,body{overflow:hidden}.w{-webkit-text-size-adjust:100%;text-size-adjust:100%;font-size:15px}</style><div role=\"button\" tabindex=\"0\">Dokun</div>"), [], ["W01", "W02", "W03", "W04", "W05", "W06", "W07"]),
        ("W06 küçük yazı", lambda: widget("<style>.a{font-size:11px}</style>"), ["W06"], []),
        ("Q iyi mini test", lambda: sor(Q_IYI, test_turu="mini"), [], ["Q01", "Q09", "Q10", "Q08"]),
        ("Q01 mini test 3 soru", lambda: sor(Q_IYI + [Q_IYI[0]], test_turu="mini"), ["Q01"], []),
        ("Q09 Türkçe yok", lambda: sor([["Which food has the lowest water activity?", ["Fresh milk", "Raw meat", "Honey", "Cooked rice"], 2, "Bal."]], test_turu="tam"), ["Q09"], []),
        ("Q09 ana metin Türkçe", lambda: sor([["Hangi gıdanın su aktivitesi en düşüktür ve neden böyledir? (Which food has the lowest water activity?)", ["Fresh milk (Taze süt)", "Raw meat (Çiğ et)", "Honey (Bal)", "Cooked rice (Pişmiş pirinç)"], 2, "Bal."]], test_turu="tam"), ["Q09"], []),
        ("Q09 sayı şıkları çeviri istemez", lambda: sor([["What is the water activity if p = 2.4 kPa and p0 = 3.0 kPa? (p = 2.4 kPa ve p0 = 3.0 kPa ise su aktivitesi kaçtır?)", ["0.80", "1.25", "0.60", "7.20"], 0, "Oran p/p0."]], test_turu="tam"), [], ["Q09"]),
        ("Q08 slayt numarası soruda", lambda: sor([["In Slide 5, which food has the lowest water activity? (Slayt 5'te hangi gıdanın su aktivitesi en düşüktür?)", ["Fresh milk (Taze süt)", "Raw meat (Çiğ et)", "Honey (Bal)", "Cooked rice (Pişmiş pirinç)"], 2, "Bal."]], test_turu="tam"), ["Q08"], []),
        ("Q08 konu adı soruda", lambda: sor(Q_IYI[:1], test_turu="tam", konu_adlari=["water activity"]), ["Q08"], []),
        ("Q08 konu adı açıklamada serbest", lambda: sor([["Which instrument measures humidity of air? (Havanın nemini hangi cihaz ölçer?)", ["Hygrometer (Higrometre)", "Colorimeter (Kolorimetre)", "Viscometer (Viskozimetre)", "Refractometer (Refraktometre)"], 0, "Konu: water activity. Higrometre nemi ölçer."]], test_turu="tam", konu_adlari=["water activity"]), [], ["Q08"]),
        ("Q10 cevap hep aynı şıkta", lambda: sor([_s(i, 0) for i in range(6)], {"test_dil": None}, test_turu="tam"), ["Q10"], []),
        ("Q10 dağınık cevap geçer", lambda: sor(dagit, {"test_dil": None}, test_turu="tam"), [], ["Q10"]),
        ("Q04/Q05 aynı şık ve soru", lambda: sor([[Q_IYI[0][0], ["Honey (Bal)", "Honey (Bal)", "Raw meat (Çiğ et)", "Cooked rice (Pişmiş pirinç)"], 2, "Bal."], Q_IYI[1], Q_IYI[1]], test_turu="tam"), ["Q04", "Q05"], []),
        ("Q06/Q03 boş açıklama, dışarıda cevap", lambda: sor([[Q_IYI[0][0], Q_IYI[0][1], 2, ""], [Q_IYI[1][0], Q_IYI[1][1], 9, "x"]], test_turu="tam"), ["Q06", "Q03"], []),
        ("Q15 etiket yok", lambda: sor(Q_IYI, {"karisik_test": True}, test_turu="mini"), ["Q15"], []),
        ("Q15 mini hepsi aynı konu", lambda: sor([_et(Q_IYI[0], "Lipids"), _et(Q_IYI[1], "Lipids")], {"karisik_test": True}, test_turu="mini"), ["Q15"], []),
        ("Q15 mini hepsi güncel konu", lambda: sor([_et(Q_IYI[0], "Maillard reaction"), _et(Q_IYI[1], "Maillard reaction")], {"karisik_test": True}, test_turu="mini", konu_adlari=["Maillard reaction"]), ["Q15"], []),
        ("Q15 mini karışık geçer", lambda: sor([_et(Q_IYI[0], "Water activity"), _et(Q_IYI[1], "Maillard reaction")], {"karisik_test": True}, test_turu="mini", konu_adlari=["Maillard reaction"]), [], ["Q15", "Q08"]),
        ("Q12 W10 tam testte art arda aynı konu", lambda: sor([_s(i, i % 4) + ["", k] for i, k in ((1, "A konu"), (2, "A konu"), (3, "B konu"))], {"test_dil": None}, test_turu="tam"), ["Q12"], []),
        ("Q12 art arda aynı konu", lambda: dosya_bulgulari(".json", json.dumps({"baslik": "T", "karistir": "yok", "dil": "tek", "sorular": [
            {"no": i, "bolum": b, "soru": f"Which statement about topic number {i} is correct for this test?",
             "siklar": [{"metin": f"Statement {j} about topic {i}", "neden_yanlis": "" if j == i % 4 else f"Neden {j}"} for j in range(4)], "dogru": "ABCD"[i % 4], "aciklama": ["Açıklama."]}
            for i, b in ((1, "Water activity"), (2, "Water activity"), (3, "Lipids"))]}), {"test_dil": None}, None, test_turu="tam"), ["Q12"], []),
    ]


def kendini_dene():
    """Ek kuralların yanlış ve doğru örnekleri + depodaki şablonlar. -> başarısız sayısı"""
    kotu = 0
    for ad, f, olmali, olmamali in _denemeler():
        kodlar = {x[1] for x in f()}
        sorun = [k for k in olmali if k not in kodlar] + [f"fazladan {k}" for k in olmamali if k in kodlar]
        if sorun:
            kotu += 1
            print(f"BAŞARISIZ · {ad}: {', '.join(sorun)}")
        else:
            print(f"geçti · {ad}")
    import glob
    yollar = sorted(glob.glob(os.path.join(KOK, "gorsel", "sablonlar", "*.html")) + glob.glob(os.path.join(KOK, "alanlar", "*", "sablonlar", "*.html")))
    hatali = []
    for y in yollar:
        h = [x for x in dosya_bulgulari(".html", open(y, encoding="utf-8").read(), {}) if x[0] == H]
        if h:
            hatali.append((os.path.basename(y), h[0]))
    if hatali or len(yollar) < 20:
        kotu += 1
        print(f"BAŞARISIZ · şablonlar kendi denetiminden geçmiyor: {hatali[:3]} ({len(yollar)} şablon)")
    else:
        print(f"geçti · {len(yollar)} widget şablonu HATA'sız")
    try:
        import soru_testi
        d = json.load(open(os.path.join(KOK, "gorsel", "soru-testi", "ornek.json"), encoding="utf-8"))
        h = [x for x in dosya_bulgulari(".json", json.dumps(d), {}) if x[0] == H]
        if h:
            kotu += 1
            print("BAŞARISIZ · ornek.json HATA veriyor:", h[:2])
        else:
            print("geçti · W24 örnek verisi HATA'sız")
    except OSError:
        pass
    return kotu
