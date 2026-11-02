# Görev: çoktan seçmeli soru seti hazırlamak (şablon W24)

Konu anlatımı DIŞINDA soru hazırlarken (kullanıcı soru dosyası yükledi, deneme sınavı, "bana N soru hazırla") testin biçimi hep **W24**'tür: elle HTML yazma, şablonu `araclar/soru_testi.py` ile veriden üret. Anlatım içindeki mini test ve konu sonu testi W10'da kalır (gorevler/ozet-ve-test.md).

## Akış
1. **Kaynağı oku.** Soru dosyası metinse (docx, txt, metin PDF) doğrudan oku; taranmış ya da fotoğraf PDF ise önce gorevler/pdf-cevir.md. İngilizce soru ve şık metnini kaynaktan aynen al, kısaltma ve değiştirme (kaynağa bağlılık).
2. **Cevap anahtarını doğrula.** Dosyada anahtar varsa kullan ama her soruyu kendin de çöz; ayrılan soru olursa kullanıcıya tek satırla göster. Anahtar yoksa kendin hesapla, hesabı açıklamaya yaz. Yeni soru yazıyorsan: zor, çok adımlı, tuzak şıklı (çekirdek §5); doğru cevap harflerini dengeli dağıt.
3. **Veri JSON'unu yaz.** Şema ve varsayılanlar `python3 araclar/soru_testi.py --ornek` çıktısındadır (tek kaynak; burada kopyalanmaz). Kurallar:
   - Soru ve şıklar İngilizce, Türkçesi ayrı alanda (`soru_tr`, `tr`); araç parantezi kendisi koyar. Sayı ve sembol şıklarında `tr` boş kalabilir. Terim dili ayar C'ye göre; kullanıcının yerel ayarı geçer.
   - Her yanlış şıkta `neden_yanlis`: tuzağın adı (ters oran, birim, işaret, kavram karışıklığı) ve doğrusu, 1–2 cümle. Doğru şıkta yok.
   - `aciklama` 2–5 kısa satır; hesap varsa adım adım ayrı satırlar. Gerçek kesir `{pay|payda}`, üs `^{2}`, alt indis `_{0}`; `a/b` gibi düz kesir yazma. Şık harfine gönderme yapma ("B'de..." yok).
   - `kaynak` her soruda slayt/sayfa numarası. Gösterimi (açıklama altı, sonda Ekstra tablosu ya da ikisi) ayar D'ye ve kullanıcının tercihine göre `kaynak` alanıyla seçilir.
   - `bolum` (ünite ya da slayt bölümü): sonuç ekranında bölüm çubukları çıkar, zayıf konu görünür.
   - Şıklar her başlangıçta karışır (`karistir`): açıklama ve notlarda şık harfine gönderme yapma ("B'de..." yok, araç yakalar); "hepsi/hiçbiri/ikisi de" şıkkına `"sabit": true` yaz (olduğu yerde kalır).
   - `mod`, `yanlis_notu`, `kaynak`, `karistir`, `dil` üst alanları kullanıcı tercihidir; yerel ayarlarda yazan varsa onu yaz. Verilen kararlar: gorsel/soru-testi/kararlar.md.
4. **Üret.** Önce `python3 araclar/anlatim_testi.py veri.json` (dil, konu ipucu, cevap dağılımı; gorevler/anlatim-kontrol.md), sonra `python3 araclar/soru_testi.py veri.json cikti.html`. Hata varsa düzelt (araç eksik not, yanlış harf, tekrar eden numara, kayıp Türkçe karakter yakalar); uyarılara bak. 20 sorudan uzun set otomatik eşit parçalara bölünür (`-1`, `-2`). Veri ve çıktıyı kullanıcının proje klasörüne koy (ör. `dersler/<ders>/test/`) ki yeniden üretilebilsin; depoya soru yazma.
5. **Yayınla.** `post_widget` · `show_widget`, `widget_code` = çıktı dosyasının içeriği AYNEN. Elle yeniden yazma, `\u` kaçışıyla yazma (ü, ı düşüyor); yayınlanmış widget değiştirilemez. Başlık kısa kebab-case (ör. `ders-5-test`). Yayından sonra mesajı geri oku ve Türkçe karakterleri kontrol et.
6. **Paylaşım.** Başkalarına yollanacaksa `python3 araclar/soru_testi.py veri.json cikti.html --tek-sayfa`: tek dosya, internet gerekmez, açık/koyu tema cihazı izler. Dosyayı mesaja ekle; kullanıcı isterse aynı sayfayı Artifact olarak da yayınla (bağlantıyı kullanıcı paylaşır). Kullanıcıya ait soru dosyasından üretilen test depoya girmez.
7. **Mesaj.** En çok 2 satır: kaç soru, kaç parça, hangi mod. Parçalar sırayla gönderilir.

## Ekran testi (ayar G)
Yalnız soru verisi değişiyorsa test yok (G2). Şablonun kendisini değiştirdiysen yapı değişti sayılır: `python3 araclar/soru_testi.py gorsel/soru-testi/ornek.json x.html --tek-sayfa` ile üret, `gorsel/test/ekran-testi.js` ile 390 ve 844 genişlikte, açık ve koyu temada bak; tıklama akışını (cevap, sınav modu, tekrar, sonuç) elle dene.

## Şablonu değiştirmek
Görünüm ya da davranış isteği gelirse (kararlar gorsel/soru-testi/kararlar.md, değişince oraya satır ekle) tek yer `gorsel/sablonlar/W24-coktan-secmeli-test.html`. Değişince `python3 araclar/soru_testi.py --sablonu-yenile` ve `python3 araclar/uret.py` çalıştır (gorevler/kural-guncelle.md). iPad için emoji, `color-mix` ve geçiş animasyonu yok; renk tonu için `.tn` katmanı kullanılır.
