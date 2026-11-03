#!/usr/bin/env python3
"""Kaynak okuma kapısı: anlatım sohbetleri kaynağı YALNIZ bununla okur.

Kullanım:
  python3 araclar/kaynak.py <pdf-metin.md> <basılı-baş> [basılı-son]   # basılı sayfa numarasıyla
  python3 araclar/kaynak.py <pdf-metin.md> --pdf <sıra-baş> [sıra-son]  # pdf sıra numarasıyla
  python3 araclar/kaynak.py <pdf-metin.md> --liste                      # sayfa işaretlerini listele

Yalnız çevrilmiş metin (.md, `[[SAYFA <basılı> | pdf <sıra>]]` işaretli) okunur. PDF, slayt ya da görsel
verilirse okumaz ve çıkış kodu 3 ile çeviri sohbeti istenmesini söyler (anlatım ve çeviri ayrı sohbetlerdedir).
"""
import os, re, sys

HAM = (".pdf", ".ppt", ".pptx", ".key", ".doc", ".docx", ".png", ".jpg", ".jpeg", ".heic", ".webp")
ISARET = re.compile(r"^\[\[SAYFA\s+([^|\]]*?)\s*\|\s*pdf\s+(\d+)[^\]]*\]\]", re.M)


def dur(mesaj, kod=3):
    sys.stderr.write(mesaj.strip() + "\n")
    sys.exit(kod)


def ham_mi(yol):
    if yol.lower().endswith(HAM):
        return True
    if os.path.exists(yol):
        with open(yol, "rb") as f:
            if f.read(5) == b"%PDF-":
                return True
    return False


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    yol = a[0]
    if ham_mi(yol):
        dur(f"""DUR: '{yol}' çevrilmemiş kaynak (PDF/slayt/görsel). Bu sohbet onu AÇMAZ ve ÇEVİRMEZ.
Koordinatöre tek mesaj gönder: "PDF çeviri sohbeti aç. Brief: AI-ders oku. Rol: pdf-cevirici. Ders: <ders>. Dosya: {yol}. Konu: <istenen konu>. Kod: <geçerli kod>."
Kullanıcıya tek satır: "PDF'i çeviri sohbetine gönderdim; metin hazır olunca anlatım yeni sohbette başlayacak." Ayrıntı: gorevler/pdf-yonlendir.md""")
    if not os.path.exists(yol):
        dur(f"Dosya yok: {yol}. indeks.md'den doğru pdf-metin dosyasını bul; metin yoksa çeviri sohbeti iste (gorevler/pdf-yonlendir.md).", 2)
    t = open(yol, encoding="utf-8").read()
    isaretler = [(m.start(), m.group(1).strip(), int(m.group(2))) for m in ISARET.finditer(t)]
    if not isaretler:
        dur(f"'{yol}' içinde [[SAYFA <basılı> | pdf <sıra>]] işareti yok; çevrilmiş metin değil. Çeviri sohbeti iste (gorevler/pdf-yonlendir.md).")
    if a[1:2] == ["--liste"]:
        for _, b, p in isaretler:
            print(f"basılı {b or '?'} · pdf {p}")
        return
    pdf = a[1:2] == ["--pdf"]
    sayi = a[2:] if pdf else a[1:]
    if not sayi:
        dur("Sayfa aralığı ver: <baş> [son]. Tüm dosyayı okuma.", 2)
    bas, son = sayi[0], (sayi[1] if len(sayi) > 1 else sayi[0])

    def anahtar(i):
        _, b, p = isaretler[i]
        return str(p) if pdf else b.lstrip("~").strip()

    idx = [i for i in range(len(isaretler)) if anahtar(i) in (bas, son)]
    ilk = next((i for i in range(len(isaretler)) if anahtar(i) == bas), None)
    sonu = max((i for i in idx if anahtar(i) == son), default=None)
    if ilk is None or sonu is None or sonu < ilk:
        dur(f"Sayfa bulunamadı ({'pdf' if pdf else 'basılı'} {bas}–{son}). Mevcut işaretler için: --liste", 2)
    bitis = isaretler[sonu + 1][0] if sonu + 1 < len(isaretler) else len(t)
    parca = t[isaretler[ilk][0]:bitis].rstrip()
    if "[[MODEL-OKU" in parca:
        dur(f"""DUR: bu aralıkta çevirisi tamamlanmamış sayfa var (tablo/şekil/grafik model okumasını bekliyor, `[[MODEL-OKU`). Bu sohbet tamamlamaz.
Eksik şekil/tablo olan metne dayanma. Koordinatörden tek mesajla çeviri sohbetinin bitirmesini iste: "PDF çevirisi yarım: {yol}. Rol: pdf-cevirici." Ayrıntı: gorevler/pdf-cevir.md""")
    print(parca)


if __name__ == "__main__":
    main()
