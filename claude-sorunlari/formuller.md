# Sohbet mesajlarında formül yazımı

**Belirti:** Mesajdaki formül çizilmez, ham LaTeX kodu görünür (`\Large \boldsymbol{...}` gibi) ya da kesir/indis bozulur.
**Test:** 2 Kasım 2026, Claude uygulaması (tablet ve telefon). Aşağıdaki kurallar orada denenmiştir; bu dosya çekirdekteki ve alanlardaki eski formül kalıplarının önüne geçer.

## Kurallar
1. **Biçim:** Formül ya `$$...$$` bloğudur (kendi satırında, üstünde ve altında boş satır) ya da kısa satır içi `$...$`. Bir blokta tek denklem; çok denklem varsa her biri ayrı blok.
2. **Yazma, ham kod görünür:** `\Large`, `\LARGE`, `\boldsymbol`, `\mathbf`, `\boxed`, `\color`, `\displaystyle`, `\qquad`, `\quad`. Büyütmek için komut ekleme: `$$` bloğu zaten büyük çıkar. Renk, kalınlık ve vurgu gerekiyorsa formülde değil, widgetta (W01) ya da formülün dışında (kalın metin, ayrı satır) ver.
3. **İndis ve üs hep süslü parantezle:** `P_{X}`, `Q_{1}`, `E^{d}`. Süslü parantezsiz `P_X` ham görünür.
4. **Kesir:**
   - Kesrin içine kesir koyma; ara değeri ayrı blokta tanımla.
   - `\left( \right)` kullanma; düz `( )`.
   - Kesirden sonra `\times 100` getirme (tablette `× 100` paydaya kayar); çarpanı payın içine al.
5. **Para birimi için `$` ya da `\$` yazma**, "50 dolar" yaz. Tek bir `$` işareti aynı satırdaki bütün formülleri bozar.
6. **Rahat çalışanlar:** `\dfrac`, `^{}`, `_{}`, `\times`, `\cdot`, `\approx`, `\le`, `\ge`, `\neq`, `\Delta`, Yunan harfleri, `\sqrt`, `\ln`, `\%`, `\text{}`.
   Matris ve toplam da çalışır (2 Kasım 2026, Lineer Cebir): `$$A=\begin{bmatrix}3&-1&0\\2&5&4\end{bmatrix}$$` ve `$$c_{ij}=\sum_{k=1}^{n}a_{ik}b_{kj}$$` ham görünmeden çizildi. İz için `\text{tr}(A)`.
7. **Gönderdikten sonra kontrol et;** bozuk formül varsa mesajı düzelt (edit).

## Örnek
Yanlış (ara değer kesrin içinde, `\left`, `\times 100` dışarıda):

```
$$\Large \boldsymbol{\dfrac{Q_2 - Q_1}{\dfrac{Q_1 + Q_2}{2}} \times 100}$$
```

Doğru (ara değer ayrı blokta, çarpan payın içinde, indisler süslü parantezli):

```
$$Q_{avg} = \dfrac{Q_{1} + Q_{2}}{2}$$

$$\text{Değişim} = \dfrac{(Q_{2} - Q_{1}) \times 100}{Q_{avg}} \%$$
```

## Teyit bekleyen (kural değil, ihtiyat)
Aşağıdakiler tek bir gözlemden geldi; kesin kural sayılmaz. Güvenli yol: kullanma. Denenince yukarıya taşı ya da sil.
- `\,` `\;` `\!` boşluk komutları: bitişik yaz ya da `\cdot` / `\text{ }` kullan.
- Satır içi formülü rakamla başlatma (`${2}\times 3$`) ve formülden hemen sonra kesme işareti getirme (`$X$'nın` yerine `$X$ matrisinin`): `$` işaretinin para sanılması riskine karşı.
- `aligned` içeren `$$` blokları: denenmedi; blokta tek denklem kuralı zaten ayrı blok önerir, kullanma.
- Telefon genişliği (içerik ≈ 340 px): uzun denklem tek satıra sığmazsa satırlara böl, her `$$` bloğunda tek matris.

## Bu kurala bağlı yerler
Çekirdek `cekirdek/temel.md` §4 ve alan katmanları (`alanlar/<alan>/kurallar.md`) formül biçimini bu dosyadan alır; çelişki olursa bu dosya kazanır. Yeni bir komut ham görünürse buraya ekle, başka yere yazma.
