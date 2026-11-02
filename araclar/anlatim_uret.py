#!/usr/bin/env python3
"""Anlatım widget'ı (W25): JSON -> post_widget'a hazır HTML.

Sekmeli anlatım için: sekmelerin gövdesi (çizgili/gri/derin renkli/pastel bileşenler, formül terimleri,
işaret ve hesap bölümü) ve her sekmenin çizgili mini testi JSON'da durur; şablondaki /*VERI*/ bloğu yenilenir.

Kullanım:
  python3 araclar/anlatim_uret.py veri.json cikti.html     # widget HTML'i (post_widget'a aynen yapıştırılır)
  python3 araclar/anlatim_uret.py veri.json --kontrol      # yalnız doğrula
  python3 araclar/anlatim_uret.py --ornek                  # örnek veri JSON'unu yazdır

Veri biçimi (JSON):
{
  "sekmeler": [
    {"ad": "Formül",
     "html": "<div class=\\"lb\\">...</div>...",             # bileşenler: gorsel/stil.md §3-§5
     "sorular": [                                           # 0-3 soru; yoksa mini test çıkmaz
       {"soru": "English question? (Türkçesi?)",
        "siklar": ["A text (Türkçe)", "B text (Türkçe)", "C text (Türkçe)", "D text (Türkçe)"],
        "dogru": 0,                                         # 0 tabanlı şık sırası
        "aciklama": "Neden doğru.", "ipucu": "Düşündüren ipucu."}]}
  ],
  "tanimlar": {"ed": "<b>Terim (Türkçesi)</b><p>Açıklama.</p>"}   # formül terimi/kart: data-d="ed" -> bu metin
}
Alt indis: <span class=\\"sb\\">d</span>. Biçim kuralları ve renk/yüzey sınıfları: gorsel/stil.md.
"""
import argparse, json, os, re, sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SABLON = os.path.join(KOK, "gorsel/sablonlar/W25-anlatim-karma.html")
BAS, SON = "\n/*VERI*/\n", "\n/*VERI_SON*/"
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⭕✅❌]")


def ornek():
    return {
        "sekmeler": [
            {"ad": "Formül",
             "html": ('<div class="lb">Ürünün kendi fiyatı değişirse</div>'
                      '<div class="fm z1"><span class="tm k1" role="button" tabindex="0" data-d="ed">E<span class="sb">d</span></span>'
                      '<span class="es">=</span><span class="fr"><span class="n"><span class="tm k2" role="button" tabindex="0" data-d="dq">%ΔQ<span class="sb">d</span></span></span>'
                      '<span><span class="tm k3" role="button" tabindex="0" data-d="dp">%ΔP</span></span></span></div>'
                      '<div class="dt zp k1"></div>'
                      '<div class="h">Ne yapacaksın: formüldeki bir terime dokun. Ne göreceksin: o terimin anlamı.</div>'),
             "sorular": [{"soru": "If price rises by 10% and quantity demanded falls by 5%, what is E<span class=\"sb\">d</span>? (Fiyat %10 artar, miktar %5 düşerse E<span class=\"sb\">d</span> kaç olur?)",
                          "siklar": ["−0.5 (−0,5)", "−2 (−2)", "+0.5 (+0,5)", "+2 (+2)"], "dogru": 0,
                          "aciklama": "E<span class=\"sb\">d</span> = −5 ÷ 10 = −0,5.", "ipucu": "Önce %ΔP ve %ΔQ işaretlerini yaz, sonra böl."}]},
            {"ad": "İşaret ve Hesap",
             "html": ('<div class="lb">İşaret (sign)</div><div class="sn"><span class="sy">−</span>'
                      '<div>Fiyat ↑, miktar ↓: ters yönde<small>bu yüzden E<span class="sb">d</span> negatif çıkar</small></div></div>'
                      '<div class="lb">Hesap (calculation)</div><div class="sl"><div><i>1</i><div><div class="hs">%ΔP = (12 − 10) ÷ 10 = +20%</div>'
                      '<small>fiyat 10 dolardan 12 dolara çıktı</small></div></div></div>'
                      '<div class="rz"><b>E<span class="sb">d</span> = −0,5</b><span>|E<span class="sb">d</span>| = 0,5 &lt; 1: inelastic (esnek değil)</span></div>'),
             "sorular": []},
        ],
        "tanimlar": {
            "ed": '<b>E<span class="sb">d</span>: price elasticity of demand (talebin fiyat esnekliği)</b><p>Fiyat değişince talep edilen miktar ne kadar değişir?</p>',
            "dq": '<b>%ΔQ<span class="sb">d</span>: percentage change in quantity demanded (talep edilen miktardaki yüzde değişim)</b><p>Miktar yüzde kaç değişti?</p>',
            "dp": '<b>%ΔP: percentage change in price (fiyattaki yüzde değişim)</b><p>Fiyat yüzde kaç değişti?</p>'},
    }


def kontrol(v):
    h, u = [], []
    if not v.get("sekmeler"):
        h.append("sekmeler boş")
    tan = v.get("tanimlar", {})
    kullanilan = set()
    for i, s in enumerate(v.get("sekmeler", []), 1):
        ad = s.get("ad") or f"#{i}"
        if not s.get("ad"): h.append(f"sekme {i}: ad yok")
        if not s.get("html"): h.append(f"{ad}: html yok")
        kullanilan |= set(re.findall(r'data-d="([^"]+)"', s.get("html", "")))
        if "<button" in s.get("html", ""): h.append(f"{ad}: <button> yok sayılmaz, role=button kullan")
        if EMOJI.search(s.get("html", "")): h.append(f"{ad}: widget içinde emoji yok")
        if len(s.get("sorular", [])) > 3: u.append(f"{ad}: mini test 3 sorudan uzun (stil.md §7)")
        for k, q in enumerate(s.get("sorular", []), 1):
            et = f"{ad} soru {k}"
            for a in ("soru", "siklar", "dogru", "aciklama"):
                if a not in q: h.append(f"{et}: {a} yok")
            sk = q.get("siklar", [])
            if not 2 <= len(sk) <= 5: h.append(f"{et}: şık sayısı 2-5 olmalı")
            if not isinstance(q.get("dogru"), int) or not 0 <= q.get("dogru", -1) < len(sk): h.append(f"{et}: dogru sırası şıkların dışında")
            for t in [q.get("soru", "")] + sk:
                if not re.search(r"\([^()]*\)\s*$", re.sub(r"<[^>]+>", "", t)):
                    u.append(f"{et}: sonda Türkçe parantez yok: {re.sub('<[^>]+>', '', t)[:50]}")
            if not q.get("ipucu"): u.append(f"{et}: ipucu yok")
    for d in sorted(kullanilan - set(tan)): h.append(f'data-d="{d}" için tanimlar girdisi yok')
    for d in sorted(set(tan) - kullanilan): u.append(f'tanimlar["{d}"] hiçbir sekmede kullanılmıyor')
    return h, u


def js(v):
    T = [{"n": s["ad"], "h": s["html"],
          "q": [[q["soru"], q["siklar"], q["dogru"], q["aciklama"], q.get("ipucu", "")] for q in s.get("sorular", [])]}
         for s in v["sekmeler"]]
    d = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"var T={d(T)},\nD={d(v.get('tanimlar', {}))};\n"


def uret(v):
    t = open(SABLON, encoding="utf-8").read()
    i, j = t.index(BAS) + len(BAS), t.index(SON)
    c = t[:i] + js(v) + t[j + 1:]
    return re.sub(r"^<!--.*?-->\s*", "", c, count=1, flags=re.S)


def main():
    ap = argparse.ArgumentParser(description="Anlatım widget'ı (W25)", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("veri", nargs="?")
    ap.add_argument("cikti", nargs="?")
    ap.add_argument("--kontrol", action="store_true")
    ap.add_argument("--ornek", action="store_true")
    a = ap.parse_args()
    if a.ornek:
        print(json.dumps(ornek(), ensure_ascii=False, indent=2)); return
    if not a.veri:
        ap.error("veri.json gerekli")
    v = json.load(open(a.veri, encoding="utf-8"))
    h, u = kontrol(v)
    for x in u: print("uyarı:", x)
    for x in h: print("HATA:", x)
    if h: sys.exit(1)
    if a.kontrol or not a.cikti:
        print("tamam" if not u else "tamam (uyarılarla)"); return
    open(a.cikti, "w", encoding="utf-8").write(uret(v))
    print("yazıldı:", a.cikti)


if __name__ == "__main__":
    main()
