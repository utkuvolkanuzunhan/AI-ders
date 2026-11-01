---
alan: eee
---
# Ders kartı: Digital Systems · Sayısal Sistemler

Genel ders bilgisi (kişisel değil). İlerleme ve kişisel notlar kullanıcının proje klasöründe `dersler/digital-systems/hafiza.md`.

## Kaynak önceliği
yüklenen slayt / ders notu / lab föyü > ders kitabı > genel bilgi (ayar A4)

Kitap: Mano & Kime, *Logic and Computer Design Fundamentals* (2. basım). Yardımcı: Pedroni, *Circuit Design with VHDL*. Ders İngilizce işlenir; sınav İngilizcedir. Kapı sembolleri IEEE/ANSI şekilli kapılardır. Kitap bölüm numaraları basımdan basıma kaydığı için bu kartta bölüm adı/konu yazılır; numara gerekirse yüklenen PDF indeksinden alınır.

Ön bilgi (flip-flop, yazmaç, çoklayıcı, kod çözücü, sayıcı, 2'ye tümleyen) gerektiğinde kısa bir geri ipucuyla hatırlatılır, ayrı konu olarak anlatılmaz.

## Müfredat sırası
| # | Konu | Kitapta konu başlığı |
|---|---|---|
| 1 | Veri yolları ve yazmaç transferi; aritmetik, mantık ve öteleme mikroişlemleri | Registers and Register Transfers |
| 2 | Veri transfer çeşitleri, üç-durumlu hatlar, ortak yol (bus), ALU | Registers / Buses, ALU |
| 3 | Veri yolu gösterimi, kontrol kelimesi, zaman çoğullamalı veri yolu | Datapath, control word |
| 4 | Kontrol birimi, algoritmik durum makinesi (ASM), akış diyagramları | Sequencing and Control |
| 5 | İkili çarpıcı tasarımı, donanım bağlantılı kontrol, her duruma bir flip-flop | Sequencing and Control |
| 6 | Sıralama yazmaçları, kod çözücüler, HDL (VHDL, Verilog) | Sequence registers, HDL |
| 7 | Komutlar, komut formatları, tek çevrimli mikrobilgisayar | Computer Design Basics |
| 8 | Çok çevrimli mikroprogramlı kontrol, mikroprogram tasarımı | Microprogrammed control |
| 9 | Bilgisayar mimarisi kavramları: komut çevrimi, yazmaç kümesi, operand adresleme, 0/1/2/3 adresli komutlar | Instruction Set Architecture |
| 10 | Adresleme modları, komut kümesi, veri transfer komutları | Instruction Set Architecture |
| 11 | Yığın komutları, bağımsız ve bellek haritalı G/Ç, veri işleme, kayan nokta, program kontrol, kesme | ISA, Input-Output |
| 12 | CPU tasarımları, G/Ç ve haberleşme, bellek sistemleri | CPU, I/O, Memory Systems |

Lab konuları: FPGA kartı tanıtımı, VHDL ile yarım/tam/4 bit toplayıcı, 4 işlemli ALU, yukarı/aşağı sayıcı, bellek, yazmaç bankası, işlemci veri yolu, hafızalı veri yolu, tek vuruşlu işlemci. Araç ve kart adı lab föyünden alınır.

## Konu tipleri (ayar E3)
| Konu | Tip |
|---|---|
| Veri yolu ve mikroişlemler | kavram + tablo |
| Üç-durumlu hat, ortak yol, ALU | kavram |
| Kontrol kelimesi tasarımı | tasarım (hesap) |
| ASM ve kontrol birimi | tasarım + kavram |
| İkili çarpıcı, her duruma bir flip-flop | tasarım |
| VHDL | kod |
| Komut formatları, mikroprogramlı kontrol | ezber + tasarım |
| Adresleme modları, komut kümesi | kavram + hesap (etkin adres) |
| Yığın, G/Ç, kesme, kayan nokta | kavram + hesap |
| Bellek sistemleri | kavram + hesap (kapasite, adres hattı) |

## Notasyon ve birim
- Yazmaç transferi: $R2 \leftarrow R1$; kontrol koşulu ile $K_1: R2 \leftarrow R1$; mikroişlem $R0 \leftarrow R1 + R2$. Kitap notasyonuyla yaz.
- Sayılar: ikili ($1011_2$), onaltılık ($\mathrm{0x3F}$ ya da $3F_{16}$), 2'ye tümleyen; bit genişliği her zaman belirtilir. Kapasite: $2^{n}$ adres $\times$ $m$ bit.
- Üç-durumlu çıkış: `Z` yüksek empedans. ASM: durum kutusu (dikdörtgen), karar kutusu (eşkenar dörtgen), koşullu çıkış kutusu (oval).
- VHDL: `std_logic`, `std_logic_vector`, `entity`/`architecture`, `process`, sinyal atama `<=`, değişken atama `:=`, saat kenarı `rising_edge(clk)`. Kod blokları `vhdl` etiketiyle.
- IEEE 754 tek duyarlıklı: 1 işaret, 8 üs (kayık 127), 23 mantis (gizli 1).

## Sık tuzaklar
- Elde (carry) ile taşmayı (overflow) karıştırmak: işaretli toplamada taşma, son iki elde farklıysa olur.
- Birleşik (kombinasyonel) süreçte her koşulda atama yapılmazsa istenmeyen latch oluşur.
- VHDL'de sinyal ataması süreç sonunda geçerli olur, değişken ataması anında; bir süreçte sinyali atadıktan hemen sonra okuyup eski değeri görmek.
- Üç-durumlu olmayan ortak hatta iki sürücü: çakışma.
- Senkron ve asenkron reset farkı; saat kenarına duyarlı süreçte duyarlılık listesi.
- Mealy ve Moore çıkışları; ASM'de koşullu çıkış kutusunun hangisine karşılık geldiği.
- Adresleme modlarında "değer mi, adres mi?": anlık (immediate), doğrudan, dolaylı, yazmaç dolaylı, indisli; etkin adres hesabı.
- Yığın işaretçisi artan mı azalan mı büyür; push ve pop sırası.
- Büyük/küçük sonlu (endian) bayt sırası; kayan noktada üs kayığı ve gizli bit.

## Uygulama örnek havuzu
Trafik ışığı denetleyici (ASM/FSM), asansör kontrolü, dijital saat ve 7 segment sürücü, UART alıcısı, tuş takımı tarayıcı, sade bir CPU (SAP tarzı), mikrodenetleyicide kesme ile tuş okuma, bellek haritalı G/Ç ile LED sürme.
