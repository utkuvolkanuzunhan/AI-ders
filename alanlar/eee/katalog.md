# EEE widget kataloğu (W15+)

Çekirdek katalogdaki W01–W12 şablonları EEE'de de kullanılır. W13 (kimyasal yapı) ve W14 (etken kartları) gıdaya özgüdür, EEE sohbetleri kullanmaz. Aşağıdakiler EEE içindir; kural aynıdır: şablonu kopyala, yalnız veriyi değiştir.

Hazır EEE şablonları: **W16** devre şeması + göz akımı sekmeleri (`sablonlar/W16-devre-sema-goz-akimi.html`; iki gözlü direnç-kaynak örneği, değerler ve etiketler veridir, topoloji değişirse çizim yapı değişikliğidir ve ekran testi ister) ve **W17** matris satır işlemi, adım adım indirgeme (`sablonlar/W17-matris-satir-islemi.html`; `M0` ve `ST` veridir). W15 (eleman sembol kartı) henüz yok; o ve aşağıdaki diğer türler stil rehberine göre sıfırdan yazılır.

## Şablonu olmayan EEE türleri
Stil rehberine göre sıfırdan yazılır, iyi çıkarsa şablona eklenir (gorevler/kural-guncelle.md, galeri için `python3 araclar/uret.py`).

| Tür | Ne zaman | Ders |
|---|---|---|
| Eleman sembol kartı (W15 olacak): ad TR + EN, harf, birim, sembol | Eleman, bileşen ya da kapı adı geçince (alan kuralları §1) | hepsi |
| Devre şeması (W16): etiket, değer, gerilim kutbu, akım oku | Çözümlenecek devre | circuit-analysis-1, digital-systems |
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

## Çizim kuralları (W15, W16 ve yeni EEE şemaları)
- Eleman sembolü kitap standardında, tel çizgisi `var(--text-primary)`, vurgu `--c1…--c5`. Akım oku dolu uçlu, gerilim kutbu "+" ve "−" işaretiyle.
- Etiket her zaman elemanın yanında (üstünde ya da yanında), değer birimiyle ($4{,}7\,\mathrm{k\Omega}$ gibi SVG içinde düz metin: `4,7 kΩ`).
- Referans (toprak) düğümü sembolü ve düğüm adları (a, b, c ya da v1, v2) çizilir; kesişen teller yalnız nokta varsa bağlıdır.
- SVG genişliği 560 viewBox, yazı 22 px (ekranda ≈ 14 px); telefonda 390 px'te taşma yok.
