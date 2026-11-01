---
alan: eee
---
# Ders kartı: Object-Oriented Programming · Nesne Yönelimli Programlama (C++)

Genel ders bilgisi (kişisel değil). İlerleme ve kişisel notlar kullanıcının proje klasöründe `dersler/object-oriented-programming/hafiza.md`.

## Kaynak önceliği
yüklenen slayt / ders notu / lab kodu / çıkmış soru > ders kitabı > genel bilgi (ayar A4)

Kitap: Deitel & Deitel, *C++ How to Program* (9. basım, C++11); yardımcı: *C How to Program* (8. basım, "C'de ileri konular" için). Ders İngilizce işlenir; sınav İngilizcedir ve kod yazma/kod izleme içerir. Diller: C ve C++. Kod örnekleri standart C++ ile (g++ ile derlenebilir) yazılır; IDE ve derleyici ayrıntısı lab föyünden alınır. Kitap bölüm numaraları 9. basıma göredir.

## Müfredat sırası (konu → Deitel bölümü)
| # | Konu | Kitap bölümü |
|---|---|---|
| 1 | Giriş, C++ geliştirme ortamı (IDE) | 1 Introduction to Computers and C++ |
| 2 | C'de ileri konular: işaretçiler, diziler, yapılar, dinamik bellek | *C How to Program*: Pointers, Structures, File Processing |
| 3 | C'den C++'a geçiş: `cin`/`cout`, referanslar, `namespace`, `new`/`delete`, varsayılan argüman, fonksiyon aşırı yükleme, `string` | 2, 6, 8 |
| 4 | Sınıflar ve veri soyutlama: sınıf, nesne, üye fonksiyon, erişim belirteçleri, yapıcı, yıkıcı | 3 Introduction to Classes, Objects, and Strings |
| 5–6 | C++'da sınıflar: `const`, `friend`, `this`, `static`, bileşim, üye başlatma listesi, kopya | 9 Classes: A Deeper Look |
| 7 | Operatör aşırı yükleme | 10 Operator Overloading; Class string |
| 8 | Kalıtım | 11 Object-Oriented Programming: Inheritance |
| 9 | Çok biçimlilik ve soyut fonksiyonlar | 12 Object-Oriented Programming: Polymorphism |
| 10 | Dizge ve IO akışları | 13 Stream Input/Output; 19 Class string and String Stream Processing |
| 11 | Hata yakalama ve dosyalar | 17 Exception Handling; 14 File Processing |
| 12 | ATM vaka çalışması (UML ile nesne yönelimli tasarım ve gerçekleme) | Kitabın ATM vaka çalışması bölümleri |

Her hafta lab kodlama deneyi vardır; kod yazma sorularında önce tasarım (hangi sınıf, hangi üye), sonra kod.

## Konu tipleri (ayar E3)
| Konu | Tip |
|---|---|
| C'ye hızlı dönüş, C → C++ | kavram + kod |
| Sınıf, nesne, yapıcı/yıkıcı | kavram + kod |
| `const`, `friend`, `static`, bileşim | kavram + kod izleme |
| Operatör aşırı yükleme | kod + kural |
| Kalıtım, çok biçimlilik | kavram + kod izleme |
| Akışlar, dosya, istisna | kod + kavram |
| ATM vaka çalışması | tasarım (UML) + kod |

## Notasyon ve biçim
- Kod bloğu `cpp` etiketli, tam program (`#include`, `main`) olur; parça verirsen "..." ile işaretle. Çıktı koddan sonra ayrı blokta gösterilir. Nokta ondalık ayırıcıdır (kodda).
- Adlandırma Deitel tarzı: sınıf adı büyük harfle başlar (`Account`), üye fonksiyon küçük harfle (`getBalance`), veri üyesi `m_` ya da kitabın kullandığı biçimle. Tek tutarlı biçim seç.
- UML sınıf diyagramı: sınıf adı / veri üyeleri / üye fonksiyonlar bölmeleri; `+` public, `-` private, `#` protected. Ok türleri: kalıtım (içi boş üçgen), bileşim (dolu eşkenar dörtgen).
- Çıktı tahmini sorularında satır satır izleme tablosu (değişken değerleri).

## Sık tuzaklar
- `=` ile `==`; tamsayı bölmesi; dizi sınırı aşımı; ilk değer verilmemiş değişken.
- Kopya yapıcı, kopya atama ve yıkıcı birlikte düşünülür: işaretçi üye varsa derin kopya gerekir (sığ kopya çift silmeye yol açar).
- Çok biçimlilik için taban sınıf işaretçisi/referansı ve `virtual` gerekir; taban sınıfın yıkıcısı `virtual` olmalı; nesneyi değerle atamak dilimlemeye (object slicing) yol açar.
- `operator<<` üye fonksiyon olamaz (sol operand `cout`); `friend` ya da üye olmayan fonksiyon olarak yazılır.
- `new[]` ile `delete[]`, `new` ile `delete`; bellek sızıntısı ve sarkan işaretçi.
- Üye başlatma listesinde sıra bildirim sırasıdır; `const` ve referans üyeler yalnız başlatma listesiyle ilk değer alır.
- `static` üye sınıf dışında tanımlanır; `const` üye fonksiyon nesneyi değiştirmez.
- Kalıtımda erişim: `public` kalıtımda taban sınıfın `private` üyelerine türemiş sınıf erişemez; `protected` erişir.
- `catch` blokları sırayla denenir: türemiş istisna sınıfı tabandan önce yazılır, referansla yakalanır.
- Başlık dosyası koruması (`#ifndef`) ve ayrı derleme.

## Uygulama örnek havuzu
Devre elemanı sınıf hiyerarşisi (`Component` → `Resistor`, `Capacitor`; çok biçimlilikle empedans/güç hesabı), karmaşık sayı sınıfı (operatör aşırı yükleme, fazör hesabına hazırlık), sensör sınıfı ve ölçüm kaydı, matris/vektör sınıfı, sinyal örnek tamponu, dosyadan ölçüm okuma ve istisna, ATM.
