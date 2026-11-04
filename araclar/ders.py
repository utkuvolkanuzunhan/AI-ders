#!/usr/bin/env python3
"""Ders durumu ve adım akışı: modelin hafızada tuttuğu her şey dosyaya geçer.

Durum dosyası kullanıcının proje klasöründe durur (depoya GİRMEZ): dersler/<ders>/durum/<ad>.json, çıktılar durum/<ad>/NN.*.

  ders.py baslat --ders D --ad AD --kaynak K [--kod KOD] [--tempo J2] [--baslik "Sohbet başlığı"]
  ders.py konu-ekle T3 "Kalsiyum görevleri" [--sayfa 28-34] [--adim 3] --ders D --ad AD   etiket soruda görünmez, yalnız takip için
  ders.py sonraki          sıradaki adım, mini test için önerilen ESKİ konular, devir uyarısı
  ders.py adim NN taslak.md [widget.json|widget.html] [--konu "Adım başlığı"] [--ilk]
                           mesaj denetimi + widget üretimi (spec ise) + widget denetimi + karışık soru denetimi + sadakat denetimi;
                           çıktı NN.mesaj.md / NN.widget.html / NN.yuk.json; HATA varsa çıkış kodu 1 (gönderme)
  ders.py yayinlandi NN [--mesaj N]    sayaç +N (varsayılan 1), adım "gönderildi", sorulan konular kaydedilir
  ders.py dogrula [NN ...] [--oturum kayit.jsonl]   oturum kaydındaki post_widget/post_message ile çıktıyı karşılaştırır: AYNI / FARKLI + ilk farklı karakter
  ders.py kusur NN "Flüorür -> Florür"  açık kusur (devir notuna ve Ekstra'ya gider)
  ders.py not zayif|acik-soru|tercih "metin"   devir notuna girecek kayıt
  ders.py devir            devir notunu durumdan üretir; koordinatöre gidecek tek satırı basar
  ders.py rapor            konu sonu: anlatim_testi --rapor 2 satırı + ders yöneticisine ünite raporu taslağı
  ders.py goster           durum özeti
Ortak: --ders D --ad AD (ya da proje klasöründeki tek durum dosyası), --proje <klasör> (varsayılan AI_DERS_PROJE ya da /mnt/project-files).
"""
import argparse, difflib, glob, hashlib, json, os, re, subprocess, sys, tempfile, time

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)
import profil as PROFIL  # noqa: E402

H, U = "HATA", "UYARI"


def proje_kok(a=None):
    return a or os.environ.get("AI_DERS_PROJE") or "/mnt/project-files"


def durum_dir(proje, ders):
    return os.path.join(proje, "dersler", ders, "durum")


def durum_yolu(proje, ders, ad):
    return os.path.join(durum_dir(proje, ders), ad + ".json")


def bul(proje, ders, ad):
    """--ders/--ad verilmediyse proje klasöründeki TEK durum dosyasını bulur."""
    if ders and ad:
        return ders, ad
    adaylar = []
    for y in glob.glob(os.path.join(proje, "dersler", ders or "*", "durum", (ad or "*") + ".json")):
        adaylar.append(y)
    if len(adaylar) == 1:
        p = adaylar[0].split(os.sep)
        return p[-3], os.path.splitext(p[-1])[0]
    sys.exit("--ders ve --ad gerekli" + (f" ({len(adaylar)} durum dosyası bulundu)" if adaylar else " (durum dosyası yok; önce baslat)"))


def yukle(proje, ders, ad):
    y = durum_yolu(proje, ders, ad)
    if not os.path.isfile(y):
        sys.exit(f"durum dosyası yok: {y} (önce: ders.py baslat)")
    return json.load(open(y, encoding="utf-8"))


def kaydet(proje, durum):
    y = durum_yolu(proje, durum["ders"], durum["ad"])
    os.makedirs(os.path.dirname(y), exist_ok=True)
    gecici = y + ".tmp"
    with open(gecici, "w", encoding="utf-8") as f:
        json.dump(durum, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(gecici, y)


def cikti_dir(proje, durum):
    d = os.path.join(durum_dir(proje, durum["ders"]), durum["ad"])
    os.makedirs(d, exist_ok=True)
    return d


def adim_bul(durum, no, yeni=False):
    for s in durum["adimlar"]:
        if s["no"] == no:
            return s
    if not yeni:
        sys.exit(f"adım {no} durumda yok (önce: ders.py adim {no} ...)")
    s = {"no": no, "durum": "taslak"}
    durum["adimlar"].append(s)
    durum["adimlar"].sort(key=lambda x: x["no"])
    return s


def profil_ayar():
    return PROFIL.oku(PROFIL.bul())


# ───────────────────────────── sonraki adım ve konu önerisi ─────────────────────────────
def gonderilen_adimlar(durum):
    return [s for s in durum["adimlar"] if s.get("durum") == "gonderildi"]


def siradaki_adim(durum):
    g = gonderilen_adimlar(durum)
    return (max(s["no"] for s in g) + 1) if g else 1


def ana_etiket(durum, e):
    """Alt başlık etiketi (T1a, T1b) -> ana konu etiketi (T1). Tanımlı etiket aynen döner; ilk başlıkta eski konu yokken
    aynı konudan iki ayrı yönden sormak için alt başlık harfi kullanılır, ana etiket ders.py konu-ekle ile tanımlı olmalı."""
    if e in durum["konular"]:
        return e
    m = re.fullmatch(r"(.+?)([a-z])", e or "")
    return m.group(1) if m and m.group(1) in durum["konular"] else e


def sorulma_say(durum):
    """etiket -> (toplam kez, ESKİ konu olarak kaç kez, en son hangi adımda). Eski = sorulduğu adım konunun kendi adımından sonra."""
    say = {}
    for s in gonderilen_adimlar(durum):
        for e in (ana_etiket(durum, x) for x in s.get("sorulan", [])):
            n, eski, _ = say.get(e, (0, 0, 0))
            own = durum["konular"].get(e, {}).get("adim")
            say[e] = (n + 1, eski + (1 if own is not None and own != s["no"] else 0), s["no"])
    return say


def eski_konu_onerisi(durum, adim_no, adet, guncel=None):
    """Bu adımın mini testi için önerilen eski konu etiketleri: önce eski konu olarak hiç sorulmamışlar, sonra en az sorulan ve en eski;
    bir önceki adımda sorulan konu başka seçenek varken tekrar önerilmez."""
    say = sorulma_say(durum)
    anlatildi = [e for e, k in durum["konular"].items() if k.get("adim") is not None and k["adim"] < adim_no and e != guncel]
    onceki = next((s for s in reversed(gonderilen_adimlar(durum)) if s["no"] < adim_no), None)
    onceki_eski = set(onceki.get("sorulan", [])) if onceki else set()
    sira = sorted(anlatildi, key=lambda e: (e in onceki_eski, say.get(e, (0, 0, 0))[1], say.get(e, (0, 0, 0))[0], say.get(e, (0, 0, 0))[2], e))
    return sira[:adet], say


def devir_uyarisi(durum, esik):
    sayac = durum.get("mesaj_sayaci", 0)
    sonraki_mesaj = sayac + 1
    kalan = esik - sonraki_mesaj
    if sayac >= esik:
        return f"DEVRET: {sayac} mesaj gönderildi (eşik {esik}); adım bittiyse şimdi `ders.py devir`, koordinatöre tek satır, sohbeti kapat."
    if kalan in (1, 2):
        return f"Devir uyarısı (mesaj {sonraki_mesaj}): kullanıcıya tek satır yaz: \"{kalan} mesaj sonra yeni sohbete taşınıyoruz, kaldığın yer aynen taşınacak\"."
    if kalan == 0:
        return f"Bu {sonraki_mesaj}. mesaj: biter bitmez devret (`ders.py devir`); adım ortasında devretme."
    return ""


def cmd_sonraki(a, proje, durum, ayar):
    no = siradaki_adim(durum)
    n_soru = int(ayar.get("mini_test_soru", 2))
    guncel = next((e for e, k in durum["konular"].items() if k.get("adim") == no), None)
    print(f"Sıradaki: Adım {no}" + (f" · güncel konu etiketi: {guncel} ({durum['konular'][guncel]['ad']})" if guncel else " · bu adım için konu etiketi yok (ders.py konu-ekle)"))
    adet = max(n_soru - 1, 0)
    if adet:
        oner, say = eski_konu_onerisi(durum, no, adet, guncel)
        if oner:
            print(f"Mini test ({n_soru} soru): 1 güncel + {adet} eski konudan. Eski konu önerisi (eski konu olarak hiç sorulmamışlar önce):")
            for e in oner:
                n, eski, son = say.get(e, (0, 0, 0))
                print(f"  {e} · {durum['konular'][e]['ad']} · " + ("hiç sorulmadı" if not n else f"{n} kez soruldu (eski konu olarak {eski}), son Adım {son}"))
        else:
            print(f"Mini test ({n_soru} soru): henüz anlatılmış eski konu yok; güncel konudan ayrı alt başlıklardan sor ve soruları alt başlık etiketiyle işaretle"
                  + (f" ({guncel}a, {guncel}b: ana etiket {guncel} tanımlı, harfli etiket ayrıca tanımlanmaz)." if guncel else "."))
    son = gonderilen_adimlar(durum)
    if son and son[-1].get("dogru_siklar"):
        print(f"Doğru şık dağılımı: son adımda {son[-1]['dogru_siklar']}; bu adımda farklı şıklarda olsun.")
    acik = [k for k in durum.get("kusurlar", [])]
    if acik:
        print(f"Açık kusur: {len(acik)} (ders.py goster)")
    w = devir_uyarisi(durum, int(ayar.get("devir_esik", 10)))
    print(w if w else f"Devir: gönderilen mesaj {durum.get('mesaj_sayaci', 0)}/{ayar.get('devir_esik', 10)}")


# ───────────────────────────── denetim ─────────────────────────────
def anlatim_denetle(dosya, ders, ekstra=()):
    """anlatim_testi.py'yi çalıştırır -> (hata sayısı, uyarı sayısı, satırlar)."""
    r = subprocess.run([sys.executable, os.path.join(BURASI, "anlatim_testi.py"), dosya, "--ders", ders] + list(ekstra),
                       capture_output=True, text=True)
    satirlar = [l.rstrip() for l in r.stdout.splitlines() if re.match(r"\s+(HATA|UYARI)\b", l)]
    hata = sum(1 for l in satirlar if l.lstrip().startswith(H))
    return hata, len(satirlar) - hata, satirlar, r.returncode, r.stderr


def etiketleri_oku(html):
    """Widget HTML'indeki var Q=[...] -> [(etiket, dogru şık no)]."""
    import anlatim_testi_ek as EK
    q = EK.w10_sorular(html) or []
    return [(x.get("bolum", ""), x["dogru"]) for x in q]


def karisik_denetim(durum, adim, etiketler, ayar):
    """Durumdaki konu geçmişine karşı: etiket bilinen mi, güncel dışından en az biri var mı, aynı eski konu art arda tekrar mı."""
    b = []
    n_soru = int(ayar.get("mini_test_soru", 2))
    bilinen = durum["konular"]
    guncel = next((e for e, k in bilinen.items() if k.get("adim") == adim["no"]), None)
    kume = {e for e, k in bilinen.items() if k.get("adim") == adim["no"]}      # bu adımın tüm etiketleri (alt başlıklar ayrı tanımlıysa hepsi)
    for e, _ in etiketler:
        if not e:
            b.append((H, "D01", "soruda konu etiketi yok (6. eleman); ders.py konu-ekle ile tanımlı bir etiket yaz"))
        elif ana_etiket(durum, e) not in bilinen:
            b.append((H, "D02", f"etiket '{e}' durumda tanımlı değil (ders.py konu-ekle {e} \"…\")"))
    ana = [ana_etiket(durum, e) for e, _ in etiketler]
    oner, say = eski_konu_onerisi(durum, adim["no"], max(n_soru - 1, 1), guncel)
    if ana and n_soru > 1 and guncel and all(e in kume for e in ana):
        if oner:
            b.append((H, "D03", f"tüm sorular güncel konudan ({guncel}); mini test karışık olmalı, en az biri eski konudan"))
        elif len({e for e, _ in etiketler}) < 2:
            b.append((H, "D03", f"eski konu yok ve tüm sorular aynı etiketli ({guncel}); güncel konunun ayrı alt başlıklarından sor ve {guncel}a, {guncel}b gibi etiketle"))
    if ana and n_soru > 1 and guncel and all(e not in kume for e in ana):
        b.append((U, "D03", f"hiçbir soru güncel konudan ({guncel}) değil"))
    eski = [e for e in ana if e and e not in kume and e in bilinen]
    onceki = next((s for s in reversed(gonderilen_adimlar(durum)) if s["no"] < adim["no"]), None)
    tekrar = [e for e in eski if onceki and e in onceki.get("sorulan", [])]
    if tekrar and any(o not in tekrar for o in oner):
        b.append((U, "D04", f"{', '.join(tekrar)} bir önceki adımda da sorulmuştu; sorulmamış ya da daha az sorulmuş konu var: {', '.join(oner)}"))
    return b


def sadakat_denetim(durum, adim, mesaj, widget_html, proje):
    """araclar/sadakat.py varsa onu çağırır (UYARI üretir, HATA üretmez)."""
    try:
        import sadakat
    except ImportError:
        return []
    kaynak = adim.get("kaynak") or durum.get("kaynak")
    if not kaynak or not kaynak.endswith(".md"):
        return []
    return sadakat.denetle(durum, adim, mesaj, widget_html, proje)


def cmd_adim(a, proje, durum, ayar):
    no = a.no
    if not os.path.isfile(a.taslak):
        sys.exit(f"taslak yok: {a.taslak}")
    adim = adim_bul(durum, no, yeni=True)
    if a.konu:
        adim["baslik"] = a.konu
    if a.kaynak:
        adim["kaynak"] = a.kaynak
    if a.sayfa:
        adim["sayfa"] = a.sayfa
    cd = cikti_dir(proje, durum)
    mesaj = open(a.taslak, encoding="utf-8").read()
    toplam_hata, rapor = 0, []

    def ekle(kaynak, hata, uyari, satirlar):
        nonlocal toplam_hata
        toplam_hata += hata
        rapor.append(f"{kaynak}: {hata} hata, {uyari} uyarı")
        rapor.extend("  " + l.strip() for l in satirlar)

    ek = (["--ilk"] if a.ilk else [])
    h, u, s, rc, err = anlatim_denetle(a.taslak, durum["ders"], ek)
    if rc == 2:
        sys.exit(f"anlatim_testi çalışmadı: {err.strip()}")
    ekle(f"mesaj {no:02d}", h, u, s)
    html = None
    if a.widget:
        if a.widget.endswith(".json"):
            import widget
            try:
                spec = json.load(open(a.widget, encoding="utf-8"))
                tema = ayar.get("tema")
                if tema == "karma":
                    sys.exit("profilde tema 'karma': widget.py yalnız Neobrutalism motorudur")
                html = widget.olustur(spec, tema, proje)
            except widget.SpecHatasi as e:
                ekle(f"widget {no:02d} (spec)", 1, 0, [f"  {H} SPEC: {e}"])
        else:
            html = open(a.widget, encoding="utf-8").read()
    if html is not None:
        wy = os.path.join(cd, f"{no:02d}.widget.html")
        open(wy, "w", encoding="utf-8").write(html)
        konu_args = ["--test-turu", "mini"] + (["--konu", adim["baslik"]] if adim.get("baslik") else [])
        h, u, s, rc, err = anlatim_denetle(wy, durum["ders"], konu_args)
        ekle(f"widget {no:02d}", h, u, s)
        et = etiketleri_oku(html)
        kb = karisik_denetim(durum, adim, et, ayar)
        ekle(f"karışık soru {no:02d}", sum(1 for x in kb if x[0] == H), sum(1 for x in kb if x[0] == U), [f"  {x[0]} {x[1]}: {x[2]}" for x in kb])
        adim["sorulacak"] = [e for e, _ in et]
        adim["dogru_siklar"] = [d for _, d in et]
        import widget as W
        W.yuk_yaz(html, f"{durum['ad']}-adim-{no:02d}", os.path.join(cd, f"{no:02d}.yuk.json"))
    sb = sadakat_denetim(durum, adim, mesaj, html, proje)
    if sb:
        ekle(f"sadakat {no:02d}", 0, len(sb), [f"  {U} {x}" for x in sb])
    open(os.path.join(cd, f"{no:02d}.mesaj.md"), "w", encoding="utf-8").write(mesaj)
    adim["hazir"] = {"mesaj_sha1": hashlib.sha1(mesaj.encode("utf-8")).hexdigest(),
                     "widget_sha1": hashlib.sha1(html.encode("utf-8")).hexdigest() if html is not None else None,
                     "hata": toplam_hata, "zaman": time.strftime("%Y-%m-%d %H:%M")}
    if adim.get("durum") != "gonderildi":
        adim["durum"] = "hazir" if toplam_hata == 0 else "hatali"
    kaydet(proje, durum)
    print("\n".join(rapor))
    print(f"SONUÇ: Adım {no}: " + ("HAZIR · " + cd + f"/{no:02d}.*" if toplam_hata == 0 else f"{toplam_hata} HATA, gönderme"))
    return 1 if toplam_hata else 0


# ───────────────────────────── yayın sonrası ─────────────────────────────
def cmd_yayinlandi(a, proje, durum, ayar):
    adim = adim_bul(durum, a.no)
    if adim.get("durum") == "hatali":
        print(f"UYARI: Adım {a.no} hatalı olarak işaretliydi; yine de gönderildi sayılıyor", file=sys.stderr)
    adim["durum"] = "gonderildi"
    adim["sorulan"] = list(dict.fromkeys(adim.get("sorulacak", [])))
    durum["mesaj_sayaci"] = durum.get("mesaj_sayaci", 0) + a.mesaj
    kaydet(proje, durum)
    esik = int(ayar.get("devir_esik", 10))
    print(f"Adım {a.no} gönderildi; mesaj sayacı {durum['mesaj_sayaci']}/{esik}; sorulan konular: {', '.join(adim['sorulan']) or '-'}")
    w = devir_uyarisi(durum, esik)
    if w:
        print(w)


def oturum_kaydi(yol=None):
    if yol:
        return yol
    adaylar = glob.glob("/root/.claude/projects/*/*.jsonl")
    return max(adaylar, key=os.path.getmtime) if adaylar else None


def post_cagrilari(yol):
    """Oturum kaydı -> ([(title, widget_code)], [text])."""
    def bul_(o, anahtar):
        if isinstance(o, dict):
            if anahtar in o:
                return o
            for v in o.values():
                r = bul_(v, anahtar)
                if r:
                    return r
        return None
    widgetlar, mesajlar = [], []
    for satir in open(yol, encoding="utf-8"):
        try:
            d = json.loads(satir)
        except ValueError:
            continue
        c = d.get("message", {}).get("content")
        if not isinstance(c, list):
            continue
        for b in c:
            if b.get("type") != "tool_use":
                continue
            ad = b.get("name", "")
            if ad.endswith("post_widget"):
                r = bul_(b["input"], "widget_code")
                if r:
                    wc = r["widget_code"]
                    if isinstance(wc, str) and wc.startswith('"'):
                        try:
                            wc = json.loads(wc)
                        except ValueError:
                            pass
                    widgetlar.append((r.get("title") or b["input"].get("title"), wc))
            elif ad.endswith("post_message"):
                t = b["input"].get("text")
                if isinstance(t, str):
                    mesajlar.append(t)
    return widgetlar, mesajlar


def ilk_fark(x, y):
    """İki metnin ilk farklı karakteri -> açıklama."""
    n = min(len(x), len(y))
    i = next((k for k in range(n) if x[k] != y[k]), n)
    if i == n and len(x) == len(y):
        return None
    a_, b_ = x[max(i - 12, 0):i + 12], y[max(i - 12, 0):i + 12]
    return f"{i}. karakterde: kayıtta …{a_!r}…, dosyada …{b_!r}… (uzunluk {len(x)} / {len(y)})"


def cmd_dogrula(a, proje, durum, ayar):
    yol = oturum_kaydi(a.oturum)
    if not yol or not os.path.isfile(yol):
        sys.exit("oturum kaydı bulunamadı (--oturum kayit.jsonl)")
    widgetlar, mesajlar = post_cagrilari(yol)
    cd = cikti_dir(proje, durum)
    numaralar = a.nolar or [s["no"] for s in gonderilen_adimlar(durum)]
    kotu = 0
    print(f"Kayıt: {yol} ({len(widgetlar)} widget, {len(mesajlar)} mesaj)")
    for no in numaralar:
        wy, my = os.path.join(cd, f"{no:02d}.widget.html"), os.path.join(cd, f"{no:02d}.mesaj.md")
        if os.path.isfile(wy):
            beklenen = open(wy, encoding="utf-8").read()
            baslik = f"{durum['ad']}-adim-{no:02d}"
            adaylar = [wc for t, wc in widgetlar if t == baslik] or [wc for t, wc in widgetlar if wc == beklenen]
            if not adaylar:
                print(f"  Adım {no:02d} widget: BULUNAMADI (başlık '{baslik}')")
                kotu += 1
            else:
                f = ilk_fark(adaylar[-1], beklenen)
                print(f"  Adım {no:02d} widget: " + ("AYNI" if f is None else "FARKLI · " + f))
                kotu += f is not None
        if os.path.isfile(my):
            beklenen = open(my, encoding="utf-8").read().strip()
            en_iyi = max(mesajlar, key=lambda t: difflib.SequenceMatcher(None, t.strip()[:600], beklenen[:600]).quick_ratio(), default=None)
            if en_iyi is None or difflib.SequenceMatcher(None, en_iyi.strip()[:600], beklenen[:600]).quick_ratio() < 0.8:
                print(f"  Adım {no:02d} mesaj: BULUNAMADI")
                kotu += 1
            else:
                f = ilk_fark(en_iyi.strip(), beklenen)
                print(f"  Adım {no:02d} mesaj: " + ("AYNI" if f is None else "FARKLI · " + f))
                kotu += f is not None
    print("SONUÇ: " + ("hepsi AYNI" if not kotu else f"{kotu} FARKLI/BULUNAMADI"))
    return 1 if kotu else 0


# ───────────────────────────── kusur, not, devir, rapor ─────────────────────────────
def cmd_kusur(a, proje, durum, ayar):
    durum.setdefault("kusurlar", []).append({"adim": a.no, "not": a.metin})
    kaydet(proje, durum)
    print(f"kusur kaydedildi: Adım {a.no}: {a.metin}")


def cmd_not(a, proje, durum, ayar):
    anahtar = {"zayif": "zayif_noktalar", "acik-soru": "acik_sorular", "tercih": "tercihler"}[a.tur]
    durum.setdefault(anahtar, []).append(a.metin)
    kaydet(proje, durum)
    print(f"{a.tur} kaydedildi")


def cmd_konu_ekle(a, proje, durum, ayar):
    k = durum["konular"].setdefault(a.etiket, {})
    k["ad"] = a.ad_
    if a.sayfa:
        k["sayfa"] = a.sayfa
    k["adim"] = a.adim if a.adim is not None else (siradaki_adim(durum) if "adim" not in k else k["adim"])
    kaydet(proje, durum)
    print(f"{a.etiket}: {k['ad']} (adım {k['adim']}" + (f", sayfa {k['sayfa']}" if k.get("sayfa") else "") + ")")


def cmd_devir(a, proje, durum, ayar):
    dd = os.path.join(proje, "dersler", durum["ders"], "devir")
    os.makedirs(dd, exist_ok=True)
    n = 1 + len(glob.glob(os.path.join(dd, durum["ad"] + "-*.md")))
    yol = os.path.join(dd, f"{durum['ad']}-{n}.md")
    g = gonderilen_adimlar(durum)
    son = g[-1]["no"] if g else 0
    hazir = [s["no"] for s in durum["adimlar"] if s.get("durum") in ("hazir", "hatali")]
    say = sorulma_say(durum)
    L = [f"# Devir notu: {durum.get('baslik', durum['ad'])} (devam {n})", "",
         f"Üretildi: {time.strftime('%Y-%m-%d %H:%M')} · ders.py devir (durum dosyasından; kural kopyası yok, yeni sohbet depodan okur)", "",
         "## Kod ve tempo", f"- Kod: {durum.get('kod') or '(profil/ayarlar.md)'}", f"- Tempo: {durum.get('tempo', 'J2')}" + (f" ({durum['tempo_neden']})" if durum.get("tempo_neden") else ""), "",
         "## Tam kaldığı yer",
         f"- Ders: {durum['ders']} · kaynak: {durum.get('kaynak', '-')}",
         f"- Son gönderilen adım: {son or 'yok'}" + (f" · {g[-1].get('baslik', '')}" if g and g[-1].get("baslik") else ""),
         f"- Sıradaki adım: {son + 1}" + (f" (hazır ama gönderilmemiş: {', '.join(map(str, hazir))})" if hazir else ""),
         f"- Gönderilen mesaj sayısı: {durum.get('mesaj_sayaci', 0)}", ""]
    L += ["## Konu etiketleri ve mini test geçmişi", "| Etiket | Konu | Adım | Sayfa | Kaç kez soruldu | Son soruldu |", "|---|---|---|---|---|---|"]
    for e, k in sorted(durum["konular"].items(), key=lambda x: (x[1].get("adim") or 0, x[0])):
        n_, _, s_ = say.get(e, (0, 0, 0))
        L.append(f"| {e} | {k['ad']} | {k.get('adim', '-')} | {k.get('sayfa', '-')} | {n_} | {('Adım ' + str(s_)) if n_ else '-'} |")
    L += ["", "## Açık soru"] + ([f"- {x}" for x in durum.get("acik_sorular", [])] or ["- yok"])
    L += ["", "## Zayıf noktalar ve açık kusurlar"] + [f"- {x}" for x in durum.get("zayif_noktalar", [])] + [f"- Adım {k['adim']}: {k['not']}" for k in durum.get("kusurlar", [])]
    if not durum.get("zayif_noktalar") and not durum.get("kusurlar"):
        L.append("- yok")
    L += ["", "## Kullanıcının bu sohbette verdiği tercihler"] + ([f"- {x}" for x in durum.get("tercihler", [])] or ["- yok"])
    open(yol, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"devir notu: {yol}")
    print(f"Koordinatöre (tek satır): devam sohbeti aç: {durum.get('baslik', durum['ad'])} (devam {n}), Kod: {durum.get('kod') or '(ayarlar.md)'}, not: {yol}")


def cmd_rapor(a, proje, durum, ayar):
    cd = cikti_dir(proje, durum)
    dosyalar = sorted(glob.glob(os.path.join(cd, "*.mesaj.md")) + glob.glob(os.path.join(cd, "*.widget.html")))
    if not dosyalar:
        sys.exit("denetlenecek çıktı yok (önce ders.py adim)")
    r = subprocess.run([sys.executable, os.path.join(BURASI, "anlatim_testi.py")] + dosyalar + ["--ders", durum["ders"], "--rapor"], capture_output=True, text=True)
    print(r.stdout.rstrip())
    g = gonderilen_adimlar(durum)
    print("\n--- Ders yöneticisine ünite raporu (taslak) ---")
    print(f"{durum.get('baslik', durum['ad'])}: {len(g)} adım gönderildi ({', '.join(str(s['no']) for s in g) or '-'}), {len(durum['konular'])} konu etiketi.")
    for k in durum.get("kusurlar", []):
        print(f"- Açık kusur · Adım {k['adim']}: {k['not']}")
    for z in durum.get("zayif_noktalar", []):
        print(f"- Zayıf nokta: {z}")


def cmd_goster(a, proje, durum, ayar):
    print(f"{durum.get('baslik', durum['ad'])} · ders {durum['ders']} · kaynak {durum.get('kaynak', '-')} · kod {durum.get('kod') or '-'} · tempo {durum.get('tempo', 'J2')}")
    print(f"Mesaj sayacı: {durum.get('mesaj_sayaci', 0)}/{ayar.get('devir_esik', 10)}")
    for s in durum["adimlar"]:
        print(f"  Adım {s['no']:02d} · {s.get('durum', '-'):10} · {s.get('baslik', '')}" + (f" · sorulan: {', '.join(s['sorulan'])}" if s.get("sorulan") else ""))
    for e, k in sorted(durum["konular"].items(), key=lambda x: (x[1].get("adim") or 0, x[0])):
        print(f"  {e}: {k['ad']} (adım {k.get('adim', '-')})")
    for k in durum.get("kusurlar", []):
        print(f"  kusur · Adım {k['adim']}: {k['not']}")


def cmd_baslat(a, proje):
    y = durum_yolu(proje, a.ders, a.ad)
    if os.path.exists(y):
        sys.exit(f"durum dosyası zaten var: {y}")
    ayar = profil_ayar()
    durum = {"ders": a.ders, "ad": a.ad, "baslik": a.baslik or a.ad, "kaynak": a.kaynak, "kod": a.kod or ayar.get("kod", ""), "tempo": a.tempo,
             "mesaj_sayaci": 0, "konular": {}, "adimlar": [], "kusurlar": [], "olusturma": time.strftime("%Y-%m-%d %H:%M")}
    kaydet(proje, durum)
    print(f"durum açıldı: {y}")


# ───────────────────────────── kendini deneme ─────────────────────────────
def kendini_dene():
    sorun = []

    def dene(ad, kosul):
        print(("geçti" if kosul else "BAŞARISIZ") + " · " + ad)
        if not kosul:
            sorun.append(ad)

    def calistir(*arg, ortam=None):
        return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(arg), capture_output=True, text=True, env={**os.environ, **(ortam or {})})
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "yerel"))
        json.dump({"terim_dili": "C2", "mini_test_soru": 2, "test_dil": "en-tr", "karisik_test": True, "devir_esik": 10}, open(os.path.join(d, "yerel", "profil.json"), "w"))
        env = {"AI_DERS_PROFIL": os.path.join(d, "yerel", "profil.json")}
        ortak = ["--proje", d, "--ders", "deneme", "--ad", "d1"]
        r = calistir("baslat", "--proje", d, "--ders", "deneme", "--ad", "d1", "--kaynak", "kaynak.md", "--kod", "A1", ortam=env)
        dene("baslat durum açar", r.returncode == 0 and os.path.isfile(durum_yolu(d, "deneme", "d1")))
        dene("aynı durum yeniden açılmaz", calistir("baslat", "--proje", d, "--ders", "deneme", "--ad", "d1", "--kaynak", "k.md", ortam=env).returncode != 0)
        for e, ad, ad_no in (("T1", "Su aktivitesi", 1), ("T2", "Maillard tepkimesi", 2), ("T3", "Lipit oksidasyonu", 3)):
            calistir("konu-ekle", e, ad, "--adim", str(ad_no), *ortak, ortam=env)
        # adım 1 ve 2 gönderildi gibi işaretle: T1 sorulan, T2 sorulan
        dur = json.load(open(durum_yolu(d, "deneme", "d1"), encoding="utf-8"))
        dur["adimlar"] = [{"no": 1, "durum": "gonderildi", "sorulan": ["T1"]}, {"no": 2, "durum": "gonderildi", "sorulan": ["T2", "T1"]}]
        dur["mesaj_sayaci"] = 2
        json.dump(dur, open(durum_yolu(d, "deneme", "d1"), "w", encoding="utf-8"), ensure_ascii=False)
        r = calistir("sonraki", *ortak, ortam=env)
        dene("sonraki: sıradaki adım 3", "Sıradaki: Adım 3" in r.stdout and "T3" in r.stdout)
        dene("sonraki: 1 eski konu önerilir, en az sorulan (T2: 1 kez; T1: 2 kez)", "T2 ·" in r.stdout and "T1 ·" not in r.stdout)
        dur["mesaj_sayaci"] = 7
        json.dump(dur, open(durum_yolu(d, "deneme", "d1"), "w", encoding="utf-8"), ensure_ascii=False)
        r = calistir("sonraki", *ortak, ortam=env)
        dene("devir: 8. mesajda '2 mesaj sonra' uyarısı", "2 mesaj sonra yeni sohbete taşınıyoruz" in r.stdout)
        dur["mesaj_sayaci"] = 8
        json.dump(dur, open(durum_yolu(d, "deneme", "d1"), "w", encoding="utf-8"), ensure_ascii=False)
        dene("devir: 9. mesajda '1 mesaj sonra' uyarısı", "1 mesaj sonra yeni sohbete taşınıyoruz" in calistir("sonraki", *ortak, ortam=env).stdout)
        dur["mesaj_sayaci"] = 10
        json.dump(dur, open(durum_yolu(d, "deneme", "d1"), "w", encoding="utf-8"), ensure_ascii=False)
        dene("devir: 10 mesajdan sonra DEVRET", "DEVRET" in calistir("sonraki", *ortak, ortam=env).stdout)
        dur["mesaj_sayaci"] = 2
        json.dump(dur, open(durum_yolu(d, "deneme", "d1"), "w", encoding="utf-8"), ensure_ascii=False)
        # uzun tablo (GK5 STATE.md'deki S1-S12 biçimi): eski konu olarak hiç sorulmamış konular önce önerilir
        tablo = [("T1a", "T1b"), ("T1c", "T2"), ("T3", "T2b"), ("T4", "T1d"), ("T5", "T3"), ("T6", "T4"), ("T7", "T2"), ("T8", "T6"), ("T9", "T5"), ("T10", "T8"), ("T11", "T7"), ("T12", "T6")]
        uzun = {"ders": "x", "ad": "y", "konular": {}, "adimlar": []}
        for i, (guncel_, eski_) in enumerate(tablo, 1):
            uzun["konular"][guncel_] = {"ad": guncel_, "adim": i}
            uzun["konular"].setdefault(eski_, {"ad": eski_, "adim": i})
            uzun["adimlar"].append({"no": i, "durum": "gonderildi", "sorulan": [guncel_, eski_]})
        uzun["konular"]["T13"] = {"ad": "T13", "adim": 13}
        oner, _ = eski_konu_onerisi(uzun, 13, 1, "T13")
        dene("uzun tablo: S13 için eski konu olarak hiç sorulmamış bir konu önerilir (T6 değil)", oner and oner[0] not in ("T6", "T2", "T3", "T4", "T5", "T8"))
        dene("uzun tablo: son adımda sorulan T12/T6 önerilmez", oner and oner[0] not in ("T12", "T6"))
        # karışık soru denetimi
        adim3 = {"no": 3}
        et_iyi = [("T3", 0), ("T2", 2)]
        dene("karışık: güncel + eski geçer", not [x for x in karisik_denetim(json.load(open(durum_yolu(d, "deneme", "d1"))), adim3, et_iyi, {"mini_test_soru": 2}) if x[0] == H])
        dene("karışık: hepsi güncel HATA", any(x[1] == "D03" and x[0] == H for x in karisik_denetim(json.load(open(durum_yolu(d, "deneme", "d1"))), adim3, [("T3", 0), ("T3", 1)], {"mini_test_soru": 2})))
        dene("karışık: tanımsız etiket HATA", any(x[1] == "D02" for x in karisik_denetim(json.load(open(durum_yolu(d, "deneme", "d1"))), adim3, [("T3", 0), ("T9", 1)], {"mini_test_soru": 2})))
        ilk = {"konular": {"T1": {"ad": "ilk", "adim": 1}}, "adimlar": []}
        ayar2 = {"mini_test_soru": 2}
        dene("ilk adım, eski konu yok: T1a + T1b geçer (D01–D03 yok)", not karisik_denetim(ilk, {"no": 1}, [("T1a", 0), ("T1b", 1)], ayar2))
        dene("ilk adım, eski konu yok: iki soru da T1 aynı etiket HATA, alt başlık harfi önerilir", any(x[1] == "D03" and x[0] == H and "T1a" in x[2] for x in karisik_denetim(ilk, {"no": 1}, [("T1", 0), ("T1", 1)], ayar2)))
        ilk2 = {"konular": {"T1a": {"ad": "a", "adim": 1}, "T1b": {"ad": "b", "adim": 1}}, "adimlar": []}
        dene("ilk adım: alt başlıklar ayrı tanımlıysa da (T1a, T1b) D03 yok", not [x for x in karisik_denetim(ilk2, {"no": 1}, [("T1a", 0), ("T1b", 1)], ayar2) if x[1] == "D03"])
        dene("ilk adım: T1a+T1b için 'hiçbir soru güncel değil' UYARISI yok", not [x for x in karisik_denetim(ilk, {"no": 1}, [("T1a", 0), ("T1b", 1)], ayar2) if x[1] == "D03"])
        dene("ilk adım: tanımsız ana etiketin harfi (T9a) D02", any(x[1] == "D02" for x in karisik_denetim(ilk, {"no": 1}, [("T1a", 0), ("T9a", 1)], ayar2)))
        dene("eski konu varken T3a + T3b yetmez (D03 HATA)", any(x[1] == "D03" and x[0] == H for x in karisik_denetim(json.load(open(durum_yolu(d, "deneme", "d1"))), adim3, [("T3a", 0), ("T3b", 1)], {"mini_test_soru": 2})))
        dene("karışık: bir önceki adımdaki eski konu tekrarı UYARI", any(x[1] == "D04" for x in karisik_denetim(json.load(open(durum_yolu(d, "deneme", "d1"))), adim3, [("T3", 0), ("T1", 1)], {"mini_test_soru": 2})))
        # kusur, devir, doğrulama
        calistir("kusur", "2", "Flüorür -> Florür", *ortak, ortam=env)
        calistir("not", "zayif", "Maillard çizimi", *ortak, ortam=env)
        r = calistir("devir", *ortak, ortam=env)
        notu = open(os.path.join(d, "dersler", "deneme", "devir", "d1-1.md"), encoding="utf-8").read() if os.path.isfile(os.path.join(d, "dersler", "deneme", "devir", "d1-1.md")) else ""
        basliklar = ("Kod ve tempo", "Tam kaldığı yer", "Açık soru", "Zayıf noktalar", "Kullanıcının bu sohbette verdiği tercihler", "Konu etiketleri")
        dene("devir notu: gorevler/devir.md'deki başlıklar + açık kusur", all(b in notu for b in basliklar) and "Flüorür" in notu)
        dene("devir: koordinatör satırı", "devam sohbeti aç:" in r.stdout and "(devam 1)" in r.stdout)
        # dogrula: sentetik oturum kaydı
        cd = os.path.join(durum_dir(d, "deneme"), "d1")
        os.makedirs(cd, exist_ok=True)
        html = '<div class="nb">Florür — çalışıyor ığüşöç</div>'
        open(os.path.join(cd, "01.widget.html"), "w", encoding="utf-8").write(html)
        open(os.path.join(cd, "01.mesaj.md"), "w", encoding="utf-8").write("Merhaba, bu birinci adımın mesajıdır ve yeterince uzundur.\n")

        def kayit(wc, mesaj):
            def satir(ad, girdi):
                return json.dumps({"message": {"content": [{"type": "tool_use", "name": ad, "input": girdi}]}}, ensure_ascii=False)
            y = os.path.join(d, "oturum.jsonl")
            open(y, "w", encoding="utf-8").write("\n".join([satir("mcp__x__post_message", {"text": mesaj}),
                                                           satir("mcp__x__post_widget", {"widget": "show_widget", "input": {"title": "d1-adim-01", "widget_code": wc}})]) + "\n")
            return y
        r = calistir("dogrula", "1", "--oturum", kayit(html, "Merhaba, bu birinci adımın mesajıdır ve yeterince uzundur."), *ortak, ortam=env)
        dene("dogrula: aynı yayın AYNI", r.returncode == 0 and r.stdout.count("AYNI") >= 3)
        r = calistir("dogrula", "1", "--oturum", kayit(html.replace("Florür", "Flüorür"), "Merhaba, bu birinci adımın mesajıdır ve yeterince uzundur."), *ortak, ortam=env)
        dene("dogrula: harf bozulması FARKLI ve yeri gösterilir", r.returncode == 1 and "FARKLI" in r.stdout and "Fl" in r.stdout)
        r = calistir("dogrula", "1", "--oturum", kayit(html, "Başka bir mesaj"), *ortak, ortam=env)
        dene("dogrula: kayıtta olmayan mesaj BULUNAMADI", r.returncode == 1 and "mesaj: BULUNAMADI" in r.stdout)
        # adim: taslak + spec
        import widget
        taslak = os.path.join(d, "t.md")
        open(taslak, "w", encoding="utf-8").write("## Su Aktivitesi\n\nKısa bir deneme metni yazıldı.\n")
        spec = dict(widget.ORNEK)
        spec["paneller"] = [spec["paneller"][0], spec["paneller"][1], [{"tur": "test", "sorular": [
            ["Which food has the lowest water activity? (Hangi gıdanın su aktivitesi en düşüktür?)", ["Honey (Bal)", "Fresh milk (Taze süt)", "Raw meat (Çiğ et)", "Cooked rice (Pişmiş pirinç)"], 0, "Bal şekerce zengindir.", "", "T3"],
            ["Which statement is correct? (Hangisi doğrudur?)", ["It freezes first (İlk o donar)", "It cannot act as a solvent (Çözücü olamaz)", "It is total water (Toplam sudur)", "It is above 0.9 (0.9 üstündedir)"], 1, "Bağlı su çözücü değildir.", "", "T2"]]}]]
        sp = os.path.join(d, "w.json")
        json.dump(spec, open(sp, "w", encoding="utf-8"), ensure_ascii=False)
        r = calistir("adim", "3", taslak, sp, "--konu", "Lipit oksidasyonu", *ortak, ortam=env)
        dene("adim: mesaj + spec + karışık soru işlenir, çıktı dosyaları yazılır", "karışık soru 03: 0 hata" in r.stdout and os.path.isfile(os.path.join(cd, "03.yuk.json")) and os.path.isfile(os.path.join(cd, "03.mesaj.md")))
        yuk = json.load(open(os.path.join(cd, "03.yuk.json"), encoding="utf-8"))
        dene("adim: yayın yükü title + widget_code", yuk["title"] == "d1-adim-03" and yuk["widget_code"].startswith('<div class="nb"'))
        spec["paneller"][2][0]["sorular"][1][5] = "T3"
        json.dump(spec, open(sp, "w", encoding="utf-8"), ensure_ascii=False)
        r = calistir("adim", "3", taslak, sp, "--konu", "Lipit oksidasyonu", *ortak, ortam=env)
        dene("adim: tüm sorular güncel konu → HATA, çıkış 1", r.returncode == 1 and "D03" in r.stdout)
        dene("adim: hatalı adım durumda 'hatali'", json.load(open(durum_yolu(d, "deneme", "d1")))["adimlar"][-1]["durum"] == "hatali")
        r = calistir("yayinlandi", "3", "--mesaj", "2", *ortak, ortam=env)
        dene("yayinlandi: sayaç +2, adım gönderildi", json.load(open(durum_yolu(d, "deneme", "d1")))["mesaj_sayaci"] == 4)
    print("KENDİNİ DENEME " + ("GEÇTİ" if not sorun else f"BAŞARISIZ ({len(sorun)})"))
    return 1 if sorun else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kendini-dene", action="store_true")
    alt = ap.add_subparsers(dest="komut")

    def ortak(p):
        p.add_argument("--proje")
        p.add_argument("--ders", default="")
        p.add_argument("--ad", default="")
        return p
    p = ortak(alt.add_parser("baslat"))
    p.add_argument("--kaynak", required=True)
    p.add_argument("--kod", default="")
    p.add_argument("--tempo", default="J2")
    p.add_argument("--baslik", default="")
    p = ortak(alt.add_parser("konu-ekle"))
    p.add_argument("etiket")
    p.add_argument("ad_")
    p.add_argument("--sayfa", default="")
    p.add_argument("--adim", type=int)
    ortak(alt.add_parser("sonraki"))
    p = ortak(alt.add_parser("adim"))
    p.add_argument("no", type=int)
    p.add_argument("taslak")
    p.add_argument("widget", nargs="?")
    p.add_argument("--konu", default="")
    p.add_argument("--kaynak", default="", help="bu adımın kaynak dosyası (varsayılan: durumdaki kaynak)")
    p.add_argument("--sayfa", default="", help="bu adımın kaynak sayfaları, ör. 28-34 (sadakat denetimi için)")
    p.add_argument("--ilk", action="store_true")
    p = ortak(alt.add_parser("yayinlandi"))
    p.add_argument("no", type=int)
    p.add_argument("--mesaj", type=int, default=1)
    p = ortak(alt.add_parser("dogrula"))
    p.add_argument("nolar", nargs="*", type=int)
    p.add_argument("--oturum")
    p = ortak(alt.add_parser("kusur"))
    p.add_argument("no", type=int)
    p.add_argument("metin")
    p = ortak(alt.add_parser("not"))
    p.add_argument("tur", choices=["zayif", "acik-soru", "tercih"])
    p.add_argument("metin")
    for k in ("devir", "rapor", "goster"):
        ortak(alt.add_parser(k))
    a = ap.parse_args()
    if a.kendini_dene:
        sys.exit(kendini_dene())
    if not a.komut:
        ap.print_usage(sys.stderr)
        sys.exit(2)
    proje = proje_kok(a.proje)
    if a.komut == "baslat":
        if not (a.ders and a.ad):
            sys.exit("--ders ve --ad gerekli")
        return cmd_baslat(a, proje)
    ders, ad = bul(proje, a.ders, a.ad)
    durum = yukle(proje, ders, ad)
    ayar = profil_ayar()
    islev = {"konu-ekle": cmd_konu_ekle, "sonraki": cmd_sonraki, "adim": cmd_adim, "yayinlandi": cmd_yayinlandi, "dogrula": cmd_dogrula, "kusur": cmd_kusur,
             "not": cmd_not, "devir": cmd_devir, "rapor": cmd_rapor, "goster": cmd_goster}[a.komut]
    sys.exit(islev(a, proje, durum, ayar) or 0)


if __name__ == "__main__":
    main()
