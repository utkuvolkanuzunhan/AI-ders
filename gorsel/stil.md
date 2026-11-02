# Görsel stil: widget kuralları

Anlatım yapan roller okur. Hazır şablonlar: `gorsel/sablonlar/` (kimlikler ve ne zaman kullanılacağı: `gorsel/katalog.md`). Yeni widget'ı şablondan türet, sıfırdan yazma. Anlatım widget'larının referans uygulaması **W25** (karma tasarım, bileşen sınıfları ve CSS hazır), soruların referansı **W10 / W24** (çizgili).

## 1. Kalite çıtası: sade, net, bol boşluklu
- Ölçüt "az parça, net sıra": kalın renkli çerçeve + renkli dolgu + çok renk birlikte "karmaşık" görünür ve yasaktır. Bir widget = bir fikir; her parçanın tek işi var.
- Hiyerarşi yazıyla kurulur (boyut ve kalınlık), kutu ve renkle değil. Önce başlık/soru, sonra gövde, sonra soluk açıklama.
- Yazmadan önce `dataviz` ve `artifact-diagramming` becerilerini yükle (grafik ve şema içeren widget'larda zorunlu).
- Kitaptaki/slayttaki şekil, tablo ve grafikleri numarasıyla yeniden çiz.

## 2. Yüzey seviyeleri (kullanıcı kararı, 2 Kasım 2026): anlatım karma, sorular çizgili
Her parça şu dört yüzeyden birinde durur (W25'te sınıf adları):

| Sınıf | Yüzey | Nerede |
|---|---|---|
| `z0` | **Çizgi**: arka plan yok, 1 px ince çizgi ya da 3–4 px renkli çizgi (kartın üstü, açıklamanın solu) | Varsayılan akış: sekmeler, kart akışı, çipler, not, adım listesi, **bütün test soruları** |
| `z1` | **Gri zemin** (`var(--surface-1)`), köşe 16 px | Üzerinde çalışılan nesne: formül, hesap adımları, işaret kartı, açıklama kutusu |
| `z2` | **Derin renkli zemin** (`--d`, beyaz yazı) | Sayfanın en önemli 1–2 parçası: ana kural, sonuç sayısı, vurgulu not, cevap bandı |
| `zp` | **Pastel zemin** (`--p`) | Seyrek; yalnız açıklama kutusu ya da çip. Pastel yerine derin ton tercih edilir |

Kurallar:
- Bir widget'ın ilk ekranında çoğu parça `z0` ya da `z1`; `z2` en çok 2 parça; `zp` en çok 1. Aynı widget'ta yüzeyler karışır ama düzenli: aynı tür parça hep aynı yüzeyde (ör. formül hep `z1`, not hep `z2` ya da `z0`).
- **İşaret ve hesap bölümü**: gri zemin (`z1`), belirgin ve büyük. Hesap satırı en az 22 px / 600, her satırın altında 15 px soluk açıklama, işaret büyük renkli daire içinde (`.sn`), sonuç en az 34 px / 800 derin renkli kartta (`.rz`).
- **Test soruları (mini test, tam test, soru seti)**: yalnız çizgili. Gri ya da renkli kutu şık yok; yalnız cevaptan sonra doğru ve seçilen yanlış şık renklenir.
- Dört yanı kalın çerçeveli kutu yok. Çerçeve ya 1 px (çipler, düğmeler) ya da tek kenar (3–5 px sol çizgi).
- Bir fikir bir yüzeyde: kutu içinde kutu yok.

## 3. Yerleşim
- Her anlatılan küçük parçanın hemen altında kendi widget'ı; başa az sona çok yığılmaz.
- Her widget altında "Ne yapacaksın, ne göreceksin" en çok 2 kısa cümle (15 px, `var(--text-secondary)`).
- Widget, mesajdaki sayıların aynısını kullanır.
- Kaynak satırı widget'ın içine yazılmaz (ayar D1). D2/D3'te mesajın altında durur.
- Çeşitlilik: bir konuda en az 4 farklı widget türü; art arda iki widget aynı türde olmaz; kaydırıcılı widget toplamın en fazla üçte biri; karşılaştırma gereken her yerde tablo (W08). Konu başında 4–6 widget'lık plan çıkar.

## 4. Renk paleti
Tema değişkenleri (yazı, panel, çizgi) hep `var(--text-primary)`, `var(--text-secondary)`, `var(--surface-1)`, `var(--border)`; yazı ya da zemin için sabit hex yazma. Arka plan şeffaf. Vurgu renkleri altı derin ton; her renk dört biçimde kullanılır:

| Sınıf | Renk | `--c` orta (çizgi, nokta, halka, ikon) | `--d` derin (dolu zemin, beyaz yazı) | `--l` açık (derin zeminde alt çizgi) | Anlam |
|---|---|---|---|---|---|
| `k1` | indigo | `#6F82E6` | `#4C5FD5` | `#D5DAFF` | ana vurgu, seçili, bilgi |
| `k2` | turkuaz yeşil | `#45B39D` | `#0F7B70` | `#B3EFE2` | doğru, olumlu, artış |
| `k3` | amber | `#E0924A` | `#B85A14` | `#FFD9B3` | yanlış, dikkat, tuzak |
| `k4` | mor | `#A468D1` | `#8B4DB8` | `#E6D0F7` | ipucu, ek bilgi |
| `k5` | gül | `#D9587F` | `#C23B63` | `#FFCBDB` | beşinci kavram |
| `k6` | camgöbeği | `#2A9CC7` | `#1C7FA6` | `#B9E6F7` | altıncı kavram |

- Pastel `--p` = orta tonun %18 saydamı; seyrek (§2).
- Aynı kavram widget'lar arasında aynı rengi korur (ör. fiyat hep k3, miktar hep k2). Kavram başına renk, rastgele süs rengi yok; ilk ekranda en çok 4 farklı renk.
- Orta ton (`--c`) yalnız çizgi, nokta, halka, ikon ve alt çizgi içindir. Renkli yazı yalnız derin zeminde beyazdır; zemini tema olan yerde yazı tema renginde kalır.
- Doğru = `#45B39D` (işaret) / `#0F7B70` (dolu), yanlış = `#E0924A` / `#B85A14`; renk tek başına anlam taşımaz (ikon + yazı).
- Neon, çok parlak ve soluk renk yok. Her ikisi (koyu, açık tema) denenir.

## 5. Yazı, boşluk, dokunma
| Parça | Boyut / kalınlık |
|---|---|
| Test sorusu (İngilizce) | 22 px / 700, satır 1,4 |
| Test sorusu Türkçesi | 16 px normal, soluk, parantez içinde, **ayrı satırda** (italik ve kalın değil) |
| Şık: İngilizce | 17–18 px / 600; Türkçesi altında 15–16 px soluk, parantezli |
| Gövde | 16 px, satır 1,5 |
| Kart başlığı / açıklama başlığı | 17–19 px / 700 |
| Etiket (`.lb`, soru no, bölüm adı) | 14 px / 600 soluk |
| Hesap satırı | 22 px / 600 |
| Sonuç kartı | 34 px / 800 |
| Formül | 30 px (kesir ve üs doğru yerde) |

Hiçbir yazı 13 px'ten küçük olmaz (üs/alt indis dahil: `.sb` 0,86 em).
- Boşluk: bölümler `.lb` etiketiyle ayrılır, üstünde 26 px; sorular arası 24–26 px; şık satırı en az 72 px (geniş ekranda 92); kartlar arası 10 px; çizgiyle ayrılan satırlarda iç boşluk 16 px. Dar dar sıkışık görünüm yok: iki parça arası en az 10 px.
- Dokunma hedefi en az 44 px yüksek, düğme 54 px.
- Düğme için `<button>` KULLANMA: sohbet kendi düğme stilini basıp rengini siliyor. `<div role="button" tabindex="0">`.
- Her widget kökünde `-webkit-text-size-adjust:100%; text-size-adjust:100%`.
- Widget kökü `max-width:760px; margin:0 auto`.

### Geniş ekran (tablet yatay, telefon yatay)
`@media(min-width:600px)` ile: **şıklar 2×2** (iki sütun, aralarında 28 px; dar ekranda 1×4 kalır); şık satırı 92 px; düğmeler tam genişlikte uzayıp ince-uzun olmaz (`max-width` 260–520 px, ortalı); sekmeler `flex:none; min-width:200px`; kart akışı en çok 320 px kart. Test: 1180×820 yatay görüntü.

## 6. Test arayüzü (W10, W24, W25'in mini testi)
- Soru ve şıklar İngilizce, Türkçesi parantezli ve ayrı satırda (motor sondaki parantezi ayırır; veride `"English (Türkçe)"` yazılır).
- Şık satırı: sol harf (soluk, 20 px / 800), ortada İngilizce kalın + Türkçe soluk, sağda (cevaptan sonra) ✓ ya da ✕ ikonu. Harf başına renk yok.
- Cevaptan sonra: doğru satır `rgba(69,179,157,.14)` zemin + 5 px yeşil sol çizgi, seçilen yanlış turuncu aynı biçimde, ötekiler %50 soluk. Altında renkli ikonlu "Doğru" / "Yanlış · doğru cevap: B" satırı, onun altında 3 px sol çizgili açıklama.
- İpucu: 1 px çerçeveli hap düğme; açılınca sol çizgili metin.
- 1 soru: tek soru. 2–3 soru: alt alta mini test, sonda büyük "x / n". 4+ soru: tek tek, üstte segmentli ilerleme şeridi, "Sonraki soru" düğmesi, sonda halka ve numaralı sonuç çipleri.
- Soruda, şıkta ve etikette konu adı, adım ya da sayfa numarası yok (ayarlar karışık test); konu yalnız açıklamada geçer.

## 6b. Formül widget'ı (W01, W25 `.fm`)
- Kesir `.fr` yapısıyla (pay, çizgi, payda), hiçbir zaman "a/b". Üs/alt indis `.sb` (yukarı kaydırılmış, 0,86 em); `<sup>` kullanma.
- Formül satırı ekrana sığan en büyük boyuta kendini ayarlar (14–110 px; W01), W25'te 30 px sabit.
- Her terim dokunulabilir: terimin altında 3 px kendi renginde alt çizgi; seçilince `--p` zemin. Kutu çerçevesi yok. Terim rengi açıklamadaki çizgi/nokta ile aynı.
- Açıklama (`.dt`) 17 px başlık + 16 px soluk metin; ilk hali ilk terimin açıklaması (boş kutu yok).

## 7. Grafik (W03, W04)
- Eksenler SABİT: aralık önceden seçilir, kaydırıcıyla değişmez; eğri `clipPath` ile kırpılır.
- Eksen başlıkları ve birimleri yazılı, tüm değerler okunur. Üst boşluk 30 px, eksen etiketi en üst sayıyla çakışmaz. Çizgi 3 px, nokta yarıçapı 7–8, tek vurgulu nokta turuncu, noktalı kılavuz.
- Dolgu `fill-opacity` .14–.25 + 3 px çizgi; yazı dolgunun üstüne bindirilmez.
- Grafiğin altında 1–2 cümle: yatay ne, dikey ne, sağa/yukarı gidince ne olur, nasıl okunur.

## 7b. Kimyasal yapı (W13)
- Ad (İngilizce kalın, Türkçe soluk) ve formül yazısı her zaman çizimin yanında; organik kimyayı okumakta zorlanan kişi adı doğrudan görür.
- Atom renkleri sabit: N `--c1`, O `--c5`, C `--text-primary`, H ve R `--text-secondary`. Çift bağ iki paralel çizgi, bağlar atom harfine değmez.
- Grubun kendisi kesikli renkli halkanın içinde, molekülün geri kalanı R ile gösterilir. Kaynakta yapı çizimi varsa onu yeniden çiz.

## 8. Teknik
- Script: IIFE, `document.getElementById`, sade `var`/`function`. Dış kütüphane yok (KaTeX yüklenmez, kesirler CSS ile).
- Yeniden boyutlandırma JS'te yalnız `window.resize`'da ve genişlik ≥ 24 px değişince. `ResizeObserver` ve `setInterval` YOK (git-gel hatası). CSS `@media` serbest.
- `html,body{overflow:hidden}`. Animasyon ve geçiş yok; `color-mix` yok (iPad): saydam renk için `rgba`.
- Widget başlığı (title) kısa, kebab-case, 1–80 karakter.
- Emoji widget içinde kullanılmaz (ikon için SVG).

## 9. Gönderme öncesi kontrol listesi
- [ ] Telefon dikey (390×800), telefon/tablet yatay (844×390 ve 1180×820) taşma yok; geniş ekranda şıklar 2×2.
- [ ] Koyu ve açık temada okunur; yazı en az 13 px.
- [ ] Yüzey seviyeleri kurala uygun (§2): test çizgili; hesap gri ve büyük; `z2` en çok 2 parça.
- [ ] İlk ekranda en çok 4 renk; aynı kavram aynı renk; renkli yazı yalnız derin zeminde beyaz.
- [ ] Boşluk: sıkışık yer yok, bölümler `.lb` ile ayrılmış, ince-uzun düğme yok.
- [ ] Tıklanmış hal güzel görünüyor (kaybolma yok); altında "ne yapacaksın" cümlesi var, metindeki sayılarla aynı.
