#!/usr/bin/env python3
"""AI-ders okuma paketi: rol + ayar kodu -> tek metin.

Kullanım:
  python3 araclar/paket.py --rol unite --kod A1B3C3D1E3F1G2H1I1J1 --ders reaction-kinetics
  python3 araclar/paket.py --rol ders-yoneticisi --ders statistics
  python3 araclar/paket.py --kod-coz A2          # yalnız kodu çöz
  python3 araclar/paket.py --roller              # rolleri listele
Kod yazılmazsa varsayılan; eksik harfler varsayılandan tamamlanır.
F2 için beğeni listesi: ...F2/W01.W06-W03 (W03 hiç kullanılmaz).
"""
import argparse, json, os, re, sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOD = json.load(open(os.path.join(KOK, "araclar", "kod.json"), encoding="utf-8"))


def oku(yol):
    p = os.path.join(KOK, yol)
    if not os.path.exists(p):
        return None
    return open(p, encoding="utf-8").read().strip()


def kod_coz(kod):
    """Kodu {harf: rakam} sözlüğüne çevirir; hata varsa açıklamayla çıkar."""
    harfler = {h["harf"]: h for h in KOD["harfler"]}
    sonuc = dict(re.findall(r"([A-Z])(\d+)", KOD["varsayilan"]))
    ek = ""
    if kod:
        kod = kod.strip().upper().replace(" ", "")
        if "/" in kod:
            kod, ek = kod.split("/", 1)
        kalan = re.sub(r"[A-Z]\d+", "", kod)
        if kalan:
            sys.exit(f"Kod okunamadı: '{kalan}' parçası harf+rakam değil. Örnek: {KOD['varsayilan']}")
        for h, r in re.findall(r"([A-Z])(\d+)", kod):
            if h not in harfler:
                sys.exit(f"Bilinmeyen harf: {h}. Geçerli harfler: {', '.join(harfler)}")
            if r not in harfler[h]["secenekler"]:
                gec = ", ".join(f"{h}{k} ({v})" for k, v in harfler[h]["secenekler"].items())
                sys.exit(f"{h}{r} yok. {harfler[h]['ad']} için seçenekler: {gec}")
            sonuc[h] = r
    begen, istemez = [], []
    for m in re.finditer(r"(-?)(W\d+)", ek):
        (istemez if m.group(1) else begen).append(m.group(2))
    return sonuc, begen, istemez


def kod_yaz(sec, begen, istemez):
    s = "".join(f"{h}{sec[h]}" for h in sorted(sec))
    if begen or istemez:
        s += "/" + ".".join(begen) + "".join("-" + w for w in istemez)
    return s


def tablo(sec):
    satir = ["| Harf | Ayar | Seçim |", "|---|---|---|"]
    for h in KOD["harfler"]:
        r = sec[h["harf"]]
        satir.append(f"| {h['harf']}{r} | {h['ad']} | {h['secenekler'][r]} |")
    return "\n".join(satir)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rol")
    ap.add_argument("--kod", default="")
    ap.add_argument("--ders", default="")
    ap.add_argument("--kod-coz", dest="kodcoz")
    ap.add_argument("--roller", action="store_true")
    a = ap.parse_args()

    if a.roller:
        for k, v in KOD["roller"].items():
            print(f"{k}: {v['aciklama']}")
        return
    if a.kodcoz is not None:
        sec, b, i = kod_coz(a.kodcoz)
        print(f"Kod: {kod_yaz(sec, b, i)}\n\n{tablo(sec)}")
        return
    if not a.rol or a.rol not in KOD["roller"]:
        sys.exit(f"--rol gerekli. Roller: {', '.join(KOD['roller'])}")

    rol = KOD["roller"][a.rol]
    sec, begen, istemez = kod_coz(a.kod)
    parca = []
    parca.append(f"# AI-ders okuma paketi\n\nRol: **{a.rol}** · Kod: **{kod_yaz(sec, begen, istemez)}**"
                 + (f" · Ders: **{a.ders}**" if a.ders else "")
                 + "\n\nBu paket bu sohbetin tüm kurallarıdır. Kullanıcının bu sohbette açıkça söyledikleri her şeyi geçer.\n\n"
                 + tablo(sec))
    if begen or istemez:
        parca.append(f"Beğenilen şablonlar: {', '.join(begen) or '-'} · Kullanılmayacak: {', '.join(istemez) or '-'}")
    parca.append(oku("cekirdek/temel.md"))
    parca.append(oku(f"roller/{a.rol}.md"))
    for g in rol["gorevler"]:
        parca.append(oku(f"gorevler/{g}.md"))
    harfler = [h["harf"] for h in KOD["harfler"]] if rol["secenekler"] == "hepsi" else rol["secenekler"]
    if harfler:
        parca.append("# Ayar kodu seçenekleri")
        for h in harfler:
            parca.append(oku(KOD["secenek_dosyasi"].format(harf=h, rakam=sec[h])))
    if rol["gorsel"]:
        parca.append(oku("gorsel/stil.md"))
        parca.append(oku("gorsel/katalog.md"))
    if rol["ders"] and a.ders:
        d = oku(f"dersler/{a.ders}/ders.md")
        if d is None:
            mevcut = sorted(x for x in os.listdir(os.path.join(KOK, "dersler")) if not x.startswith("_"))
            parca.append(f"> Ders kartı yok: dersler/{a.ders}/ders.md. Mevcut dersler: {', '.join(mevcut)}. "
                         "Yeni ders ise dersler/_sablon/'dan oluştur (gorevler/kural-guncelle.md).")
        else:
            parca.append(d)
            if sec["C"] == "3":
                s = oku(f"dersler/{a.ders}/sozluk.md")
                if s:
                    parca.append(s)
    metin = "\n\n---\n\n".join(p for p in parca if p)
    print(metin)
    print(f"\n\n<!-- paket boyutu: {len(metin.encode('utf-8')) // 1024} KB -->")


if __name__ == "__main__":
    main()
