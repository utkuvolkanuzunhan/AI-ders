# EEE widget kataloğu (W15+)

Çekirdek katalogdaki W01–W12 şablonları EEE'de de kullanılır. W13 (kimyasal yapı) ve W14 (etken kartları) gıdaya özgüdür, EEE sohbetleri kullanmaz. Aşağıdakiler EEE içindir; kural aynıdır: şablonu kopyala, yalnız veriyi değiştir.

| Kimlik | Tür | Ne zaman | Dosya |
|---|---|---|---|
| W15 | Eleman sembol kartı | Eleman, bileşen ya da kapı adı geçince: ad (TR + EN), harf sembolü, birim ve çizim birlikte (alan kuralları §1) | sablonlar/W15-eleman-sembol-karti.html |
| W16 | Devre şeması + göz akımı sekmeleri | Göz akımı çözümü: eleman etiketi ve değeri, kaynak kutbu, toprak, göz akımı oku; sekmelerle KGY denklemi ve Gauss çözümü. İki gözlü direnç-kaynak örneği; değerler ve etiketler veridir, topoloji değişirse çizim yapı değişikliğidir ve ekran testi ister | sablonlar/W16-devre-sema-goz-akimi.html |
| W17 | Matris satır işlemi, adım adım indirgeme | Gauss ve Gauss–Jordan; `M0` ve `ST` veridir | sablonlar/W17-matris-satir-islemi.html |
| W20 | Devre şeması | Çözümlenecek devre: eleman etiketleri, gerilim kutupları, akım okları; elemana dokununca açıklama ve ilgili yasa | sablonlar/W20-devre-semasi.html |

Semboller W15'teki `SYM` sözlüğünde durur (zikzak direnç, kondansatör, bobin, diyot, gerilim kaynağı, op-amp, VE ve DEĞİL kapıları). W20 aynı çizim biçimini kullanır; yeni bir sembol gerekirse önce W15'e eklenir, sonra W20'ye kopyalanır. Semboller kitap standardındadır (alan kuralları §1). W15'te yoksa (akım kaynağı, VEYA, BJT, MOSFET, flip-flop) aynı koordinat düzeninde yeni giriş yazılır ve iyi çıkarsa şablona eklenir. W18, W19 ve W21–W23 Lineer Cebir şablonlarıdır, aşağıda.

## Şablonu olmayan EEE türleri
Stil rehberine göre sıfırdan yazılır, iyi çıkarsa şablona eklenir (gorevler/kural-guncelle.md, galeri için `python3 araclar/uret.py`).

| Tür | Ne zaman | Ders |
|---|---|---|
| Dalga formu / tepki eğrisi (sabit eksen, kaydırıcı) | RC-RL basamak cevabı, sönüm durumları, $v(t)$ | circuit-analysis-1 |
| Doğruluk tablosu + kapı (girişe dokununca çıkış) | Kapılar, ifade sadeleştirme | digital-systems |
| Karnaugh haritası (gruplama) | Sadeleştirme | digital-systems |
| Durum diyagramı ve ASM şeması | Kontrol birimi tasarımı | digital-systems |
| Veri yolu / blok diyagram (W12 türevi) | Yazmaç transferi, CPU | digital-systems |
| Enerji bandı diyagramı (kaydırıcı: Fermi seviyesi, gerilim) | Yarıiletken, p-n eklemi, MOS | electronic-materials-device-physics |
| Matris satır işlemi, adım adım indirgeme (W17) | Gauss–Jordan, determinant | linear-algebra |
| 2B vektör ve dönüşüm çizimi | Doğrusal dönüşüm, özvektör | linear-algebra |
| Sınıf diyagramı + kod yan yana | Sınıf, kalıtım, çok biçimlilik | object-oriented-programming |
| Serbest cisim diyagramı, kinematik grafik | Newton yasaları, hareket | physics-1 |
| Fazör diyagramı, Bode diyagramı | Sonraki dönem dersleri (devre analizi 2, sinyaller) | |

## Çizim kuralları (W15, W20 ve yeni EEE şemaları)
- Eleman sembolü kitap standardında, tel çizgisi `var(--text-primary)`, vurgu `--c1…--c5`. Akım oku dolu uçlu, gerilim kutbu "+" ve "−" işaretiyle.
- Etiket her zaman elemanın yanında (üstünde ya da yanında), değer birimiyle ($4{,}7\,\mathrm{k\Omega}$ gibi SVG içinde düz metin: `4,7 kΩ`).
- Referans (toprak) düğümü sembolü ve düğüm adları (a, b, c ya da v1, v2) çizilir; kesişen teller yalnız nokta varsa bağlıdır.
- SVG genişliği 560 viewBox, yazı 22 px (ekranda ≈ 14 px); telefonda 390 px'te taşma yok.

## Lineer Cebir matris şablonları (W18, W19) ve matris çizim kısayolu
Kural aynıdır: şablonu kopyala, yalnız veriyi değiştir. Veri `<script>` başındaki dizilerdir.

| Şablon | Ne zaman | Veri |
|---|---|---|
| W18 matris çarpımı etkileşimli | Matris çarpımı, $c_{ij}$ hesabı, boyut kuralı | `A`, `B` (örnek 2×3 · 3×2). Boyut değişirse 390 px'te taşmayı ekran testiyle bak |
| W19 $A\mathbf{x}=\mathbf{b}$ iki bakış | Matris denklemi, sistemin matris yazılışı, sütunların doğrusal birleşimi | `A` (3×3), `V` değişken adları, `S` çözüm, `Bv` sağ taraf; `Bv` = `A·S` olmalı |

Matris çizimi (W06, W08, W09, W10 türevi widget'lar): metne `<i data-mx="1 2;3 4"></i>` yaz (satırlar `;`, sütunlar boşlukla ayrılır). Widget'ın betiği `conv(root)` ile bunu köşeli parantezli `.mx` ızgarasına çevirir. Köşeli parantez iki yan kenarlıktır, `bmatrix` yazımı yoktur; yazı boyutu 15 px, hücre aralığı `2px .6em`, 390 px'te dört sütuna kadar sığar.

## Lineer Cebir ters matris şablonları (W21–W23)
Kural aynıdır: şablonu kopyala, yalnız veriyi değiştir. Veri `<script>` içindeki dizilerdir; üçü de 390 px dikeyde ve 844 px yatayda denendi.

| Şablon | Ne zaman | Veri |
|---|---|---|
| W21 elemanter matris, sekmeli | Elemanter matris, satır işleminin soldan çarpma olması, $E^{-1}$ | `D` (işlem adı, `E`, `A`, `EA`, `Ei`, değişen satırlar `hi`, not). 3×3; kesir hücresi `f1_2` yazılır |
| W22 Gauss–Jordan ile ters, adım adım | $[A\mid I]\to[I\mid A^{-1}]$ | `ST` (6 sütunlu matris, işlem, açıklama, değişen satır `b`, öncü `p`). Tekil örnek için sol yarıda sıfır satırla biten bir `ST` yaz |
| W23 denklik / ispat zinciri | Birbirini gerektiren ifadeler (tersinirlik denklikleri) | `D` (numara, ifade, kısa not, neden) |
