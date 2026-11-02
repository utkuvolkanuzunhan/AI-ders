# Sohbet mesajlarında formül yazımı

**Belirti:** Mesajdaki formül çizilmez, ham LaTeX kodu görünür (`\Large \boldsymbol{...}` gibi) ya da kesir/indis bozulur.
**Not:** Widget (HTML) içindeki formül bu dosyanın dışındadır; kurallar sohbet mesajı metni içindir.
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
7. **Liste ve tabloda satır içi `$...$` yok:** madde (`-`, `1.`) ve tablo (`|`) satırında `$dt$` ham görünür. Düz metin yaz (dt, Δt, x², v₀) ya da listeyi böl: madde cümlesi, boş satır, ayrı `$$` bloğu, sonraki madde numarasıyla devam (`2.`). Listenin ya da tablonun içine `$$` bloğu da konmaz.
8. **Kesin kural, kodla zorlanır:** her mesaj gönderilmeden önce taslak bir dosyaya yazılır ve `python3 /tmp/ai-ders/araclar/formul_denetle.py taslak.md` çalıştırılır. `HATA` varsa mesaj gönderilmez; düzeltilir ve yeniden denetlenir. `UYARI` kural değil ihtiyattır (aşağıdaki "Teyit bekleyen"). Denetleyici yukarıdaki kuralların hepsini kontrol eder: yasaklı komutlar, süslü parantezsiz indis/üs, iç içe kesir, kesirden sonra `\times`, bir blokta çok denklem, `$$` bloğunun kendi satırında ve boş satırlar arasında olması, liste/tablo satırında `$`, para için `$`. Yeni bir kural eklenince denetleyiciye de (testiyle: `--test`) eklenir.
9. **Gönderdikten sonra da bak;** bozuk formül görünürse mesajı düzelt (edit) ve nedenini bu dosyaya yaz.

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
- Matris (`bmatrix`), `aligned`, `\sum` içeren çıplak `$$` blokları: bir ekran görüntüsünde sorunsuz görüldü, ama tek örnek; ilk kez kullanılırken görünüşü sor.
- Telefon genişliği (içerik ≈ 340 px): uzun denklem tek satıra sığmazsa satırlara böl, her `$$` bloğunda tek matris.

## Bu kurala bağlı yerler
Çekirdek `cekirdek/temel.md` §4 ve alan katmanları (`alanlar/<alan>/kurallar.md`) formül biçimini bu dosyadan alır; çelişki olursa bu dosya kazanır. Yeni bir komut ham görünürse buraya ekle, başka yere yazma.
