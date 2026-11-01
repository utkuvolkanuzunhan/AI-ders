# Görsel stil: widget kuralları

Anlatım yapan roller okur. Hazır şablonlar: `gorsel/sablonlar/` (kimlikler ve ne zaman kullanılacağı: `gorsel/katalog.md`). Yeni widget'ı şablondan türet, sıfırdan yazma.

## 1. Kalite çıtası
- Az ama cilalı, hoş ve renkli. "Düz kutu" ve özensiz çizim gönderilmez (kullanıcı geri bildirimi: "kaliteler düşük", "bu görsel çok çirkin").
- Yazmadan önce `dataviz` ve `artifact-diagramming` becerilerini yükle (grafik ve şema içeren widget'larda zorunlu).
- Görsel zenginlik araçları: renkli başlık şeridi (`color-mix(... 30%)`), seçilince hafif parlama (`box-shadow:0 0 0 4px color-mix(...30%)`) ve 2 px yukarı kalkma, kategori ikonları (emoji ya da basit SVG), kenar şeridi (`border-left:6–8px solid var(--c)`), yuvarlak köşe 12–16 px.
- Kitaptaki/slayttaki şekil, tablo ve grafikleri numarasıyla yeniden çiz.

## 2. Çeşitlilik
- Bir konuda en az 4 farklı widget türü; art arda iki widget aynı türde olmaz.
- Kaydırıcılı widget toplamın en fazla üçte biri.
- Karşılaştırma gereken her yerde tablo (W08).
- Konu başında 4–6 widget'lık plan çıkar (hangi adıma hangi tür), tekrarı kontrol et.

## 3. Yerleşim
- Her anlatılan küçük parçanın hemen altında kendi widget'ı; başa az sona çok yığılmaz.
- Her widget altında "Ne yapacaksın, ne göreceksin" tek cümle (15 px, `var(--text-secondary)`).
- Widget, mesajdaki sayıların aynısını kullanır.
- Kaynak satırı widget'ın içine yazılmaz (ayar D1). D2/D3'te mesajın altında durur.

## 4. Tema ve renk
- Arka plan şeffaf. Yazı `var(--text-primary)`, soluk `var(--text-secondary)`, panel `var(--surface-1)`, çizgi `var(--border)`. Yazı ya da zemin için sabit hex YAZMA.
- Vurgu renkleri ayar H'deki paletten, şablonlarda `--c1 … --c5` değişkenleri. Neon yok, soluk da yok.
- Doğru = `--c2` (yeşil-mavi), yanlış/uyarı/sonuç = `--c3` (turuncu).

## 5. Yazı ve dokunma
- En küçük yazı 13 px (etiket). Açıklama 15 px, gövde 16–17 px, başlık 18–22 px. SVG içindeki yazılar viewBox 560 genişlikte 22 px (ekranda ≈ 14 px).
- Dokunma hedefi en az 44 px yüksek.
- Düğme için `<button>` KULLANMA: sohbet kendi düğme stilini basıp rengini siliyor. `<div role="button" tabindex="0">` kullan.
- Her widget kökünde `-webkit-text-size-adjust:100%; text-size-adjust:100%` (telefon yan çevrilince yazı büyüyüp kutular küçük kalmasın).

## 6. Formül widget'ı (W01)
- Kesir `.fr` yapısıyla (pay, çizgi, payda), hiçbir zaman "a/b".
- Üs `.eb` iki kolonlu grid ile ayrı yukarı yerde; `<sup>` kullanma.
- Formül satırı ekrana sığan en büyük boyuta kendini ayarlar (14–110 px). Dikeyde 30 px'in altına düşecekse iki satıra böl (sol taraf / sağ taraf). Hedef: dikey ≥ 30 px, yatay ≥ 48 px.
- Her terim dokunulabilir kutu: çerçeve renkli, dolgu %14, harf formülle aynı renk ve boyutta, kalın. Seçilince dolgu %40 + halka; siyaha dönmez.
- Açıklama kutusu 17 px, başlığı 19 px; ilk hali "Bir kutuya dokun 👆".

## 7. Grafik (W03, W04)
- Eksenler SABİT: aralık önceden seçilir, kaydırıcıyla değişmez; eğri `clipPath` ile kırpılır.
- Eksen başlıkları ve birimleri yazılı, tüm değerler okunur. Üst boşluk 30 px, eksen etiketi en üst sayıyla çakışmaz.
- Noktalar yarıçap 7–8, noktalı kılavuz çizgisi, etiket noktanın üstünde.
- Grafiğin altında 1–2 cümle: yatay ne, dikey ne, sağa/yukarı gidince ne olur, nasıl okunur.

## 8. Teknik
- Script: IIFE, `document.getElementById`, sade `var`/`function`. Dış kütüphane yok (KaTeX yüklenmez, kesirler CSS ile).
- Yeniden boyutlandırma yalnız `window.resize`'da ve genişlik ≥ 24 px değişince. `ResizeObserver` ve `setInterval` YOK (git-gel hatası).
- `html,body{overflow:hidden}`.
- Animasyon az; `prefers-reduced-motion` saygı.
- Widget başlığı (title) kısa, kebab-case, 1–80 karakter.

## 9. Gönderme öncesi kontrol listesi
- [ ] Telefonda dikey (390) ve yatayda (844) taşma yok (test zorunluluğu ayar G'de).
- [ ] Yazılar okunur, kutular harflerle orantılı, üsler binmiyor.
- [ ] Tıklanmış hal güzel görünüyor (siyaha dönme, kaybolma yok).
- [ ] Açık ve koyu temada okunur.
- [ ] Altında "ne yapacaksın" cümlesi var, metindeki sayılarla aynı.
