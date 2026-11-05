#!/usr/bin/env python3
"""Widget üretici: model HTML yazmaz, kısa bir JSON spec yazar; HTML bu araçtan çıkar.

Kullanım:
  python3 araclar/widget.py spec.json cikti.html            spec -> tek parça widget HTML'i (sohbette show_widget'a verilir)
  ... --tema yol.json | ad        tema dosyası (varsayılan: profildeki "tema" -> gorsel/motor/tema-varsayilan.json, üstüne yerel/tema.json)
  ... --yuk cikti.yuk.json        yayın yükü: {"title", "widget_code"} (ensure_ascii=False; sohbete BİREBİR yapıştırılır)
  ... --test [--goruntu klasor]   Playwright (node): 390 ve 900 px, açık/koyu, her sekme, doğru/yanlış durumlar; JS hatası, 13 px altı yazı,
                                  44 px altı dokunma hedefi, yatay taşma raporlanır; çıkış kodu 1 = sorun var
  ... --karsilastir eski.html     aynı eylem dizisiyle iki widget'ın ekran görüntülerini piksel farkıyla karşılaştırır (PIL gerekir)
  python3 araclar/widget.py --ornek                         örnek spec basar
  python3 araclar/widget.py --kendini-dene

Spec biçimi ve bileşenler: gorsel/motor/README.md. Görünüm gorsel/motor/neo.css + engine.js'ten, renk temadan gelir; bu dosya yalnız birleştirir.
Metinler HTML olarak kaçışlanır (`<` `&` düz yazılır); yalnız <b>…</b> ve <br> serbesttir. `ham` bileşeni kaçışsız HTML/JS alır.
"""
import ast, html as _html, json, os, re, subprocess, sys, tempfile

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(BURASI)
MOTOR = os.path.join(KOK, "gorsel", "motor")
SINIF = {"k1", "k2", "k3", "k4", "k5", "k6", "rd"}
TUR = {"etiket", "not", "formul", "secici", "kartlar", "cubuklar", "siniflama", "tablo", "zincir", "kaydirici", "svg", "ham", "test"}
CK = '<svg class="ic ck" viewBox="0 0 24 24"><path d="M5 12l5 5l10 -10"/></svg>'


class SpecHatasi(Exception):
    pass


# ───────────────────────────── yardımcılar ─────────────────────────────
def m(s):
    """Düz metin -> HTML (kaçışlı); yalnız <b></b> ve <br> serbest."""
    s = nbsp_esit(_html.escape(str(s), quote=False))
    return s.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>").replace("&lt;br&gt;", "<br>")


def a(s):
    return _html.escape(str(s), quote=True)


def mj(o):
    """Veriyi JS'e gömmek için: metinler HTML kaçışlı, JSON UTF-8 (\\u kaçışı yok), </script> güvenli."""
    def k(x):
        if isinstance(x, str):
            return m(x)
        if isinstance(x, list):
            return [k(i) for i in x]
        if isinstance(x, dict):
            return {kk: k(v) for kk, v in x.items()}
        return x
    return js(k(o))


def js(o):
    s = json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def kebap(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def renk(v, yol, varsayilan="k1"):
    v = v or varsayilan
    if v not in SINIF:
        raise SpecHatasi(f"{yol}: renk '{v}' geçersiz (izinli: {', '.join(sorted(SINIF))})")
    return v


def gerekli(d, anahtarlar, yol):
    for k in anahtarlar:
        if k not in d:
            raise SpecHatasi(f"{yol}: '{k}' yok")


def nbsp_esit(s):
    """'Q = 10' gibi kısa ifadelerde satır sonu kırılmasın."""
    return re.sub(r"(?<=\w) = (?=\w)", "\u00a0=\u00a0", s)


def ifade_degeri(expr, u):
    """Güvenli aritmetik ifade (yalnız u, sayılar, + - * / ** ve parantez)."""
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name) and n.id == "u":
            return u
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            return -ev(n.operand) if isinstance(n.op, ast.USub) else ev(n.operand)
        if isinstance(n, ast.BinOp):
            x, y = ev(n.left), ev(n.right)
            op = type(n.op)
            if op is ast.Add: return x + y
            if op is ast.Sub: return x - y
            if op is ast.Mult: return x * y
            if op is ast.Div: return x / y
            if op is ast.Pow: return x ** y
        raise SpecHatasi(f"ifade desteklenmiyor: {expr}")
    return ev(ast.parse(expr, mode="eval"))


# ───────────────────────────── bileşenler: (html, js) ─────────────────────────────
class Baglam:
    def __init__(self, pi):
        self.pi, self.n = pi, 0
        self.test = None

    def yeni(self, onek):
        self.n += 1
        return f"{onek}{self.pi}{self.n}"


def b_etiket(d, c, yol):
    gerekli(d, ["metin"], yol)
    k = renk(d["renk"], yol) if d.get("renk") else ""
    return '<div class="lb"><span class="sk%s">%s</span></div>' % (" " + k if k else "", m(d["metin"])), ""


def b_not(d, c, yol):
    if "metin" in d:
        return f'<div class="nt">{m(d["metin"])}</div>', ""
    gerekli(d, ["yap", "gor"], yol)
    return f'<div class="nt">Ne yapacaksın: {m(d["yap"])} Ne göreceksin: {m(d["gor"])}</div>', ""


def b_formul(d, c, yol):
    gerekli(d, ["ogeler"], yol)
    h, kol = '<div class="eq"', []
    govde = ""
    for i, o in enumerate(d["ogeler"]):
        if isinstance(o, str):
            govde += f'<div class="op">{m(o)}</div>'
            kol.append("auto")
        else:
            gerekli(o, ["kod"], f"{yol}.ogeler[{i}]")
            k = renk(o.get("renk"), f"{yol}.ogeler[{i}]", "k1")
            govde += f'<div class="nd bx {k}"><b>{m(o["kod"])}</b>' + "".join(f"<span>{m(o[x])}</span>" for x in ("en", "tr") if o.get(x)) + "</div>"
            kol.append("1fr")
    if kol != ["1fr", "auto", "1fr", "auto", "1fr"]:
        h += f' style="grid-template-columns:{" ".join(kol)}"'
    return h + ">" + govde + "</div>", ""


def b_secici(d, c, yol):
    gerekli(d, ["secenekler", "cubuklar", "eksen"], yol)
    g = c.yeni("s")
    mx, onek = d["eksen"][1], d.get("onek", "")
    ids = [x["id"] for x in d["cubuklar"]]
    h = f'<div class="lb"><span class="sk">{m(d["baslik"])}</span></div>' if d.get("baslik") else ""
    h += f'<div class="cps {"c3" if len(d["secenekler"]) == 3 else "c2"}">'
    for i, o in enumerate(d["secenekler"]):
        gerekli(o, ["etiket", "degerler", "sonuc"], f"{yol}.secenekler[{i}]")
        h += (f'<div role="button" tabindex="0" class="cp big {renk(d.get("secici_renk"), yol, "k4")}{" on" if i == 0 else ""}" '
              f'data-act="sc" data-g="{g}" data-n="{i}" data-sg="{g}">{CK}{m(o["etiket"])}</div>')
    h += '</div><div style="margin-top:18px">'
    for x in d["cubuklar"]:
        gerekli(x, ["id", "ad"], f"{yol}.cubuklar")
        k = renk(x.get("renk"), yol)
        h += (f'<div class="br"><div class="nm {k}">{m(x["ad"])}</div><div class="tr"><i class="{k}" data-b="{g}{a(x["id"])}"></i></div>'
              f'<div class="vl" data-v="{g}{a(x["id"])}"></div></div>')
    h += f'<div class="sc0"><span>{m(onek)}{d["eksen"][0]}</span><span>{m(onek)}{mx}</span></div></div>'
    h += f'<div class="rs bx {renk(d.get("sonuc_renk"), yol, "k1")}" data-r="{g}"></div>'
    veri = {"mx": mx, "p": onek, "b": ids, "o": [{"v": o["degerler"], "r": o["sonuc"]} for o in d["secenekler"]]}
    return h, f'SC[{js(g)}]={mj(veri)};scset({js(g)},0);'


def b_kartlar(d, c, yol):
    gerekli(d, ["ogeler"], yol)
    g = c.yeni("r")
    kol = d.get("kolon", 3)
    h = f'<div class="cps c{kol}">'
    veri = []
    for i, o in enumerate(d["ogeler"]):
        gerekli(o, ["etiket", "baslik"], f"{yol}.ogeler[{i}]")
        k = renk(o.get("renk"), f"{yol}.ogeler[{i}]")
        sub = f'<small>{m(o["alt"])}</small>' if o.get("alt") else ""
        h += f'<div role="button" tabindex="0" class="cp {k}{" on" if i == 0 else ""}" data-act="rv" data-g="{g}" data-n="{i}">{m(o["etiket"])}{sub}</div>'
        veri.append([k, o.get("sk", ""), o["baslik"], o.get("metin", "")])
    h += f'</div><div class="st bx" data-st="{g}"></div>'
    return h, f'RV[{js(g)}]={mj(veri)};rvset({js(g)},0);'


def b_cubuklar(d, c, yol):
    gerekli(d, ["satirlar", "mx"], yol)
    g = c.yeni("r")
    mx, tikla, genis = d["mx"], bool(d.get("tikla")), bool(d.get("genis", d.get("tikla")))
    h, veri = "", []
    for i, r in enumerate(d["satirlar"]):
        gerekli(r, ["ad", "deger"], f"{yol}.satirlar[{i}]")
        k = renk(r.get("renk"), f"{yol}.satirlar[{i}]", "k6")
        sub = f'<small>{m(r["alt"])}</small>' if r.get("alt") else ""
        w = round(r["deger"] / mx * 100, 1)
        etiket = m(r.get("etiket", r["deger"]))
        govde = (f'<div class="nm {k}">{m(r["ad"])}{sub}</div><div class="tr"><i class="{k}" style="width:{w}%{";border-right-width:0" if r["deger"] == 0 else ""}"></i></div>'
                 f'<div class="vl">{etiket}</div>')
        if tikla:
            h += f'<div role="button" tabindex="0" class="br w2{" on" if i == 0 else ""}" data-act="rv" data-g="{g}" data-n="{i}">{govde}</div>'
            ay = r.get("ayrinti", {})
            veri.append([renk(ay.get("renk"), yol, "k1"), ay.get("sk", ""), ay.get("baslik", r["ad"]), ay.get("metin", "")])
        else:
            h += f'<div class="br{" w" if genis else ""}">{govde}</div>'
    if d.get("eksen"):
        h += '<div class="ax">' + "".join(f'<span style="left:{round(x / mx * 100, 2)}%">{m(t)}</span>' for x, t in d["eksen"]) + "</div>"
    if tikla:
        h += f'<div class="st bx" data-st="{g}"></div>'
        return h, f'RV[{js(g)}]={mj(veri)};rvset({js(g)},0);'
    return h, ""


def b_siniflama(d, c, yol):
    gerekli(d, ["secenekler", "ogeler"], yol)
    g = c.yeni("o")
    sec = d["secenekler"]
    h = f'<div class="lb"><span class="sk k1">{m(d["baslik"])}</span></div>' if d.get("baslik") else ""
    h += f'<div data-sort="{g}">'
    for i, it in enumerate(d["ogeler"]):
        if len(it) < 4 or not (isinstance(it[2], int) and 0 <= it[2] < len(sec)):
            raise SpecHatasi(f"{yol}.ogeler[{i}]: [İngilizce, Türkçe, doğru seçenek no (0-{len(sec) - 1}), açıklama] olmalı")
        h += f'<div class="it bx" data-i="{i}"><div class="en">{m(it[0])}</div>' + (f'<div class="trs">{m(it[1])}</div>' if it[1] else "")
        h += f'<div class="cps c{len(sec)}">'
        for v, s in enumerate(sec):
            h += f'<div role="button" tabindex="0" class="cp {renk(s[2], yol)}" data-act="srt" data-v="{v}">{m(s[0])}<small>{m(s[1])}</small></div>'
        h += '</div><div class="fb"></div></div>'
    h += '<div class="sc bx k1"></div></div>'
    return h, f'initSort(q1("[data-sort=\\"{g}\\"]"),{mj(d["ogeler"])},TABIDX);'


def b_tablo(d, c, yol):
    gerekli(d, ["baslik", "satirlar"], yol)
    h = '<div class="tw"><table class="tt"><tr>'
    for x in d["baslik"]:
        t, k = (x if isinstance(x, list) else [x, ""])
        h += f'<th{" class=" + chr(34) + renk(k, yol) + chr(34) if k else ""}>{m(t)}</th>'
    h += "</tr>"
    for r in d["satirlar"]:
        h += "<tr>"
        for x in r:
            t, k = (x if isinstance(x, list) else [x, ""])
            h += f'<td{" class=" + chr(34) + renk(k, yol) + chr(34) if k else ""}>{m(t)}</td>'
        h += "</tr>"
    return h + "</table></div>", ""


def b_zincir(d, c, yol):
    gerekli(d, ["dugumler"], yol)

    def dugum(n, i):
        t, alt, k = (n["metin"], n.get("alt", ""), renk(n.get("renk"), f"{yol}.dugumler[{i}]")) if isinstance(n, dict) else (n, "", "k1")
        return f'<div class="nd bx {k}"><div><b>{m(t)}</b>{"<span>" + m(alt) + "</span>" if alt else ""}</div></div>'
    h = '<div class="fl">' + '<div class="ar"></div>'.join(dugum(n, i) for i, n in enumerate(d["dugumler"])) + ("<div class=\"ar\"></div>" if d.get("kollar") else "") + "</div>"
    if d.get("kollar"):
        h += f'<div class="cps c{len(d["kollar"])}" style="margin-top:0">' + "".join(dugum(n, i) for i, n in enumerate(d["kollar"])) + "</div>"
    return h, ""


def b_kaydirici(d, c, yol):
    gerekli(d, ["on_ayarlar", "durumlar"], yol)
    g = c.yeni("k")
    dur = d["durumlar"]
    for i, e in enumerate(dur):
        gerekli(e, ["alt", "renk", "sk", "baslik"], f"{yol}.durumlar[{i}]")
        renk(e["renk"], f"{yol}.durumlar[{i}]")
    h = f'<div class="lb"><span class="sk k1">{m(d["baslik"])}</span></div>' if d.get("baslik") else ""
    h += '<div class="pr">'
    for o in d["on_ayarlar"]:
        sub = f'<small>{m(o["alt"])}</small>' if o.get("alt") else ""
        h += f'<div role="button" tabindex="0" class="cp {renk(o.get("renk"), yol)}" data-act="pg" data-pg="{g}" data-s="{o["deger"]}">{m(o["etiket"])}{sub}</div>'
    h += f'</div><input class="sl" type="range" min="0" max="100" step="1" value="{d.get("baslangic", 0)}" data-sl="{g}" aria-label="{a(d.get("aria", d.get("baslik", "kaydırıcı")))}">'
    if d.get("ek_html"):
        h += d["ek_html"]
    h += f'<div class="st bx" data-st="{g}"></div>'
    veri = {"s": [[e["alt"], e["renk"], e["sk"], e["baslik"], e.get("metin", "")] for e in dur]}
    gr = d.get("grafik")
    if gr:
        if gr.get("baslik"):
            h += f'<div class="lb"><span class="sk">{m(gr["baslik"])}</span></div>'
        h += '<div class="gr bx">' + gr["svg"].replace("data-dot", f'data-dot="{g}"') + "</div>"
        veri["x"] = gr["x"]
        veri["y"] = [round(ifade_degeri(gr["y"], s / 100), 1) for s in range(101)]
    js_ = f'KD[{js(g)}]={mj(veri)[:-1]}' + (f',"f":{d["ek_js"]}' if d.get("ek_js") else "") + "};"
    return h, js_ + f'kdset({js(g)},{d.get("baslangic", 0)});'


def b_svg(d, c, yol):
    gerekli(d, ["svg"], yol)
    return f'<div class="gr bx">{d["svg"]}</div>', ""


def b_ham(d, c, yol):
    return d.get("html", ""), d.get("js", "")


def b_test(d, c, yol):
    gerekli(d, ["sorular"], yol)
    for i, q in enumerate(d["sorular"]):
        if not (isinstance(q, list) and len(q) >= 4 and isinstance(q[1], list) and len(q[1]) >= 2 and isinstance(q[2], int) and 0 <= q[2] < len(q[1])):
            raise SpecHatasi(f"{yol}.sorular[{i}]: [soru, [şıklar], doğru şık no, açıklama, ipucu, konu etiketi] olmalı")
    c.test = d["sorular"]
    return "", "TEST"


BILESEN = {"etiket": b_etiket, "not": b_not, "formul": b_formul, "secici": b_secici, "kartlar": b_kartlar, "cubuklar": b_cubuklar,
           "siniflama": b_siniflama, "tablo": b_tablo, "zincir": b_zincir, "kaydirici": b_kaydirici, "svg": b_svg, "ham": b_ham, "test": b_test}
ENGINE_BLOK = {"sort": "siniflama", "test": "test", "rv": ("kartlar", "cubuklar"), "secici": "secici", "kaydirici": "kaydirici"}


# ───────────────────────────── tema ve birleştirme ─────────────────────────────
def tema_oku(tema=None, profil_kok="/mnt/project-files"):
    """Tema sözlüğü: depo varsayılanı < yerel/tema.json (kişisel, kısmi olabilir) < --tema dosyası."""
    t = json.load(open(os.path.join(MOTOR, "tema-varsayilan.json"), encoding="utf-8"))
    yollar = [os.path.join(profil_kok, "yerel", "tema.json")] if not tema or tema == "neobrutalism" else []
    if tema and tema != "neobrutalism":
        yollar.append(tema if os.path.isfile(tema) else os.path.join(MOTOR, f"tema-{tema}.json"))
    for y in yollar:
        if os.path.isfile(y):
            ust = json.load(open(y, encoding="utf-8"))
            for k in ("acik", "koyu", "roller"):
                t.setdefault(k, {}).update(ust.get(k, {}))
    bilinmeyen = [k for k in t["acik"] if k not in {"bg", "sf", "tx", "tx2", "ln", "mn", "yl", "ik", "rd", "k1", "k2", "k3", "k4", "k5", "k6"}]
    if bilinmeyen:
        raise SpecHatasi(f"tema: bilinmeyen renk anahtarı {bilinmeyen}")
    for r, v in t["roller"].items():
        if v not in SINIF:
            raise SpecHatasi(f"tema: rol '{r}' geçersiz sınıf '{v}'")
    return t


def tema_blogu(t):
    acik = "".join(f"--{k}:{v};" for k, v in t["acik"].items())
    koyu = "".join(f"--{k}:{v};" for k, v in t.get("koyu", {}).items())
    return f".nb{{{acik}}}\n.nb.dk{{{koyu}}}\n"


def css_buda(css, kullanilan):
    """Kullanılmayan sınıf kurallarını atar (tek seviye @media dahil)."""
    def kurallar(s):
        res, derin, bas = [], 0, 0
        for j, ch in enumerate(s):
            if ch == "{":
                derin += 1
            elif ch == "}":
                derin -= 1
                if derin == 0:
                    res.append(s[bas:j + 1].strip())
                    bas = j + 1
        return res

    def tut(kural):
        sel = kural.split("{", 1)[0]
        if sel.strip().startswith("@media"):
            ic = kural[kural.index("{") + 1:kural.rindex("}")]
            kalan = [r for r in kurallar(ic) if tut(r)]
            return ("%s{%s}" % (sel.strip(), "".join(kalan))) if kalan else None
        for s in sel.split(","):
            sinif = [x for x in re.findall(r"\.([A-Za-z0-9_-]+)", s) if x != "nb"]
            if all(x in kullanilan for x in sinif):
                return kural
        return None
    return "\n".join(k for k in (tut(r) for r in kurallar(css)) if k)


def engine_kes(eng, kullanilan_bloklar):
    """/*@ad*/ ... /*@/ad*/ bloklarından kullanılmayanları atar; işaretleri ve boş satırları siler."""
    def degistir(mm):
        return mm.group(0) if mm.group(1) in kullanilan_bloklar else ""
    eng = re.sub(r"/\*@(\w+)\*/.*?/\*@/\1\*/\n?", degistir, eng, flags=re.S)
    eng = re.sub(r"/\*@/?\w+\*/\n?", "", eng)
    return "\n".join(l.strip() for l in eng.split("\n") if l.strip())


def olustur(spec, tema=None, profil_kok="/mnt/project-files"):
    """Spec sözlüğü -> widget HTML metni."""
    for k in ("id", "sekmeler", "paneller"):
        if k not in spec:
            raise SpecHatasi(f"spec: '{k}' yok")
    if len(spec["sekmeler"]) != len(spec["paneller"]):
        raise SpecHatasi(f"spec: {len(spec['sekmeler'])} sekme var ama {len(spec['paneller'])} panel var")
    wid = "nb-" + kebap(spec["id"])
    t = tema_oku(tema or spec.get("tema"), profil_kok)
    roller = t["roller"]
    govde = '<div class="tbs" role="tablist">' + "".join(
        f'<div role="button" tabindex="0" class="tb bx bt{" on" if i == 0 else ""}" data-act="tab" data-i="{i}"><span class="n">{i + 1}</span><span>{m(n)}</span></div>'
        for i, n in enumerate(spec["sekmeler"])) + "</div>"
    js_parca, kullanilan = [], set()
    for pi, panel in enumerate(spec["paneller"]):
        c = Baglam(pi)
        ph, testli = "", False
        for bi, d in enumerate(panel):
            yol = f"paneller[{pi}][{bi}]"
            tur = d.get("tur")
            if tur not in TUR:
                raise SpecHatasi(f"{yol}: bilinmeyen tür '{tur}' (izinli: {', '.join(sorted(TUR))})")
            if testli:
                raise SpecHatasi(f"{yol}: 'test' panelin son bileşeni olmalı (sonuna eklenir)")
            h, j = BILESEN[tur](d, c, yol)
            ph += h
            for blok, turler in ENGINE_BLOK.items():
                if tur in (turler if isinstance(turler, tuple) else (turler,)):
                    kullanilan.add(blok)
            if tur == "test":
                testli = True
            elif j:
                js_parca.append(j.replace("TABIDX", str(pi)))
        govde += '<div class="pn"%s>%s</div>' % ("" if pi == 0 else ' style="display:none"', ph)
        if c.test is not None:
            js_parca.append(f"var Q={mj(c.test)};initTest({pi},Q,{pi});")
    eng = open(os.path.join(MOTOR, "engine.js"), encoding="utf-8").read().replace("%ID%", wid)
    eng = engine_kes(eng, kullanilan)
    kod = "\n".join(js_parca) + "\nsel(0);"
    betik = eng + "\n" + kod
    sade = lambda s: s.replace("%DOGRU%", roller["dogru"]).replace("%YANLIS%", roller["yanlis"])
    betik = sade(betik)
    css = sade(open(os.path.join(MOTOR, "neo.css"), encoding="utf-8").read())
    kullanilan_sozler = set(re.findall(r"[A-Za-z0-9_-]+", govde + betik))
    css = css_buda(css, kullanilan_sozler)
    css = re.sub(r"\s*\n\s*", "", css).replace("; ", ";").replace(": ", ":").replace(";}", "}").replace(" {", "{")
    stil = re.sub(r"\n", "", tema_blogu(t)) + css
    return (f'<div class="nb" id="{wid}"><style>{stil}</style><i class="pb" style="color:var(--text-primary)"></i>{govde}'
            f'<script>(function(){{{betik}}})();</script></div>')


def yuk_yaz(html, baslik, yol):
    """Yayın yükü: post_widget'a BİREBİR yapıştırılacak JSON (ensure_ascii=False)."""
    with open(yol, "w", encoding="utf-8") as f:
        json.dump({"title": baslik, "widget_code": html}, f, ensure_ascii=False)
        f.write("\n")


# ───────────────────────────── test ve karşılaştırma (node + Playwright) ─────────────────────────────
def node_calistir(args):
    betik = os.path.join(BURASI, "widget_test.js")
    try:
        return subprocess.run(["node", betik] + args, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise SystemExit(f"ekran testi çalışmadı: {e} (node ve Playwright gerekir: require('playwright'))")


def ekran_testi(yol, goruntu=None):
    args = [yol] + (["--goruntu", goruntu] if goruntu else [])
    r = node_calistir(args)
    print(r.stdout.rstrip())
    if r.returncode not in (0, 1):
        print(r.stderr.rstrip(), file=sys.stderr)
        return 2
    return r.returncode


def karsilastir(yeni, eski, esik=0.0005):
    try:
        from PIL import Image, ImageChops
    except ImportError:
        raise SystemExit("--karsilastir için PIL gerekir (pip install pillow)")
    with tempfile.TemporaryDirectory() as d:
        ka, kb = os.path.join(d, "a"), os.path.join(d, "b")
        for yol, k in ((yeni, ka), (eski, kb)):
            r = node_calistir([yol, "--goruntu", k, "--yalniz-goruntu"])
            if r.returncode not in (0, 1):
                raise SystemExit(r.stderr)
        farkli = 0
        for ad in sorted(os.listdir(ka)):
            if not os.path.exists(os.path.join(kb, ad)):
                print(f"  yalnız yenide: {ad}")
                continue
            ia, ib = Image.open(os.path.join(ka, ad)).convert("RGB"), Image.open(os.path.join(kb, ad)).convert("RGB")
            if ia.size != ib.size:
                print(f"  BOYUT FARKLI {ad}: {ia.size} / {ib.size}")
                farkli += 1
                continue
            fark = ImageChops.difference(ia, ib).convert("L").point(lambda p: 255 if p > 24 else 0)
            oran = fark.tobytes().count(255) / (ia.size[0] * ia.size[1])
            isaret = "FARK" if oran > esik else "aynı"
            if oran > esik:
                farkli += 1
            print(f"  {isaret:4} {oran * 100:6.3f}%  {ad}")
        print(f"{farkli} durumda fark (eşik %{esik * 100:.2f})")
        return 1 if farkli else 0


# ───────────────────────────── örnek ve kendini deneme ─────────────────────────────
ORNEK = {
    "id": "ornek-adim",
    "sekmeler": ["Açıklama", "Alıştırma", "Mini test"],
    "paneller": [
        [{"tur": "etiket", "metin": "Bir karta bas", "renk": "k1"},
         {"tur": "kartlar", "kolon": 3, "ogeler": [
             {"etiket": "Calcium", "alt": "(Kalsiyum)", "renk": "k1", "sk": "Macro mineral", "baslik": "Calcium (Kalsiyum)", "metin": "Kemik ve diş yapısında bulunur."},
             {"etiket": "Iron", "alt": "(Demir)", "renk": "k6", "sk": "Micro mineral", "baslik": "Iron (Demir)", "metin": "Kanda oksijen taşınmasında görev alır."},
             {"etiket": "Sodium", "alt": "(Sodyum)", "renk": "k4", "sk": "Macro mineral", "baslik": "Sodium (Sodyum)", "metin": "Sıvı dengesinde rol oynar."}]},
         {"tur": "not", "yap": "Bir karta bas.", "gor": "Altında kartın açıklaması açılır."}],
        [{"tur": "siniflama", "baslik": "Hangi grup?", "secenekler": [["Macro", "(Makro)", "k1"], ["Micro", "(Mikro)", "k6"]],
          "ogeler": [["Calcium", "Kalsiyum", 0, "Günlük gereksinimi yüksektir."], ["Iron", "Demir", 1, "Günlük gereksinimi düşüktür."]]},
         {"tur": "not", "yap": "Her kartta bir gruba bas.", "gor": "Doğruysa yeşil, yanlışsa kırmızı olur ve nedeni yazar."}],
        [{"tur": "test", "sorular": [
            ["Which mineral is needed in the largest amount? (Hangi mineral en çok miktarda gerekir?)", ["Calcium (Kalsiyum)", "Iron (Demir)", "Zinc (Çinko)", "Iodine (İyot)"], 0, "Calcium (Kalsiyum) makro mineraldir.", "Makro ne demek?", "T1"],
            ["Which one is a micro mineral? (Hangisi mikro mineraldir?)", ["Sodium (Sodyum)", "Calcium (Kalsiyum)", "Iron (Demir)", "Potassium (Potasyum)"], 2, "Iron (Demir) iz miktarda gerekir.", "", "T2"]]}]],
}


def kendini_dene():
    sorun = []

    def dene(ad, kosul):
        print(("geçti" if kosul else "BAŞARISIZ") + " · " + ad)
        if not kosul:
            sorun.append(ad)

    def hata_verir(spec):
        try:
            olustur(spec, profil_kok="/yok")
            return False
        except SpecHatasi:
            return True
    h = olustur(ORNEK, profil_kok="/yok")
    dene("örnek spec widget üretir", h.startswith('<div class="nb" id="nb-ornek-adim">') and h.endswith("</div>"))
    dene("tek parça: dış stil/betik/button yok", "<button" not in h and "src=" not in h and "<link" not in h)
    dene("kullanılmayan motor blokları atılır (slider, secici yok)", "kdset" not in h and "scset" not in h)
    dene("renk temadan gelir: sabit hex yalnız tema bloğunda (#fff/#000 hariç)", set(re.findall(r"#[0-9a-fA-F]{3,6}\b", re.sub(r"\.nb\{[^}]*\}|\.nb\.dk\{[^}]*\}", "", h.split("</style>")[0]))) <= {"#fff", "#000"})
    dene("doğru/yanlış rolü: yanlış = rd", "'rd'" in h and ".nb .o.no{background:var(--rd)" in h)
    dene("soru verisi var Q= olarak (denetim aracı okur)", "var Q=[[" in h)
    dene("metin kaçışlanır", "&lt;" in olustur({**ORNEK, "paneller": [[{"tur": "not", "metin": "pH < pI & x"}], [], []]}, profil_kok="/yok"))
    dene("<b> serbest", "<b>x</b>" in olustur({**ORNEK, "paneller": [[{"tur": "not", "metin": "<b>x</b>"}], [], []]}, profil_kok="/yok"))
    dene("</script> betiği bozmaz", "</script" not in mj(["a</script>b"]))
    dene("sekme/panel sayısı uyuşmazsa hata", hata_verir({**ORNEK, "sekmeler": ["a"]}))
    dene("bilinmeyen tür hata", hata_verir({**ORNEK, "paneller": [[{"tur": "uydur"}], [], []]}))
    dene("geçersiz renk hata", hata_verir({**ORNEK, "paneller": [[{"tur": "etiket", "metin": "x", "renk": "mor"}], [], []]}))
    dene("sınıflamada geçersiz doğru no hata", hata_verir({**ORNEK, "paneller": [[], [{"tur": "siniflama", "secenekler": [["a", "(a)", "k1"], ["b", "(b)", "k2"]], "ogeler": [["x", "y", 5, "z"]]}], []]}))
    dene("test panelin sonunda değilse hata", hata_verir({**ORNEK, "paneller": [[], [], [{"tur": "test", "sorular": ORNEK["paneller"][2][0]["sorular"]}, {"tur": "not", "metin": "x"}]]}))
    dene("ifade değeri güvenli", abs(ifade_degeri("140-420*(u-0.5)**2", 0.5) - 140) < 1e-9)
    try:
        ifade_degeri("__import__('os')", 0)
        dene("güvensiz ifade reddedilir", False)
    except (SpecHatasi, SyntaxError):
        dene("güvensiz ifade reddedilir", True)
    import shutil
    if shutil.which("node"):
        with tempfile.TemporaryDirectory() as d:
            iyi, kotu = os.path.join(d, "iyi.html"), os.path.join(d, "kotu.html")
            open(iyi, "w", encoding="utf-8").write(h)
            open(kotu, "w", encoding="utf-8").write(h.replace('<div class="nt">', '<div class="nt" style="font-size:11px">').replace("sel(0);", "sel(0);yok();"))
            ri, rk = node_calistir([iyi]), node_calistir([kotu])
            if ri.returncode == 2 or rk.returncode == 2:
                print("atlandı · ekran testi (Playwright bulunamadı)")
            else:
                dene("ekran testi: örnek widget geçer", ri.returncode == 0)
                dene("ekran testi: JS hatası ve küçük yazı yakalanır", rk.returncode == 1 and "JS hatası" in rk.stdout and "13 px altı yazı" in rk.stdout)
    else:
        print("atlandı · ekran testi (node yok)")
    t = tema_oku(None, "/yok")
    dene("tema: roller ve renkler tam", set(t["roller"]) == {"dogru", "yanlis", "dikkat"} and {"k1", "k6", "rd"} <= set(t["acik"]))
    print("KENDİNİ DENEME " + ("GEÇTİ" if not sorun else f"BAŞARISIZ ({len(sorun)})"))
    return 1 if sorun else 0


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?")
    ap.add_argument("cikti", nargs="?")
    ap.add_argument("--tema")
    ap.add_argument("--yuk")
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--goruntu")
    ap.add_argument("--karsilastir")
    ap.add_argument("--ornek", action="store_true")
    ap.add_argument("--kendini-dene", action="store_true")
    ap.add_argument("--proje", default="/mnt/project-files", help="proje klasörü (yerel/tema.json buradan okunur)")
    x = ap.parse_args()
    if x.kendini_dene:
        sys.exit(kendini_dene())
    if x.ornek:
        print(json.dumps(ORNEK, ensure_ascii=False, indent=1))
        return
    if not x.spec:
        ap.print_usage(sys.stderr)
        sys.exit(2)
    try:
        spec = json.load(open(x.spec, encoding="utf-8"))
        tema = x.tema
        if not tema:
            sys.path.insert(0, BURASI)
            import profil
            p = profil.oku(profil.bul())
            tema = p.get("tema")
        if tema == "karma":
            sys.exit("profilde tema 'karma': bu tema eski W25/W10 şablonlarıyla çalışır (gorsel/katalog.md); widget.py Neobrutalism motorudur")
        html = olustur(spec, tema, x.proje)
    except SpecHatasi as e:
        print(f"SPEC HATASI: {e}", file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError) as e:
        print(f"spec okunamadı: {e}", file=sys.stderr)
        sys.exit(2)
    cikti = x.cikti or os.path.splitext(x.spec)[0] + ".html"
    open(cikti, "w", encoding="utf-8").write(html)
    print(f"{cikti}: {len(html.encode('utf-8')) / 1024:.1f} KB")
    if x.yuk:
        yuk_yaz(html, spec["id"], x.yuk)
        print(f"{x.yuk}: yayın yükü")
    kod = 0
    if x.test:
        kod = ekran_testi(cikti, x.goruntu)
    if x.karsilastir:
        kod = max(kod, karsilastir(cikti, x.karsilastir))
    sys.exit(kod)


if __name__ == "__main__":
    main()
