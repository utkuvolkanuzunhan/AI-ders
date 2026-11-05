# Görev: PDF'i çeviri sohbetine yönlendirmek

**Sert kural:** PDF → metin çevirisi ile anlatım AYNI sohbette yapılmaz; çeviriyi yalnız `Rol: pdf-cevirici` sohbeti yapar. Anlatım sohbeti PDF'i açmaz, okumaz, çevirmez; kaynağı yalnız `araclar/kaynak.py` ile `pdf-metin/` dosyasından okur (kodla zorlanır: `paket.py --ek` ve `kaynak.py` çevrilmemiş dosyada çıkış kodu 3 verir).

PDF/slayt bu sohbete yüklendiyse ya da brief'te verildiyse (rol pdf-cevirici değilse):
1. Dosyayı açma, okuma, çevirme, anlatma; kullanıcı "anlat" dese de.
2. Koordinatöre (`message_coordinator`) tek mesaj: "PDF çeviri sohbeti aç. Brief: AI-ders oku. Rol: pdf-cevirici. Ders: <ders>. Dosya: <yol>. Konu: <istenen konu ya da 'indeksteki ilk konu'>. Kod: <geçerli kod>."
3. Kullanıcıya tek satır: "PDF'i çeviri sohbetine gönderdim; metin hazır olunca anlatım yeni sohbette başlayacak."
4. Yarım kalan anlatım varsa önce kısa devir notu (`ders.py devir`). Koordinatör anlatım sohbetinin bağlantısını verince tek satırla ilet ve kapan.
