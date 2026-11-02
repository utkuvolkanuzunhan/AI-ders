# Görev: bir konuyu anlatmak

## Konu açılışı (ilk mesaj)
1. `## Kısa Cevap`: konunun 1–2 cümlelik özü + hedef cümlesi ("Bu blok sonunda ... hesaplayabileceksin").
2. Yol haritası: yerleşik adım kartı (`post_widget`, `step_card_display_v0`), metne yazılmaz.
3. Tanım ve teoriyle başla.

## Her adım
- Tek mesaj = tek adım: `## Adım n: Başlık` + kısa metin (ayar E'deki kalıp) + hemen altında o adımın widget'ı.
- Widget, metindeki sayıların aynısını kullanır; altında "Ne yapacaksın, ne göreceksin" tek cümle.
- Formülleri türet (nereden geldiği), kavramı somut sayıyla göster, sınav tipi çözümlü örnek ver, fabrika/endüstri karşılığını yaz.
- Kaynaktaki liste, sınıflama ve madde sayısını koru: kaynakta kaç madde varsa o kadar (ayar A). Uzun listeyi gruplara böl ve numarala, madde atlama.
- Kimyasal grup/molekül adı geçen adımda W13, etkenler sayılan adımda W14 kullan (cekirdek §6).
- Metin biçimini de çeşitlendir: bir adımda bullet, birinde numaralı adım, birinde tablo, birinde kısa tanım kutusu.
- Grafik varsa eksenleri ve okuma sırasını yaz: başlık → yatay eksen → dikey eksen → tek bir noktayı oku → genel şekil.
- Adım sonunda gerekiyorsa tek soru, widget içinde (gorevler/soru-sor.md); her adımda soru zorunlu değil, blok sonunda 2–3 soru zorunlu.
- Adımları art arda gönder; arada cevap bekleme, "devam edelim mi" sorma (cekirdek §2).

## Konu sonu
gorevler/ozet-ve-test.md.

## Kalite kontrolü (göndermeden önce, her mesaj)
- Mesajı `araclar/anlatim_testi.py` ile dene (düz kesir, HTML etiketi, formül biçimi, boşluk düzeni, başlık, paragraf uzunluğu): gorevler/anlatim-kontrol.md. HATA varsa gönderme, düzelt.
- Kaynak/sayfa metne karışmış mı (ayar D)?
- Widget'ı gorsel/stil.md'deki kontrol listesiyle geçtin mi?
