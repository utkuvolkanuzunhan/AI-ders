# Görev: kaynağı az token ile, sadık okumak

Her PDF bir kez metne çevrilir; sohbetler yalnız gereken sayfa aralığını okur.

## Kaynak nerede (kullanıcının proje klasöründe)
- `dersler/<ders>/pdf-metin/<ad>.md`: sayfa sayfa metin, her sayfa `[[SAYFA <basılı> | pdf <sıra>]]` ile başlar, çizimler mantık diliyle yazılmış. `pdf-metin/indeks.md`: konu → sayfa aralığı. Drive yalnız ham arşivdir.

## Okuma sırası
1. `indeks.md`'den konunun dosyasını ve aralığını bul.
2. Yalnız o aralığı oku: `python3 araclar/kaynak.py dersler/<ders>/pdf-metin/<ad>.md 9 16` (basılı numarayla; pdf sırasıyla `--pdf 11 18`; `--liste` işaretleri gösterir). Başka yolla (Read, cat, PDF) okuma; tüm dosyayı okuma; aynı aralığı ikinci kez okuma. Yetmezse bir sayfa önce/sonra ekle.
3. Konunun metni yoksa: PDF'i yüklemesini bir kez hatırlat; yüklenince bu sohbet çevirmez, `gorevler/pdf-yonlendir.md`. Çeviri gelene kadar müfredata göre anlat (A1) ya da bekle (A2).

## Sadakat
- Her tanım, sıra, notasyon ve örnek okunan sayfalardan gelir. Sayfa numarasını hemen not al; kaynak gösterirken HER ZAMAN basılı numara kullanılır. `~`/`?` işaretli sayfayı kesin yazma ("s.~23"). Şekil/tablo numaralarını koru.
- Kaynakta olmayan bilgi ayar A'ya göre işlenir. `ders.py adim --sayfa` düşen sözcük, kaynakta olmayan terim/sayı ve liste sayısı farkını UYARI olarak gösterir; yargı sende.
