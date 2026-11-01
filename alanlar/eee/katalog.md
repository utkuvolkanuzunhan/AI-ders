# EEE widget kataloğu (W15+)

Çekirdek katalogdaki W01–W12 şablonları EEE'de de kullanılır. W13 (kimyasal yapı) ve W14 (etken kartları) gıdaya özgüdür, EEE sohbetleri kullanmaz. Aşağıdakiler EEE içindir; kural aynıdır: şablonu kopyala, yalnız veriyi değiştir.

Şablon henüz yok; ilk EEE şablonları W15 (eleman sembol kartı) ve W16 (devre şeması) olarak eklenecek. Eklenene kadar aşağıdaki iki tür de stil rehberine göre sıfırdan yazılır.

## Şablonu olmayan EEE türleri
Stil rehberine göre sıfırdan yazılır, iyi çıkarsa şablona eklenir (gorevler/kural-guncelle.md, galeri için `python3 araclar/uret.py`).

| Tür | Ne zaman | Ders |
|---|---|---|
| Eleman sembol kartı (W15 olacak): ad TR + EN, harf, birim, sembol | Eleman, bileşen ya da kapı adı geçince (alan kuralları §1) | hepsi |
| Devre şeması (W16 olacak): etiket, değer, gerilim kutbu, akım oku | Çözümlenecek devre | circuit-analysis-1, digital-systems |
| Dalga formu / tepki eğrisi (sabit eksen, kaydırıcı) | RC-RL basamak cevabı, sönüm durumları, $v(t)$ | circuit-analysis-1 |
| Doğruluk tablosu + kapı (girişe dokununca çıkış) | Kapılar, ifade sadeleştirme | digital-systems |
| Karnaugh haritası (gruplama) | Sadeleştirme | digital-systems |
| Durum diyagramı ve ASM şeması | Kontrol birimi tasarımı | digital-systems |
| Veri yolu / blok diyagram (W12 türevi) | Yazmaç transferi, CPU | digital-systems |
| Enerji bandı diyagramı (kaydırıcı: Fermi seviyesi, gerilim) | Yarıiletken, p-n eklemi, MOS | electronic-materials-device-physics |
| Matris satır işlemi (adım adım indirgeme) | Gauss–Jordan, determinant | linear-algebra |
| 2B vektör ve dönüşüm çizimi | Doğrusal dönüşüm, özvektör | linear-algebra |
| Sınıf diyagramı + kod yan yana | Sınıf, kalıtım, çok biçimlilik | object-oriented-programming |
| Serbest cisim diyagramı, kinematik grafik | Newton yasaları, hareket | physics-1 |
| Fazör diyagramı, Bode diyagramı | Sonraki dönem dersleri (devre analizi 2, sinyaller) | |

## Çizim kuralları (W15, W16 ve yeni EEE şemaları)
- Eleman sembolü kitap standardında, tel çizgisi `var(--text-primary)`, vurgu `--c1…--c5`. Akım oku dolu uçlu, gerilim kutbu "+" ve "−" işaretiyle.
- Etiket her zaman elemanın yanında (üstünde ya da yanında), değer birimiyle ($4{,}7\,\mathrm{k\Omega}$ gibi SVG içinde düz metin: `4,7 kΩ`).
- Referans (toprak) düğümü sembolü ve düğüm adları (a, b, c ya da v1, v2) çizilir; kesişen teller yalnız nokta varsa bağlıdır.
- SVG genişliği 560 viewBox, yazı 22 px (ekranda ≈ 14 px); telefonda 390 px'te taşma yok.

## Lineer Cebir ters matris şablonları (W21–W23)
Kural aynıdır: şablonu kopyala, yalnız veriyi değiştir. Veri `<script>` içindeki dizilerdir; üçü de 390 px dikeyde ve 844 px yatayda denendi.

| Şablon | Ne zaman | Veri |
|---|---|---|
| W21 elemanter matris, sekmeli | Elemanter matris, satır işleminin soldan çarpma olması, $E^{-1}$ | `D` (işlem adı, `E`, `A`, `EA`, `Ei`, değişen satırlar `hi`, not). 3×3; kesir hücresi `f1_2` yazılır |
| W22 Gauss–Jordan ile ters, adım adım | $[A\mid I]\to[I\mid A^{-1}]$ | `ST` (6 sütunlu matris, işlem, açıklama, değişen satır `b`, öncü `p`). Tekil örnek için sol yarıda sıfır satırla biten bir `ST` yaz |
| W23 denklik / ispat zinciri | Birbirini gerektiren ifadeler (tersinirlik denklikleri) | `D` (numara, ifade, kısa not, neden) |
