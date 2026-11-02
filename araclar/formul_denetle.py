#!/usr/bin/env python3
"""Sohbet mesajındaki formülleri claude-sorunlari/formuller.md kurallarına göre denetler.

Kullanım:
  python3 araclar/formul_denetle.py mesaj.md        # dosya
  python3 araclar/formul_denetle.py - < mesaj.md    # stdin
  python3 araclar/formul_denetle.py --test          # kendi testleri
Çıkış kodu: 0 temiz (uyarı olabilir), 1 hata var. Hata varsa mesaj GÖNDERİLMEZ; düzeltilip yeniden denetlenir.
Fence kod blokları (```) ve `satır içi kod` atlanır.
"""
import re, sys

YASAK = re.compile(r"\\(Large|LARGE|large|huge|Huge|boldsymbol|mathbf|bf|boxed|color|textcolor|displaystyle|qquad|quad|left|right)\b")
KESIR = re.compile(r"\\(?:dfrac|tfrac|frac)(?![a-zA-Z])")
LISTE = re.compile(r"^\s*(?:>\s*)*(?:[-*+]\s|\d+[.)]\s|\|)")
BOSLUK = re.compile(r"\\[,;!:]")
DENKLEM_ORTAMI = re.compile(r"\\begin\{(aligned|align\*?|gather\*?|split|eqnarray\*?|multline\*?)\}")
KORUNAN = re.compile(r"\\begin\{(p|b|B|v|V)?matrix\}.*?\\end\{(p|b|B|v|V)?matrix\}|\\begin\{cases\}.*?\\end\{cases\}", re.S)


def grup_sonu(s, i):
    """s[i] == '{' ise eşleşen '}' konumunu döndürür (yoksa -1)."""
    d = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0:
                return j
    return -1


def kesir_tara(s, ic=False, hatalar=None):
    """İç içe kesir ve kesirden sonra \\times arar. hatalar: liste (mesaj)."""
    for m in KESIR.finditer(s):
        i = m.end()
        while i < len(s) and s[i] == " ":
            i += 1
        if i >= len(s) or s[i] != "{":
            continue
        a = grup_sonu(s, i)
        if a < 0:
            continue
        j = a + 1
        while j < len(s) and s[j] == " ":
            j += 1
        if j >= len(s) or s[j] != "{":
            continue
        b = grup_sonu(s, j)
        if b < 0:
            continue
        ic_metin = s[i + 1:a] + " " + s[j + 1:b]
        if KESIR.search(ic_metin):
            hatalar.append("kesrin içinde kesir var: ara değeri ayrı blokta tanımla")
            return
        k = b + 1
        while k < len(s) and s[k] == " ":
            k += 1
        if s[k:k + 6] == "\\times":
            hatalar.append("kesirden sonra \\times var: çarpanı payın içine al")
            return


def kod_temizle(satirlar):
    """Fence bloklarını ve satır içi kodu boşlukla değiştirir (satır numaraları korunur)."""
    out, kod = [], False
    for l in satirlar:
        if l.lstrip().startswith("```"):
            kod = not kod
            out.append("")
            continue
        out.append("" if kod else re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), l))
    return out


def denetle(metin):
    """-> (hatalar, uyarilar); her biri [(satir, mesaj)]."""
    H, U = [], []
    satirlar = kod_temizle(metin.split("\n"))
    t = "\n".join(satirlar)
    # satır başlangıç konumları
    bas = [0]
    for l in satirlar:
        bas.append(bas[-1] + len(l) + 1)

    def satir_no(pos):
        lo, hi = 0, len(bas) - 1
        while lo < hi - 1:
            mid = (lo + hi) // 2
            if bas[mid] <= pos:
                lo = mid
            else:
                hi = mid
        return lo + 1

    i, n = 0, len(t)
    spans = []  # (tür, içerik, başlangıç, bitiş)
    while i < n:
        c = t[i]
        if c == "\\" and t[i:i + 2] == "\\$":
            H.append((satir_no(i), "`\\$` yazılmaz: para birimini kelimeyle yaz (\"50 dolar\")"))
            i += 2
        elif c == "\\":
            i += 2
        elif t.startswith("$$", i):
            j = t.find("$$", i + 2)
            if j < 0:
                H.append((satir_no(i), "kapanmayan $$ bloğu"))
                break
            spans.append(("blok", t[i + 2:j], i, j + 2))
            i = j + 2
        elif c == "$":
            e = t.find("\n", i)
            e = n if e < 0 else e
            j = i + 1
            while j < e and not (t[j] == "$" and t[j - 1] != "\\"):
                j += 1
            if j >= e:
                H.append((satir_no(i), "eşleşmeyen tek `$`: para birimi için `$` yazma, formülü kapat"))
                i += 1
            else:
                spans.append(("satir", t[i + 1:j], i, j + 1))
                i = j + 1
        else:
            i += 1

    for tur, ic, a, b in spans:
        ln = satir_no(a)
        if tur == "satir" and not ic.strip():
            H.append((ln, "boş `$ $` formülü (para `$` işareti olabilir)"))
            continue
        for m in YASAK.finditer(ic):
            H.append((ln, f"`\\{m.group(1)}` sohbette ham görünür: kullanma"))
        for m in re.finditer(r"[_^](?!\{)", ic):
            H.append((ln, "alt indis/üs süslü parantezsiz (`P_{X}`, `E^{d}` yaz)"))
            break
        hs = []
        kesir_tara(ic, hatalar=hs)
        H.extend((ln, h) for h in hs)
        if BOSLUK.search(ic):
            U.append((ln, "`\\,` `\\;` `\\!` teyit edilmedi: bitişik yaz ya da `\\cdot` kullan"))
        satir_metni = satirlar[ln - 1]
        if tur == "blok":
            govde = KORUNAN.sub("", ic)
            if DENKLEM_ORTAMI.search(ic) or "\\\\" in govde:
                H.append((ln, "bir `$$` bloğunda tek denklem: her denklemi ayrı blok yap"))
            son = satir_no(b - 1)
            ilk_satir = satirlar[ln - 1].strip()
            son_satir = satirlar[son - 1].strip()
            if not ilk_satir.startswith("$$") or not son_satir.endswith("$$"):
                H.append((ln, "`$$` bloğu kendi satırında olmalı (öncesinde/sonrasında metin yok)"))
            if ln > 1 and satirlar[ln - 2].strip() != "":
                H.append((ln, "`$$` bloğunun üstünde boş satır olmalı"))
            if son < len(satirlar) and satirlar[son].strip() != "":
                H.append((son, "`$$` bloğunun altında boş satır olmalı"))
            if LISTE.match(satir_metni):
                H.append((ln, "liste/tablo satırının içinde `$$` bloğu olmaz: listeyi böl, bloğu ayrı yaz"))
        else:
            if LISTE.match(satir_metni):
                H.append((ln, "liste/tablo satırında satır içi `$...$` ham görünür: düz metin yaz (dt, Δt, x²) ya da listeyi böl, formülü ayrı `$$` bloğuna koy"))
            sade = re.sub(r"\\text\{[^}]*\}", "", ic)
            sade = re.sub(r"\\[a-zA-Z]+", "", sade)
            if re.search(r"[A-Za-zÇĞİÖŞÜçğıöşü]{4,}\s+[A-Za-zÇĞİÖŞÜçğıöşü]{3,}", sade) or re.search(r"[çğıöşüÇĞİÖŞÜ]", sade) or re.search(r"\d\s+[A-Za-z]{2,}", sade):
                H.append((ln, "satır içi formülde düz yazı var (para `$` işareti olabilir): yazıyı `\\text{}` içine al ya da formülü kapat"))
            if re.match(r"\s*\d", ic):
                U.append((ln, "satır içi formül rakamla başlıyor: `${2}\\times 3$` yaz"))
        pre = t[max(0, a - 2):a]
        if pre.endswith("**") or t[b:b + 2] == "**":
            U.append((ln, "kalın metnin içine formül konmaz"))
        if t[b:b + 1] == "'" or t[b:b + 1] == "’":
            U.append((ln, "formülden hemen sonra kesme işareti getirme"))
    H.sort(key=lambda x: x[0])
    U.sort(key=lambda x: x[0])
    return H, U


def test():
    ok = lambda s: not denetle(s)[0]
    bad = lambda s: bool(denetle(s)[0])
    ornekler = [
        (ok, "Metin.\n\n$$a_{w} = \\dfrac{p}{p_{0}}$$\n\nSon."),
        (ok, "Satır içi $\\dfrac{E_{a}}{R}$ ve $x^{2}$ yazılır."),
        (ok, "$$\\begin{bmatrix} 1 & 2 \\\\ 3 & 4 \\end{bmatrix}$$"),
        (bad, "$$\\Large a_{w}$$"),
        (bad, "$$\\boldsymbol{a}$$"),
        (bad, "$$\\left( a \\right)$$"),
        (ok, "$$\\rightarrow$$"),
        (bad, "$P_X$ olur."),
        (bad, "$$E^d$$"),
        (bad, "$$\\dfrac{a}{\\dfrac{b}{c}}$$"),
        (bad, "$$\\dfrac{a}{b} \\times 100$$"),
        (ok, "$$\\dfrac{a \\times 100}{b}$$"),
        (bad, "- madde $dt$ parçalarına böl\n"),
        (bad, "1. $dt$ parçalarına böl.\n"),
        (bad, "| a | $x$ |\n|---|---|\n"),
        (ok, "- madde dt parçalarına böl\n"),
        (bad, "Fiyat 50 \\$ olur."),
        (bad, "Fiyat $50 olur."),
        (bad, "Fiyat $50 ile $60 arasında."),
        (bad, "$$a = b \\\\ c = d$$"),
        (bad, "$$\\begin{aligned} a &= b \\\\ c &= d \\end{aligned}$$"),
        (bad, "Metin $$a = b$$ devam."),
        (bad, "Metin\n$$a = b$$\n\nSon."),
        (ok, "```\n$$\\Large x$$ ve $P_X$ kod bloğunda\n```\n"),
        (ok, "Kod `\\Large` satır içi."),
    ]
    sorun = 0
    for f, s in ornekler:
        if not f(s):
            sorun += 1
            print("TEST HATASI:", f.__name__, repr(s), denetle(s))
    print(f"{len(ornekler) - sorun}/{len(ornekler)} test geçti")
    return 1 if sorun else 0


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--test":
        sys.exit(test())
    metin = sys.stdin.read() if sys.argv[1] == "-" else open(sys.argv[1], encoding="utf-8").read()
    H, U = denetle(metin)
    for ln, m in H:
        print(f"HATA  satır {ln}: {m}")
    for ln, m in U:
        print(f"UYARI satır {ln}: {m}")
    if H:
        print(f"\n{len(H)} hata: mesajı göndermeden düzelt ve yeniden denetle.")
        sys.exit(1)
    print("Formül denetimi temiz." + (f" ({len(U)} uyarı)" if U else ""))


if __name__ == "__main__":
    main()
