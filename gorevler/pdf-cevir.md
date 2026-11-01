# Görev: PDF'i metne çevir (bir kez)

Anlatım sohbetinde değil, ayrı bir işçide yapılır.

## Girdi
- Proje klasörüne ya da sohbete yüklenmiş PDF, ya da Drive'daki PDF'in OCR metni (kurulum/pdf-bolme betiği `[[SAYFA n]]` işaretli Google Dokümanı üretir).

- Slayt dosyası (.pptx) da olabilir: metni ve not alanını slayt slayt çıkar (`python-pptx`), görselleri mantık diliyle yaz. Slayt numarası basılı numara yerine geçer.

## Çıktı
`dersler/<ders>/pdf-metin/<kısa-ad>.md` (kullanıcının proje klasöründe):
```
# <PDF adı> (PDF <no>, <sayfa sayısı> sayfa)
[[SAYFA 9 | pdf 12]]
<sayfadaki yazı aynen>
[ŞEKİL 1.2: <ne gösteriyor; eksenler, birimler, oklar, değerler, ilişkiler; mantık diliyle>]
[TABLO 3: <markdown tablo olarak aynen>]
[[SAYFA 10 | pdf 13]]
...
```

## Sayfa numarası: kitabın kendi numarası esas
Kaynak gösterirken kullanılan numara, sayfanın ÜZERİNDE BASILI olan numaradır (genelde en altta; bazen üst köşede, kenarda ya da başlık satırında). PDF görüntüleyicinin sıra numarası değil.
1. Her sayfada basılı numarayı ara: önce alt orta/alt köşeler, sonra üst köşeler, sonra kenar ve başlık/altbilgi satırları. %99 sayfanın bir yerinde yazar.
2. İşareti `[[SAYFA <basılı> | pdf <sıra>]]` yaz. İkisi de her sayfada var.
3. Doğrulama (zorunlu, her çeviri sonunda):
   - Basılı numaralar ardışık mı? Atlama ya da tekrar varsa o sayfaları yeniden oku.
   - Fark sabit mi? (basılı = pdf − k). Fark bir yerde değişiyorsa (boş sayfa, ek, bölüm kapağı) nedenini sayfaya not düş: `[[SAYFA 23 | pdf 27 | not: s.22'den sonra numarasız ek sayfa]]`.
   - Basılı numara okunamayan sayfa: komşulardan çıkarılırsa `[[SAYFA ~23 | pdf 27 | çıkarıldı]]`, çıkarılamazsa `[[SAYFA ? | pdf 27]]`. Tahmini numara kaynak olarak kesinmiş gibi kullanılmaz.
   - Roma rakamı (ön sözler) ayrı yazılır: `[[SAYFA xii | pdf 14]]`.
   - Slaytta basılı numara yoksa slayt sırası kullanılır ve dosya başına `numara: slayt sırası` yazılır.
4. Dosyanın başına özet satırı: `sayfa eşlemesi: basılı = pdf − 3 (s.1–120), doğrulandı`.
- Yazılar aynen; özetleme, yorum ekleme yok.
- Çizim, şema, grafik, tablo: mantık diliyle (ne gösteriyor, eksenler, oklar, değerler, ilişkiler). Numarası korunur.
- Formüller LaTeX olarak (`$\dfrac{k_2}{k_1}$`).
- PDF numarası ve her sayfanın basılı numarası + PDF sıra numarası korunur (aşağıya bak).

## İndeks
Aynı klasördeki `indeks.md`'ye ekle:
```
## <PDF adı> (<kısa-ad>.md) · basılı = pdf − 3
- s.1–3 (pdf 4–6): <konu>
- s.4–8 (pdf 7–11): <konu>
```
Konu listesini kullanıcıya değil, ilgili dersin sohbetine gönder.

## Büyük PDF
- Sayfa sayfa ilerle; yarıda kalırsa dosyanın başına `YARIM: s.N'ye kadar` yaz, sonraki turda devam et.
