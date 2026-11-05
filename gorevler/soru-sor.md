# Görev: soru sormak

## Anlatım içindeki sorular (varsayılan)
Widget içinde sorulur (`test` bileşeni / W10, ya da doğru-yanlış kartları W09): tıklanır, anında doğru/yanlış + açıklama, gerekirse İpucu. Akış durmaz, cevap beklenmez; sonraki adımı hemen gönder. Tek adımlı ezber sorusu yok: en az iki adım ya da bir tuzak. Ezber konularında önceki konudan bir soru blok sonuna eklenir.

## Cevabı sana dönmesi gereken soru (yalnız konunun son mesajı)
- `request_decision` kartı: soru ~12 kelimeyi aşmaz, 2–4 şık, son şık "İpucu ver", önerilen o. Şıklar tuzaklı (birim hatası, Kelvin/°C, işaret, ters oran, sık kavram karışıklığı); hesap sorusunda sayılar soruda, şıklar sonuç.
- Cevap gelince: doğruysa kısa onay + neden (1 cümle); yanlışsa önce doğru yaptığı kısmı söyle, sonra hatayı düzelt, gerekirse benzer ikinci soru. "İpucu ver" seçilirse tek ipucu verip aynı soruyu yeniden sor.
- Hataları ünite raporuna "zayıf nokta" olarak somut örnekle not et (`ders.py not zayif "…"`).
