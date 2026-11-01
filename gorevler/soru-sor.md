# Görev: soru sormak

## Anlatım içindeki sorular (varsayılan)
- Widget içinde sor: W10 (tek ya da çok soru, tıklanabilir şıklar, anında doğru/yanlış + açıklama, İpucu düğmesi) ya da W09 doğru/yanlış kartları. Akış durmaz, cevap beklenmez; bir sonraki adımı hemen gönder.

## Cevabı sana dönmesi gereken soru (yalnız konu sonu)
- Yalnız konunun en son mesajı olarak, arkasında gönderilecek adım kalmadığında. Anlatım ortasında kart yok.
- `request_decision` kartı: soru en çok ~12 kelime, 2–4 şık, son şık "İpucu ver" ve önerilen o.
- Şıklar tuzaklı: birim hatası, Kelvin/°C, işaret, ters oran, sık yapılan kavram karışıklığı.
- Hesap sorusunda sayıları soru metninde ver, şıklar sonuç olsun.
- Cevap gelince: doğruysa kısa onay + neden doğru (1 cümle). Yanlışsa önce doğru yaptığı kısmı söyle, sonra hatayı düzelt, gerekirse benzer ikinci soru.
- "İpucu ver" seçilirse tek ipucu ver ve aynı soruyu yeniden kartla sor.
- Kullanıcının hatalarını ünite raporuna "zayıf nokta" olarak not et (somut örnekle).

## Kendi kendine kontrol
- Widget içinde: W10 mini test (çok adımlı, anında geri bildirim, sonda "Sonuç: x / n") ya da W09 doğru/yanlış kartları.

## Zorluk
- Tek adımlı ezber sorusu yok. En az iki adım ya da bir tuzak.
- Ezber konularında aralıklı tekrar: önceki konudan bir soru blok sonuna eklenir.
