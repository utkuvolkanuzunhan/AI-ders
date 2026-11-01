---
alan: eee
---
# Ders kartı: Circuit Analysis 1 · Devre Analizi 1

Genel ders bilgisi (kişisel değil). İlerleme ve kişisel notlar kullanıcının proje klasöründe `dersler/circuit-analysis-1/hafiza.md`.

## Kaynak önceliği
yüklenen slayt / ders notu / lab föyü > ders kitabı > genel bilgi (ayar A4)

Kitap: Nilsson & Riedel, *Electric Circuits* (10. basım). Yardımcı: Alexander & Sadiku, *Fundamentals of Electric Circuits*. Ders İngilizce işlenir; sınav İngilizcedir. Sembol standardı kitapla aynı: zikzak direnç, IEEE/ANSI gösterimi.

## Müfredat sırası (konu → Nilsson bölümü, 10. basıma göre)
| # | Konu | Kitap bölümü |
|---|---|---|
| 1 | Devre değişkenleri: gerilim, akım, güç, enerji; ideal eleman | 1 Circuit Variables |
| 2 | Bağımsız ve bağımlı kaynaklar, Ohm yasası, devre modeli | 2 Circuit Elements |
| 3 | Kirchhoff yasaları, bağımlı kaynaklı devreler | 2 Circuit Elements |
| 4 | Seri/paralel dirençler, gerilim ve akım bölücüler, (Wheatstone köprüsü, Δ–Y) | 3 Simple Resistive Circuits |
| 5 | Düğüm gerilimi ve göz akımı yöntemleri | 4 Techniques of Circuit Analysis |
| 6 | Bağımlı kaynaklı göz akımı, kaynak dönüşümü, Thévenin–Norton, süperpozisyon | 4 Techniques of Circuit Analysis |
| 7 | Maksimum güç transferi | 4 Techniques of Circuit Analysis |
| 8 | İşlemsel yükselteç (op-amp) | 5 The Operational Amplifier |
| 9 | Bobin, kondansatör, karşılıklı endüktans | 6 Inductance, Capacitance, and Mutual Inductance |
| 10 | Birinci derece RL ve RC devreleri (doğal ve basamak cevap) | 7 Response of First-Order RL and RC Circuits |
| 11 | RLC devreleri (doğal ve basamak cevap) | 8 Natural and Step Responses of RLC Circuits |

Lab konuları: Kirchhoff yasaları, bölücüler ve köprü devreleri, süperpozisyon, düğüm/göz yöntemleri, Thévenin–Norton ve maksimum güç, op-amp, RC–RL tepkileri, seri/paralel RLC. Bölüm numaraları 10. basıma göredir; farklı basımda kayabilir.

## Konu tipleri (ayar E3)
| Konu | Tip |
|---|---|
| Devre değişkenleri, güç ve enerji, işaret kuralı | kavram + hesap |
| Ohm yasası, kaynaklar, KAY/KGY, bağımlı kaynak | hesap |
| Seri/paralel, bölücüler, Δ–Y | hesap |
| Düğüm gerilimi, göz akımı | hesap (yöntem seçimi) |
| Thévenin–Norton, süperpozisyon, maksimum güç | hesap + kavram |
| Op-amp (ideal model) | kavram + hesap |
| Bobin, kondansatör, karşılıklı endüktans | kavram + hesap |
| Birinci derece RL/RC | hesap + grafik |
| RLC doğal ve basamak cevap | hesap + grafik |

## Notasyon ve birim
- Pasif işaret kuralı: akım elemanın + ucundan girerse $p = vi$ elemanın soğurduğu güçtür; $p<0$ ise eleman güç verir. Çözümün başında bir kez yaz.
- $v = iR$; $R_1\parallel R_2 = \dfrac{R_1R_2}{R_1+R_2}$; gerilim bölücü $v_k = v_s\dfrac{R_k}{R_1+\cdots+R_n}$; iki dirençli akım bölücü $i_1 = i_s\dfrac{R_2}{R_1+R_2}$.
- Thévenin: $V_{Th}=v_{oc}$, $R_{Th}=\dfrac{v_{oc}}{i_{sc}}$; maksimum güçte $R_L=R_{Th}$ ve $p_{max}=\dfrac{V_{Th}^2}{4R_{Th}}$.
- İdeal op-amp: $i_+=i_-=0$; negatif geri beslemede $v_+=v_-$. Ters çeviren $v_o=-\dfrac{R_f}{R_i}v_i$, evirmeyen $v_o=\left(1+\dfrac{R_f}{R_i}\right)v_i$; çıkış $\pm V_{CC}$'de doyar.
- Bobin $v=L\dfrac{di}{dt}$, kondansatör $i=C\dfrac{dv}{dt}$; enerji $\tfrac{1}{2}Li^2$ ve $\tfrac{1}{2}Cv^2$. DC kararlı halde bobin kısa devre, kondansatör açık devre.
- Birinci derece genel çözüm: $x(t)=x_f+\left(x_0-x_f\right)e^{-(t-t_0)/\tau}$; $\tau_{RC}=RC$, $\tau_{RL}=\dfrac{L}{R}$ ($R$: eleman uçlarından görülen Thévenin direnci).
- RLC: $\omega_0=\dfrac{1}{\sqrt{LC}}$; paralel $\alpha=\dfrac{1}{2RC}$, seri $\alpha=\dfrac{R}{2L}$; $s_{1,2}=-\alpha\pm\sqrt{\alpha^2-\omega_0^2}$. $\alpha>\omega_0$ aşırı sönümlü, $\alpha=\omega_0$ kritik, $\alpha<\omega_0$ az sönümlü ($\omega_d=\sqrt{\omega_0^2-\alpha^2}$).
- Derste fazör ve Laplace yoktur (zaman uzayı); $j$ kullanma.

## Sık tuzaklar
- Pasif işaret kuralını unutup gücün işaretini ters yorumlamak.
- Akım bölücüde payda geçen kolun kendi direnci değil, DİĞER kolun direnci paya gelir.
- Kaynak söndürmede gerilim kaynağı kısa devre, akım kaynağı açık devre olur; bağımlı kaynak söndürülmez ($R_{Th}$ için test kaynağı ya da $\dfrac{v_{oc}}{i_{sc}}$).
- Süperpozisyon gerilim ve akımda geçerlidir; güçte uygulanmaz.
- Akım kaynağı ortak iki göz arasındaysa süper göz, gerilim kaynağı iki düğüm arasındaysa süper düğüm.
- Sanal toprak ($v_-=v_+$) yalnız negatif geri beslemede geçerlidir; doymuş op-amp için kullanılmaz.
- Anahtarlamada bobin akımı ve kondansatör gerilimi sıçramaz ($t=0^-$ ve $t=0^+$ ayrımı); bobin gerilimi ve kondansatör akımı sıçrayabilir.
- $\tau$ hesabında $R$ yanlış seçilir: bobin/kondansatör çıkarılıp uçlardan görülen eşdeğer direnç alınır.
- Önek dönüşümü: mH, $\mu$F, k$\Omega$ hesapta SI'ya çevrilir.
- Karşılıklı endüktansta nokta konumuna göre işaret.

## Uygulama örnek havuzu
LED akım sınırlama direnci, sensör (termistör/LDR) gerilim bölücüsü, Wheatstone köprüsüyle ölçüm, akünün iç direnci (Thévenin), adaptör–yük eşleşmesi (maksimum güç), mikrofon ön yükselticisi (op-amp), kamera flaşı (kondansatör şarjı), RC zamanlayıcı, röle bobini ve ark, ateşleme bobini.
