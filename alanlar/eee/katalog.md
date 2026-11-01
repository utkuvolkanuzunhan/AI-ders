# EEE widget kataloğu (W15+)

Çekirdek katalogdaki W01–W12 şablonları EEE'de de kullanılır. W13 (kimyasal yapı) ve W14 (etken kartları) gıdaya özgüdür, EEE sohbetleri kullanmaz. Aşağıdakiler EEE içindir; kural aynıdır: şablonu kopyala, yalnız veriyi değiştir.

| Kimlik | Tür | Ne zaman | Dosya |
|---|---|---|---|
| W15 | Eleman sembol kartı | Eleman, bileşen ya da kapı adı geçince: ad (TR + EN), harf sembolü, birim ve çizim birlikte (alan kuralları §1) | sablonlar/W15-eleman-sembol-karti.html |
| W16 | Devre şeması | Çözümlenecek devre: eleman etiketleri, gerilim kutupları, akım okları; elemana dokununca açıklama ve ilgili yasa | sablonlar/W16-devre-semasi.html |

Semboller W15'teki `SYM` sözlüğünde durur (zikzak direnç, kondansatör, bobin, diyot, gerilim kaynağı, op-amp, VE ve DEĞİL kapıları). W16 aynı çizim biçimini kullanır; yeni bir sembol gerekirse önce W15'e eklenir, sonra W16'ya kopyalanır. Semboller kitap standardındadır (alan kuralları §1). W15'te yoksa (akım kaynağı, VEYA, BJT, MOSFET, flip-flop) aynı koordinat düzeninde yeni giriş yazılır ve iyi çıkarsa şablona eklenir.

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
