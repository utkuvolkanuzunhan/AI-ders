---
alan: eee
---
# Ders kartı: Electronic Materials and Device Physics · Elektronik Malzemeler ve Aygıt Fiziği

Genel ders bilgisi (kişisel değil). İlerleme ve kişisel notlar kullanıcının proje klasöründe `dersler/electronic-materials-device-physics/hafiza.md`.

## Kaynak önceliği
yüklenen slayt / ders notu / çıkmış soru > ders kitabı > genel bilgi (ayar A4)

Kitap: Streetman & Banerjee, *Solid State Electronic Devices* (7. basıma göre bölüm numaraları). Yardımcı: Pierret, *Semiconductor Device Fundamentals*. Ders İngilizce işlenir; sınav İngilizcedir. Bu derste uzunluk birimi çoğunlukla cm'dir (konsantrasyon $\mathrm{cm^{-3}}$, hareketlilik $\mathrm{cm^2/(V\cdot s)}$, enerji eV); SI'ya çevirmeden kitabın birimiyle hesapla.

## Müfredat sırası (konu → Streetman bölümü)
| # | Konu | Kitap bölümü |
|---|---|---|
| 1 | Kristal özellikleri, kristal kafes, Miller indisleri | 1 Crystal Properties and Growth of Semiconductors |
| 2 | Enerji bantları, yük taşıyıcıları, konsantrasyon, drift, Fermi fonksiyonu | 3 Energy Bands and Charge Carriers in Semiconductors (arka plan: 2 Atoms and Electrons) |
| 3 | Fazla taşıyıcılar: optik soğurma, luminesans, ömür, fotoiletkenlik, difüzyon, rekombinasyon, azınlık taşıyıcı difüzyon denklemi | 4 Excess Carriers in Semiconductors |
| 4 | p-n eklemi: denge, Fermi seviyesi, kontak potansiyeli, bant diyagramı, tükenme bölgesi | 5 Junctions |
| 5 | p-n eklemi ileri/ters besleme, akım, kapasitans, anahtarlama, ideal olmayanlar, metal–yarıiletken eklem | 5 Junctions |
| 6 | BJT: çalışma ilkesi, yükselteç, azınlık taşıyıcı dağılımı, bant diyagramı, anahtarlama, frekans sınırı | 7 Bipolar Junction Transistors |
| 7 | Alan etkili transistör: MOS yapısı, kanal kapanması (pinch-off), doyma, MOSFET, akım–gerilim | 6 Field-Effect Transistors |

Dikkat: müfredat BJT'yi FET'ten önce işler; kitapta FET (Bölüm 6) BJT'den (Bölüm 7) önce gelir. Anlatım müfredat sırasıyla yapılır.

## Konu tipleri (ayar E3)
| Konu | Tip |
|---|---|
| Kristal yapı, Miller indisleri | kavram + hesap |
| Enerji bantları, Fermi seviyesi | kavram + grafik |
| Taşıyıcı konsantrasyonu, katkılama | hesap |
| Drift, difüzyon, iletkenlik | hesap |
| Fazla taşıyıcılar, ömür, süreklilik denklemi | kavram + hesap |
| p-n eklemi denge ve bant diyagramı | kavram + grafik + hesap |
| p-n eklemi akım–gerilim, kapasitans | hesap + grafik |
| BJT | kavram + hesap |
| MOS yapısı ve MOSFET | kavram + grafik |

## Notasyon ve birim
- Enerji seviyeleri $E_c$, $E_v$, $E_g$, $E_F$, $E_i$; oda sıcaklığında $kT\approx 0{,}0259\,\mathrm{eV}$; Si için $n_i\approx 1{,}5\times10^{10}\,\mathrm{cm^{-3}}$ ve $E_g\approx 1{,}12\,\mathrm{eV}$ (diğer malzemelerin değerleri kitabın tablosundan).
- Termal denge: $n_0p_0=n_i^2$; $n_0=n_i\,e^{(E_F-E_i)/kT}$, $p_0=n_i\,e^{(E_i-E_F)/kT}$. Fermi–Dirac: $f(E)=\dfrac{1}{1+e^{(E-E_F)/kT}}$.
- Drift akım yoğunluğu $J=q\,(n\mu_n+p\mu_p)\,\mathcal{E}$; Einstein ilişkisi $\dfrac{D}{\mu}=\dfrac{kT}{q}$.
- p-n eklemi: kontak potansiyeli $V_0=\dfrac{kT}{q}\ln\dfrac{N_aN_d}{n_i^2}$; diyot denklemi $I=I_0\left(e^{qV/kT}-1\right)$.
- BJT: $I_C=\beta I_B$, $\beta=\dfrac{\alpha}{1-\alpha}$; çalışma bölgeleri: aktif, doyma, kesim, ters aktif.
- Bant diyagramında dikey eksen elektron enerjisidir (yukarı = elektron enerjisi artar, delik için ters); yatay eksen konumdur. Bant diyagramları yeniden çizilirken seviyeler etiketlenir ($E_c$, $E_F$, $E_v$) ve eğim yönü söylenir.

## Sık tuzaklar
- $n_0p_0=n_i^2$ yalnız termal dengede geçerlidir (ışık, ileri besleme vb. durumlarda değil).
- n-tipinde $E_F$ iletim bandına, p-tipinde değerlik bandına yakındır; katkı arttıkça $E_F$ banda yaklaşır.
- Drift (elektrik alanı) ile difüzyon (konsantrasyon farkı) ayrı; akımın yönü ile elektronun hareket yönü ters.
- İleri besleme: p tarafı pozitif, tükenme bölgesi daralır, bariyer $V_0-V$ olur; ters beslemede genişler.
- Azınlık ile çoğunluk taşıyıcıyı karıştırmak; düşük enjeksiyon varsayımı.
- Miller indisleri: kesişimlerin tersi alınır, en küçük tam sayılara çevrilir, negatif indis üstü çizgiyle yazılır.
- BJT aktif bölge: emitör–taban ileri, kolektör–taban ters; doymada ikisi de ileri.
- MOSFET'te kanal kapanması (pinch-off) akımın kesilmesi değil, doyma başlangıcıdır; eşik gerilimi $V_T$.
- cm ve m birimlerini karıştırmak; eV ile J dönüşümü.

## Uygulama örnek havuzu
LED ve lazer diyot (doğrudan bant aralığı), güneş pili ve fotodiyot (fazla taşıyıcı), diyotlu doğrultucu, diyotla sıcaklık algılama, BJT ile röle/LED anahtarlama, MOSFET ile motor sürme, CMOS evirici, ışığa duyarlı direnç (fotoiletkenlik).
