# Sohbet mesajlarında formül yazımı

**Belirti:** Mesajdaki formül çizilmez, ham LaTeX görünür (`\Large \boldsymbol{...}`) ya da kesir/indis bozulur. Claude uygulamasında (tablet, telefon) 2 Kasım 2026'da denendi; çekirdekteki ve alanlardaki eski formül kalıplarının önüne geçer. `anlatim_testi.py` F01–F14 ile denetler.

## Kurallar
1. Formül ya `$$...$$` bloğudur (kendi satırında, üstünde ve altında boş satır) ya da kısa satır içi `$...$`. Bir blokta tek denklem; çok denklem varsa her biri ayrı blok.
2. Ham görünen komutlar yazılmaz: `\Large`, `\LARGE`, `\boldsymbol`, `\mathbf`, `\boxed`, `\color`, `\displaystyle`, `\qquad`, `\quad`. `$$` bloğu zaten büyük çıkar; renk, kalınlık, vurgu formülde değil widget'ta (formül bileşeni) ya da formülün dışında (kalın metin) verilir.
3. İndis ve üs hep süslü parantezle: `P_{X}`, `E^{d}` (`P_X` ham görünür).
4. Kesrin içine kesir koyma (ara değeri ayrı blokta tanımla); `\left( \right)` yok, düz `( )`; kesirden sonra `\times 100` getirme (tablette paydaya kayar), çarpanı payın içine al.
5. Para birimi için `$` ya da `\$` yazma ("50 dolar"); tek `$` aynı satırdaki bütün formülleri bozar.
6. Rahat çalışanlar: `\dfrac`, `^{}`, `_{}`, `\times`, `\cdot`, `\approx`, `\le`, `\ge`, `\neq`, `\Delta`, Yunan harfleri, `\sqrt`, `\ln`, `\%`, `\text{}`.
7. Gönderdikten sonra kontrol et; bozuksa mesajı düzelt (edit).

Doğru örnek (ara değer ayrı blokta, çarpan payın içinde): `$$Q_{avg} = \dfrac{Q_{1} + Q_{2}}{2}$$` sonra `$$\text{Değişim} = \dfrac{(Q_{2} - Q_{1}) \times 100}{Q_{avg}} \%$$`.

## Teyit bekleyen (kural değil, ihtiyat; araç UYARI verir)
`\,` `\;` `\!`, rakamla başlayan satır içi formül, formülden hemen sonra kesme işareti (`$X$ matrisinin` yaz), `bmatrix`/`aligned`/`\sum` bloğu (ilk kullanışta görünüşü sor), telefonda sığmayan uzun denklem (satırlara böl).

Çekirdek §4 ve alan katmanları (`alanlar/<alan>/kurallar.md`) formül biçimini bu dosyadan alır; çelişkide bu dosya kazanır. Yeni komut ham görünürse buraya ve testteki `YASAK_KOMUT` listesine ekle.
