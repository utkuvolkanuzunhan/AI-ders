# Kurulum (yeni bir kullanıcı için)

1. **Proje talimatı:** Claude projesinin talimatına `proje-talimati.md`'deki 4 satırı yapıştır.
2. **Depoyu projeye ekle:** proje ayarlarında bu depoyu (utkuvolkanuzunhan/AI-ders) kaynak olarak ekle. Eklenmezse sohbet herkese açık adresten klonlar.
3. **Yerel ayarlar:** proje dosyalarına `yerel/ayarlar.md` oluştur (şablon: `yerel-ayarlar-sablonu.md`; EEE için hazır örnek: `yerel-ayarlar-eee.md`). Ayar kodunu galeri sayfasından seçip buraya yaz; alanın varsa `Alan:` satırını da ekle. Bu dosya projende kalır, istediğin zaman değiştirirsin, depo varsayılanı hiç değişmez. Depoya yazma: depo herkese açıktır. Bu adımı atlarsan ilk koordinatör ya da ders yöneticisi sohbeti dosyayı şablondan kendisi oluşturur; kişisel tercihlerin hep buraya yazılır.
3b. **Denetim profili (isteğe bağlı):** ölçülebilir tercihlerin (terim dili, emoji serisi, mini test sayısı, karışık sorular) proje dosyalarında `yerel/profil.json` olarak durur (şablon: `yerel-profil-sablonu.json`; eski ad `denetim.json` de okunur, anahtarları `araclar/profil.py` denetler); anlatım denetimi (`araclar/anlatim_testi.py`) onu kendisi bulur. Depoya yazma.
4. **Drive (isteğe bağlı):** `drive.md`'deki klasör yapısını kur; PDF'leri otomatik metne çevirmek için `pdf-bolme/` betiğini ekle.
5. **İlk sohbet:** "AI-ders oku. Rol: ders-yoneticisi. Ders: <ders>." diye bir ders sohbeti başlat; ünite listesini o çıkarır.

Model önerisi (ölçülmedi, deneme sürüyor): konu anlatan ünite sohbeti için daha yüksek düşünme ayarı; ders yöneticisi, PDF çevirisi ve idari işler için orta ayar yeter.
