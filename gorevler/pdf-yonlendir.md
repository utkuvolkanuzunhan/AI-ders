# Görev: PDF'i çeviri sohbetine yönlendirmek

**Sert kural:** PDF → metin çevirisi ile anlatım AYNI sohbette yapılmaz. Çeviriyi yalnız koordinatörün `Rol: pdf-cevirici` ile açtığı sohbet yapar. Anlatım sohbeti PDF açmaz, okumaz, çevirmez; kaynağı yalnız `araclar/kaynak.py` ile `pdf-metin/` dosyasından okur. Bu kural kodla zorlanır: `paket.py --ek <dosya>` ve `kaynak.py` çevrilmemiş dosyada durur (çıkış kodu 3).

PDF/slayt bu sohbete yüklendiyse ya da brief'te verildiyse (rol pdf-cevirici değilse):
1. Dosyayı açma, okuma, çevirme, anlatma. Kullanıcı "anlat" dese de.
2. Koordinatöre (message_coordinator) tek mesaj: "PDF çeviri sohbeti aç. Brief: AI-ders oku. Rol: pdf-cevirici. Ders: <ders>. Dosya: <yüklenen dosyanın yolu>. Konu: <kullanıcının istediği konu ya da 'indeksteki ilk konu'>. Kod: <geçerli kod>."
3. Kullanıcıya tek satır: "PDF'i çeviri sohbetine gönderdim; metin hazır olunca anlatım yeni sohbette başlayacak, bağlantısını buraya vereceğim."
4. Bu sohbette yarım kalan anlatım varsa önce kısa devir notu (gorevler/devir.md).
5. Çeviri sohbeti metni yazıp anlatım sohbetini isteyince koordinatör bağlantıyı verir; bu sohbet o bağlantıyı kullanıcıya tek satırla iletir ve kapanır.

Akış özeti: yükleme sohbeti (yönlendirir) → çeviri sohbeti (yalnız metin yazar) → anlatım sohbeti (yalnız pdf-metin okur).
