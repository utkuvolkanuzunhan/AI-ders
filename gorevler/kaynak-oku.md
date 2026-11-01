# Görev: kaynağı az token ile, sadık okumak

Amaç: kaynağa bağlı kalmak VE az okumak. İkisi aynı yolla sağlanır: her PDF bir kez metne çevrilir, sohbetler yalnız gereken sayfa aralığını okur.

## Kaynak nerede (kullanıcının proje klasöründe)
- `dersler/<ders>/pdf-metin/<ad>.md` : PDF'in sayfa sayfa metni; her sayfa `[[SAYFA <basılı> | pdf <sıra>]]` satırıyla başlar, çizimler mantık diliyle yazılmış.
- `dersler/<ders>/pdf-metin/indeks.md` : her PDF için konu → sayfa aralığı.
- Drive yalnız ham arşivdir (kurulum: kurulum/drive.md). Anlatım sohbeti Drive'daki PDF'i doğrudan okumaz.

## Okuma sırası
1. `indeks.md`'den konunun PDF'ini ve sayfa aralığını bul.
2. Yalnız o aralığı oku: `awk '/^\[\[SAYFA 9 \|/,/^\[\[SAYFA 16 \|/' dosya.md` (bir sonraki sayfanın işaretine kadar). Tüm dosyayı okuma.
3. Aralık yetmezse bir sayfa önce/sonra ekle; yine tüm dosyayı okuma.
4. Konunun metni yoksa: kullanıcıya PDF'i yüklemesini bir kez hatırlat ve PDF çevirisini işçiye ver (gorevler/pdf-cevir.md). Çeviri gelene kadar müfredata göre anlattığını söyle (ayar A1) ya da bekle (ayar A2).
5. Kullanıcı sohbete PDF yüklerse onu anlatım sohbetinde okuma; işçiye çevirt, sonra yalnız aralığı oku.

## Sadakat
- Anlatılan her tanım, sıra, notasyon ve örnek okunan sayfalardan gelir. Sayfa numarasını hemen not al: kaynak gösterirken HER ZAMAN basılı numara (kitabın üzerinde yazan) kullanılır, pdf sıra numarası değil. `~` ya da `?` işaretli sayfayı kesin numara gibi yazma ("s.~23" yaz); Ekstra'daki kaynak tablosu (ayar D) bu notlardan yazılır.
- Şekil/tablo numaralarını kaynaktaki gibi kullan; widget'ta yeniden çizerken numarasını koru.
- Kaynakta olmayan bilgi ayar A'ya göre işlenir (A1: Ekstra'da "slayt dışı", A2: hiç).

## Bütçe
- Bir konu için hedef: kural paketi ~15 KB + 5–8 sayfa kaynak metni.
- Aynı aralığı sohbet içinde ikinci kez okuma; notların yeter.
