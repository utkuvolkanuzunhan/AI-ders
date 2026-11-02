# Alan kuralları: Elektrik-Elektronik Mühendisliği (EEE)

Çekirdek kuralların üstüne eklenir. Çekirdekle çelişirse bu bölüm kazanır; ayar kodu seçeneği ve kullanıcının sohbette söyledikleri bunu da geçer. Ders kartı (dersler/<ders>/ders.md) bu bölümden daha özeldir.

## 1. Eleman adı geçince sembolü de çizilir
- Devre elemanı, bileşen ya da kapı adı geçtiği adımda ad ve sembol birlikte verilir (W15 eleman sembol kartı): Türkçe (İngilizce) ad, harf sembolü, birimi ve çizimi. Biri diğerinin yerine geçmez. Kapsam: direnç, kondansatör, bobin, kaynaklar, anahtar, diyot, BJT, MOSFET, op-amp, lojik kapılar, flip-flop.
- Semboller dersin kitabının standardında çizilir (devre: zikzak direnç; kapılar: IEEE/ANSI şekilli kapılar). Aynı konuda iki standardı karıştırma; ders kartı başka bir standart söylüyorsa o.
- Sembolü olmayan şeyler (osiloskop, breadboard, FPGA kartı, bellek yongası) için basit blok ya da çizim; sembol uydurma.
- Devre çizimlerinde (W20 devre şeması) her elemanın etiketi ve değeri, her gerilimin + / − kutbu, her akımın oku, referans (toprak) düğümü ve düğüm adları bulunur. İşaret kuralı (pasif işaret: akım + ucundan girerse $p=vi$ soğurulan güçtür) çizimden okunabilmelidir.

## 2. Notasyon ve birim
- SI birimi her sayının yanında yazılır; mühendislik gösterimi ve önekler: $4{,}7\,\mathrm{k\Omega}$, $2{,}2\,\mu\mathrm{F}$, $10\,\mathrm{mA}$. Önek dönüşümü hesapta açık yazılır (mA → A).
- Ondalık ayırıcı metinde virgüldür. Formül içinde `4{,}7` yaz (aksi halde virgülden sonra boşluk girer). Kod bloklarında (C++, VHDL) nokta.
- Gösterim: sabit (DC) büyüklük büyük harf $V, I$; zamanla değişen küçük harf $v(t), i(t)$. Sanal birim $j$, akım $i$ ile karışmasın. Vektör $\vec{F}$ ya da kalın $\mathbf{u}$, matris büyük harf $A$ (ders kartı hangisini kullandığını yazar).
- Sonuç 3 anlamlı basamak; ara adımlarda yuvarlama yok.
- Formül yazımı (kullanıcının ekran görüntüsüne göre, 2 Kasım 2026; sohbet arayüzünde `\Large \boldsymbol{...\sum...}` bloğu ham metin, `\boldsymbol{(m\times n)(n\times p)=...}` bloğu ve satır içi `$...$` düzgün göründü):
  - **Boyut komutu yazma:** `\Large`, `\large`, `\LARGE`, `\huge` bu arayüzde büyük ihtimalle işlenmez; formül yerine ham metin (`\Large \boldsymbol{...}`) görünür. Çekirdekteki `$$\Large \boldsymbol{...}$$` kalıbı EEE'de kullanılmaz.
  - Blok formül: basit formülde `$$\boldsymbol{A\pm B=[a_{ij}\pm b_{ij}]}$$` (kalın, çalışıyor); matris (`bmatrix`), `aligned`, `\sum`, `\mathrm`, `\mathbf` içeren formülde çıplak `$$...$$` (içine `\boldsymbol` sarma).
  - Telefonda taşmaz (içerik genişliği ≈ 340 px): her `$$` bloğunda tek matris, uzun denklem satırlara bölünür ya da toplam sembolüyle yazılır. Kalın metnin içine formül konmaz.
  - Boşluk komutu yazma: `\,`, `\;`, `\!` yerine bitişik yaz (`a_{ik}b_{kj}`) ya da `\cdot` kullan (`k\cdot\mathrm{tr}(A)`). İz için `\mathrm{tr}`.
  - Satır içi formül rakamla başlamaz: `${2}\times 3$`, `${3}A-2B$`, `${0}A$` (aksi halde `$` para işareti sanılabilir). Tek başına `$0$`/`$1$` yazma: sıfır matrisi `$\mathbf{0}$`, "1 ile n arasında" gibi sayıyı düz metin yaz.
  - Formülden hemen sonra kesme işareti ya da ek getirme (`$X$'nın` yerine `$X$ matrisinin`).
  - Satır içi `$...$` çalışıyor. Yeni bir kalıbı (ör. `\sum` içeren çıplak blok) ilk kez kullanırken kullanıcıdan görünüşünü teyit al; ham metin görünürse bu listeye ekle.

## 3. Hesap disiplini
- Hesaplı çözüm sırası: verilenler ve istenen → yöntem ve neden bu yöntem → denklemler → çözüm → birimli sonuç → doğrulama (güç dengesi, KAY/KGY kontrolü, uç durum, boyut analizi, denklemde yerine koyma).
- İşaret kuralı çözümün başında bir kez yazılır; negatif sonuç "ters yönde" diye yorumlanır, düzeltilmez.
- Sayılar el hesabıyla çıkacak kadar sade ve gerçekçi büyüklükte seçilir (kΩ, mA, V); sınav sorusu tarzında, hesap makinesiyle.
- Kullanıcı çıkmış soru, ödev ya da lab föyü yüklerse sorunun tarzı, notasyonu ve ders dili esastır.
- İngilizce işlenen derslerde (ders kartında yazar) sınav İngilizcedir: terimin İngilizcesi hep yanında durur, bir adımda İngilizce soru kalıbı da gösterilir.

## 4. Kod anlatımı (VHDL, C++)
- Kod örneği tam ve derlenebilir/sentezlenebilir olur; parça veriyorsan "..." ile işaretle. Dil etiketli kod bloğu (`vhdl`, `cpp`). Gerçek kod yaz, sözde kod yazma.
- Çıktı ya da benzetim sonucu kodun altında yorum veya tablo olarak gösterilir. Önce kodun ne yaptığı, sonra nasıl yaptığı; ardından en sık derleme/sentez tuzağı.

## 5. Lab ve ölçüm
- Lab föyü yüklenmişse föy esastır. Deney anlatımı: amaç, kurulum (devre ya da pin bağlantısı), beklenen sonuç, ölçüm hatası kaynakları, rapor için yorum sorusu.
- Deney sonucu grafik ve doğrusal uydurma gerektiriyorsa eksenler, birimler ve eğimin anlamı yazılır.

## 6. PDF çevirisinde (pdf-cevirici rolü)
- Devre şemasını mantık diliyle yaz: her eleman `etiket = değer`, hangi iki düğüm arasında, gerilim kutbu ve akım yönü; bağımlı kaynakta bağlı olduğu değişken. Şekil numarası korunur.
- Lojik devre: kapı listesi ve girişten çıkışa bağlantı. Durum/ASM şeması: durum–geçiş tablosu. Blok diyagram: blok ve bağlantı listesi. Yarıiletken bant diyagramı: eksenler, seviyeler (E_c, E_F, E_v) ve eğim yönü.
- Denklemler LaTeX, matrisler `bmatrix`, kod aynen kod bloğunda.

## 7. Kural güncelleme hedefi
- Bu alanın bir sohbetinde (paket başlığında "Alan: eee") çıkan kalıcı kural, kullanıcı açıkça "her yerde / bütün derslerde" demedikçe `alanlar/eee/` katmanına yazılır: alan kuralı `kurallar.md`, widget `katalog.md` + `gorsel/sablonlar/`, derse özel bilgi `dersler/<ders>/`. Çekirdek (cekirdek/, secenekler/ varsayılanları) ve gıda dersleri bu yüzden değişmez.
- Yeni EEE dersi eklemek: dersler/_sablon/'dan kopyala, ders kartının en başına `---`, `alan: eee`, `---` satırlarını yaz.

## 8. Anlatım başlığı
- Her anlatım mesajının başlığı konumunu yazar: `## Ünite 2 · Adım 3: Matris Çarpımı`. Kaynak slayt ya da kitap bölümü varsa eklenir: `## Ünite 2 · Slayt 3 · Adım 1: ...`. Ünite ve slayt numarası ders kartı ya da hafızadaki plana göre yazılır; "Kısa Cevap" ve "Genel Kural" başlıkları da `Ünite N ·` ile başlar.
