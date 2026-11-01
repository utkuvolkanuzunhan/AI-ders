#!/usr/bin/env python3
"""kod.json + gorsel/sablonlar -> KOD.md ve gorsel/galeri/galeri.html"""
import json, os, re, html
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = json.load(open(os.path.join(KOK, "araclar/kod.json"), encoding="utf-8"))

# alan varsayılanları (alanlar/<alan>/alan.json)
alanlar = []
ad = os.path.join(KOK, "alanlar")
if os.path.isdir(ad):
    for a in sorted(os.listdir(ad)):
        pj = os.path.join(ad, a, "alan.json")
        if os.path.exists(pj):
            c = json.load(open(pj, encoding="utf-8"))
            if c.get("varsayilan_kod"):
                alanlar.append(f"`{a}` ({c.get('ad', a)}): `{c['varsayilan_kod']}` depo varsayılanının üstüne biner")

# KOD.md
s = ["# Ayar kodu", "", "Her ayar bir harf, her seçenek bir rakam. Kod harf sırasıyla yazılır; eksik harf varsayılandır.",
     f"Depo varsayılanı: **`{K['varsayilan']}`**", "",
     "Örnekler: `A2` (sıkı kaynak modu, gerisi varsayılan) · `B2C2` (ciddi ton, İngilizce terim önce) · `F2/W01.W06-W03` (W01 ve W06 öncelikli, W03 hiç).", "",
     "Kodu tıklayarak üretmek için galeri sayfası: `gorsel/galeri/galeri.html` (Artifact olarak yayınlanır).", "",
     "| Harf | Ayar | Seçenekler | Varsayılan |", "|---|---|---|---|"]
var = dict(re.findall(r"([A-Z])(\d+)", K["varsayilan"]))
for h in K["harfler"]:
    sec = "<br>".join(f"**{h['harf']}{k}** {v}" for k, v in h["secenekler"].items())
    s.append(f"| {h['harf']} | {h['ad']} | {sec} | {h['harf']}{var[h['harf']]} |")
if alanlar:
    s += ["", "Alan varsayılanları (alanlar/<alan>/alan.json; verilen kod bunu da geçer): " + "; ".join(alanlar) + "."]
s += ["", "Her seçeneğin tam metni: `secenekler/<harf>/<harf><rakam>.md`. Yeni seçenek eklemek: gorevler/kural-guncelle.md."]
open(os.path.join(KOK, "KOD.md"), "w", encoding="utf-8").write("\n".join(s) + "\n")

# galeri
sab = []
d = os.path.join(KOK, "gorsel/sablonlar")
for f in sorted(os.listdir(d)):
    if not f.endswith(".html"): continue
    t = open(os.path.join(d, f), encoding="utf-8").read()
    m = re.match(r"<!--\s*(W\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*-->\s*", t)
    sab.append({"id": m.group(1), "ad": m.group(2), "ne": m.group(3), "dosya": f, "html": t[m.end():]})
veri = json.dumps({"kod": K, "sablon": sab}, ensure_ascii=False).replace("</", "<\\/")
sablon = open(os.path.join(KOK, "gorsel/galeri/galeri.sablon.html"), encoding="utf-8").read()
open(os.path.join(KOK, "gorsel/galeri/galeri.html"), "w", encoding="utf-8").write(sablon.replace("/*VERI*/null", veri))
print(f"KOD.md ve galeri.html üretildi ({len(sab)} şablon)")
