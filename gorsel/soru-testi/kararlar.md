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

## Sonradan eklenenler
| # | Konu | Seçilen | Not |
|---|---|---|---|
| 7 | Şık renkleri | **Her şık ayrı renk** | A mavi, B pembe, C turkuaz, D limon sarısı, E mor (öneri: kullanıcı, 2 Kasım). Sıra, komşu şıkların normal ve renk körü görüşte ayırt edilmesi için doğrulandı. Cevaptan sonra yalnız doğru (yeşil) ve seçilen yanlış (turuncu) renkli kalır, öteki şıklar nötr; renkler yeşil/turuncu anlam renkleriyle karışmasın diye ikisine yakın ton kullanılmaz. Harf şeridi renk dışında harfle de ayırt edilir. |

## Tasarım değişikliği (2 Kasım 2026, kullanıcı: tüm widget'lar karmaşık bulundu)
Şablon, araç ve gorsel/stil.md birlikte güncellendi; yukarıdaki eski satırlar (Görünüm 1, Görünüm 2'nin boyama biçimi, Sonradan eklenenler 7) bu satırlarla **geçersiz** oldu, kayıt için silinmedi.

| # | Konu | Seçilen | Not |
|---|---|---|---|
| 8 | Test görünümü | **Çizgili** | Kutu yok: şıklar 1 px çizgiyle ayrılır; harf soluk. Cevaptan sonra yalnız doğru (yeşil sol çizgi 5 px + açık yeşil zemin) ve seçilen yanlış (turuncu) boyanır, ötekiler %50 soluk. Mini test, tam test ve soru seti aynı |
| 9 | Şık renkleri | **Şık başına renk yok** | #7 iptal: gri harf, renk yalnız doğru/yanlış anlamı taşır |
| 10 | Geniş ekran | **Şıklar 2×2** | Tablet/telefon yatay (≥600 px): iki sütun, şık satırı 92 px, düğmeler sınırlı genişlik; dar ekranda 1×4 |
| 11 | Anlatım widget'ı | **Karma (W25)** | Çizgi + gri + derin renkli (+ seyrek pastel) yüzeyler; "işaret ve hesap" gri, büyük yazı. Kural: gorsel/stil.md §2 |
| 12 | Türkçe satırı | **Ayrı satır, soluk, parantezli** | Motor sondaki dengeli parantezi ayırır; veri `"English (Türkçe)"` kalır |

## Tasarım ilkeleri (değişmeden kalan)
- iPad: emoji, `color-mix`, geçiş animasyonu yok; renk tonu `.tn` katmanıyla.
- Doğru = `--c2`, yanlış = `--c3`; renk tek başına anlam taşımaz (ikon + yazı).
- Dokunma hedefi ≥ 44 px, yazı ≥ 13 px, `<button>` yok (`role="button"`).
