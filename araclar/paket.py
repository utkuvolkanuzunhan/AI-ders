#!/usr/bin/env python3
"""AI-ders okuma paketi: rol + ayar kodu -> tek metin.

Kullanım:
  python3 araclar/paket.py --rol unite --kod A1B3C3D1E3F1G2H1I1J2 --ders reaction-kinetics
  python3 araclar/paket.py --rol ders-yoneticisi --ders statistics
  python3 araclar/paket.py --rol unite --ders circuit-analysis-1 --alan eee   # alan katmanıyla
  python3 araclar/paket.py --rol unite --ders food-chemistry-1 --ek slayt.pdf   # ek dosya varsa: PDF kapısı
  python3 araclar/paket.py --kod-coz A2          # yalnız kodu çöz
  python3 araclar/paket.py --roller              # rolleri listele
Kod yazılmazsa varsayılan; eksik harfler varsayılandan tamamlanır.
Alan katmanı (alanlar/<alan>/): --alan ile ya da ders kartının başındaki `alan: <ad>` satırından bulunur.
Alanın varsayılan kodu (alan.json) depo varsayılanının üstüne biner; verilen kod ikisini de geçer.
F2 için beğeni listesi: ...F2/W01.W06-W03 (W03 hiç kullanılmaz).
PDF kapısı: --ek ile çevrilmemiş dosya (PDF/slayt/görsel) verilirse ve rol pdf-cevirici değilse kural paketi
verilmez; yalnız yönlendirme görevi basılır ve çıkış kodu 3 olur (çeviri ve anlatım ayrı sohbetlerdedir).
"""
import argparse, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kaynak import ham_mi  # noqa: E402

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOD = json.load(open(os.path.join(KOK, "araclar", "kod.json"), encoding="utf-8"))


def oku(yol):
    p = os.path.join(KOK, yol)
    if not os.path.exists(p):
        return None
    return open(p, encoding="utf-8").read().strip()


def kart_oku(ders):
    """Ders kartını okur. Başında `---` arasında `alan: <ad>` varsa onu ayırır. -> (alan, metin)"""
    t = oku(f"dersler/{ders}/ders.md")
    if t is None:
        return "", None
    alan = ""
    m = re.match(r"---\s*\n(.*?)\n---\s*\n?", t, re.S)
    if m:
        a = re.search(r"^alan:\s*(\S+)", m.group(1), re.M)
        if a:
            alan = a.group(1).lower()
        t = t[m.end():].strip()
    return alan, t


def alan_oku(alan):
    """alanlar/<alan>/alan.json -> sözlük; alan yoksa None."""
    p = os.path.join(KOK, "alanlar", alan, "alan.json") if alan else ""
    if not p or not os.path.exists(p):
        return None
    return json.load(open(p, encoding="utf-8"))


def kod_coz(kod, taban=""):
    """Kodu {harf: rakam} sözlüğüne çevirir; hata varsa açıklamayla çıkar.
    taban: alanın varsayılan kodu (ör. "A4"); depo varsayılanının üstüne biner, verilen kod onu da geçer."""
    harfler = {h["harf"]: h for h in KOD["harfler"]}
    sonuc = dict(re.findall(r"([A-Z])(\d+)", KOD["varsayilan"]))
    if taban:
        kod = taban + (kod or "")
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
    ap.add_argument("--alan", default="", help="alan katmanı (alanlar/<alan>/); yoksa ders kartından bulunur")
    ap.add_argument("--kod-coz", dest="kodcoz")
    ap.add_argument("--roller", action="store_true")
    ap.add_argument("--ek", action="append", default=[], help="sohbete eklenen/briefte verilen dosya (tekrarlanabilir)")
    a = ap.parse_args()

    if a.roller:
        for k, v in KOD["roller"].items():
            print(f"{k}: {v['aciklama']}")
        return
    if a.kodcoz is not None:
        cfg = alan_oku(a.alan.lower())
        sec, b, i = kod_coz(a.kodcoz, cfg.get("varsayilan_kod", "") if cfg else "")
        print(f"Kod: {kod_yaz(sec, b, i)}\n\n{tablo(sec)}")
        return
    if not a.rol or a.rol not in KOD["roller"]:
        sys.exit(f"--rol gerekli. Roller: {', '.join(KOD['roller'])}")

    rol = KOD["roller"][a.rol]
    ham = [e for e in a.ek if ham_mi(e)]
    if ham and a.rol not in ("pdf-cevirici", "soru-seti"):
        print(f"# AI-ders: PDF KAPISI\n\nRol: **{a.rol}** · Ek: {', '.join(ham)}\n\n"
              "Bu sohbete çevrilmemiş kaynak eklendi. Bu sohbet ONU AÇMAZ, ÇEVİRMEZ ve ANLATIM YAPMAZ. "
              "Kural paketi verilmedi; yalnız aşağıdaki görevi uygula.\n\n---\n\n" + oku("gorevler/pdf-yonlendir.md"))
        sys.exit(3)
    # Alan: --alan > ders kartındaki `alan:` satırı > yok (çekirdek kurallar yalnız)
    alan_kart, kart = kart_oku(a.ders) if a.ders else ("", None)
    alan = (a.alan or alan_kart).strip().lower()
    cfg = alan_oku(alan)
    sec, begen, istemez = kod_coz(a.kod, cfg.get("varsayilan_kod", "") if cfg else "")
    parca = []
    parca.append(f"# AI-ders okuma paketi\n\nRol: **{a.rol}** · Kod: **{kod_yaz(sec, begen, istemez)}**"
                 + (f" · Ders: **{a.ders}**" if a.ders else "")
                 + (f" · Alan: **{alan}**" if cfg else "")
                 + ("\n\n**Bu sohbet ANLATIM YAPMAZ.** Tek çıktı pdf-metin dosyası + indeks; bitince koordinatörden anlatım sohbeti iste." if a.rol == "pdf-cevirici" else "")
                 + "\n\nBu paket bu sohbetin tüm kurallarıdır. Kullanıcının bu sohbette açıkça söyledikleri her şeyi geçer.\n\n"
                 + tablo(sec))
    if begen or istemez:
        parca.append(f"Beğenilen şablonlar: {', '.join(begen) or '-'} · Kullanılmayacak: {', '.join(istemez) or '-'}")
    parca.append(oku("cekirdek/temel.md"))
    if alan and not cfg:
        parca.append(f"> Alan katmanı yok: alanlar/{alan}/alan.json. Yalnız çekirdek kurallarla devam et.")
    if cfg and cfg.get("kurallar"):
        parca.append(oku(f"alanlar/{alan}/{cfg['kurallar']}"))
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
        if cfg and cfg.get("katalog"):
            parca.append(oku(f"alanlar/{alan}/{cfg['katalog']}"))
    if rol["ders"] and a.ders:
        d = kart
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
