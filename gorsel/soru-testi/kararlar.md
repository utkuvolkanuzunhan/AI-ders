# W24 çoktan seçmeli test: karar kaydı

2 Kasım 2026, kullanıcı kararları (görsel seçenekler önizlemeli sorulup seçildi). Şablon: `gorsel/sablonlar/W24-coktan-secmeli-test.html`, araç: `araclar/soru_testi.py`, kural: `gorevler/soru-seti.md`. Bir karar değişirse şablon ya da araç güncellenir, bu dosyaya yeni satır eklenir (eskisi silinmez).

## Görünüm
| # | Konu | Seçilen | Not |
|---|---|---|---|
| 1 | Şık stili | **Şeritli kart** | Solda büyük harf şeridi; doğru yeşil, yanlış turuncu şerit |
| 2 | Geri bildirim | **Düğmeyle aç, açılan şerit biçiminde** | Cevap verince şıklar boyanır; "Açıklamayı göster" düğmesi renkli Doğru/Yanlış · Doğru cevap şeridini, açıklamayı ve şık notlarını açar |
| 3 | İlerleme | **Segmentli şerit** | Her soru bir parça; dokununca o soruya gider |
| 4 | Sonuç ekranı | **Halka + bölüm çubukları ve büyük skor + yanlış listesi, ikisi birlikte** | Halkanın içinde büyük "12 / 15"; altında bölüm çubukları, numaralı kutular, "Tekrar bak" listesi |
| 5 | Yazı boyutu | **Büyük** | Soru 20, şık 18, Türkçe 16 px (dosyadaki gibi büyük) |

## İşlev
| # | Konu | Seçilen | Not |
|---|---|---|---|
| 1 | Mod | **Öğren ve Sınav, iki mod** | Öğren: her cevaptan sonra geri bildirim. Sınav: cevaplar sonda açılır, cevap değiştirilebilir |
| 2 | Yanlış şık notu | **Her yanlış şıkta** | `neden_yanlis` her yanlış şıkta zorunlu |
| 3 | Sıra | **Soru ve şıklar karışır** | Her başlangıçta ve tekrar turunda yeni sıra. Açıklama şık harfine gönderme yapamaz; "hepsi/hiçbiri" şıkkı `sabit: true` |
| 4 | Uzunluk | **Sohbet uzunluğa göre seçer** | 20 soruya kadar tek test; üstü en çok 15'erli eşit parçalara bölünür (iPad'de widget hafif kalsın) |
| 5 | Kaynak | **İkisi birden** | Açıklamanın altında soluk "Kaynak" satırı ve sonuçta Ekstra tablosu |
| 6 | Paylaşım | **Başkalarına yollanabilir** | `--tek-sayfa` çıktısı tek dosyadır: internet gerekmez, açık/koyu temayı cihazdan alır; dosya ya da bağlantı olarak paylaşılır |

## Tasarım ilkeleri (değişmeden kalan)
- iPad: emoji, `color-mix`, geçiş animasyonu yok; renk tonu `.tn` katmanıyla.
- Doğru = `--c2`, yanlış = `--c3`; renk tek başına anlam taşımaz (ikon + yazı).
- Dokunma hedefi ≥ 44 px, yazı ≥ 13 px, `<button>` yok (`role="button"`).
