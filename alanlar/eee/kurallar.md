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
- Formül yazımı (sohbet arayüzünde bozulmaması için; Lineer Cebir Ü2'de bozuk göründü, kesin neden belirlenemedi, bu yüzden hepsi aynı güvenli kalıba çekildi):
  - Blok formül yalnız `$$\Large \boldsymbol{...}$$` kalıbıyla; küçük harf `\large` ve `\boldsymbol`suz çıplak `$$...$$` yazma. Taşarsa `\Large` düşer (`$$\boldsymbol{...}$$`); yine taşarsa böl.
  - Telefonda taşmaz (içerik genişliği ≈ 340 px, `\Large` ile ≈ 300 px sığar): her `$$` bloğunda tek matris, uzun denklem satırlara bölünür ya da toplam sembolüyle yazılır. Kalın metnin içine formül konmaz.
  - Boşluk komutu yazma: `\,`, `\;`, `\!` yerine bitişik yaz (`a_{ik}b_{kj}`) ya da `\cdot` kullan (`k\cdot\mathrm{tr}(A)`). İz için `\mathrm{tr}`.
  - Satır içi formül rakamla başlamaz: `${2}\times 3$`, `${3}A-2B$`, `${0}A$` (aksi halde `$` para işareti sanılabilir). Tek başına `$0$`/`$1$` yazma: sıfır matrisi `$\mathbf{0}$`, "1 ile n arasında" gibi sayıyı düz metin yaz.
  - Formülden hemen sonra kesme işareti ya da ek getirme (`$X$'nın` yerine `$X$ matrisinin`).

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
