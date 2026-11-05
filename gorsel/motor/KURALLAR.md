# Widget kuralları (Neobrutalism motoru)

HTML ve CSS yazma: kısa JSON spec yaz, `python3 araclar/widget.py spec.json cikti.html --yuk cikti.yuk.json --test` üretir ve ekranda dener (390/900 px, açık/koyu, her sekme; yazı ≥13 px, hedef ≥44 px, taşma, JS hatası). Bileşen alanları: `gorsel/motor/README.md`. Renkler temadan gelir, sabit renk yazma. Gönderimde `widget_code` yük dosyasından birebir yapıştırılır, elle yeniden yazılmaz (harf bozulur); sonra `ders.py dogrula`.

## Bileşenler (spec `tur`)
`etiket`, `not` (yap/gör), `formul` (dokunulabilir terim), `kartlar` (çipe basınca açıklama), `secici` (çip → çubuk + sonuç), `cubuklar`, `siniflama` (kartı seçeneğe ata), `tablo`, `zincir`, `kaydirici` (+ sabit eksenli `grafik`), `svg`, `ham` (başka bileşen yetmezse), `test` (panelin son bileşeni).

## Hangi iş için
| İş | Bileşen |
|---|---|
| Formülün terimleri, kesir, üs | `formul` (kesir gerçek pay/payda; "a/b" yok) |
| Türetme, adım adım hesap | `zincir` ya da `kartlar` sırayla |
| Doğrusal ya da eğri ilişki, etki | `kaydirici` + `grafik` (eksenler sabit, başlık ve birim yazılı) |
| İki üç durumu karşılaştırma | `tablo` (karşılaştırma her zaman tablo) |
| Sınıflama, tuzak kontrolü | `siniflama` |
| Etkenler (yönüyle: artırır, azaltır) | `kartlar`/`secici` ile etken kartı |
| Kimyasal grup/molekül adı | adın yanında yapı çizimi (`svg`) |
| Sorular | `test` (aşağıda) |

## Yargı kuralları (motor zorlamaz)
- Bir widget = bir fikir; her parçanın tek işi var. Altında "Ne yapacaksın, ne göreceksin" (`not`), en çok 2 kısa cümle; widget mesajdaki sayıların aynısını kullanır.
- Her küçük parçanın hemen altında kendi widget'ı. Konuda en az 4 farklı widget türü, art arda iki aynı tür yok, kaydırıcılı olan toplamın en çok üçte biri.
- Aynı kavram her widget'ta aynı rengi korur; ilk ekranda en çok 4 renk; renk tek başına anlam taşımaz (ikon + yazı).
- Grafiğin altında 1–2 cümle: yatay ne, dikey ne, nasıl okunur.
- Kaynak satırı widget'ın içine yazılmaz.

## Test soruları
- Soru ve şıklar `"English (Türkçe)"` biçiminde yazılır (motor Türkçeyi ayrı satıra koyar); soruda ve şıkta konu adı, adım ya da sayfa numarası yok; her soruya 6. eleman olarak görünmez konu etiketi (`ders.py sonraki` hangi eski konudan soracağını söyler).
- Zor, çok adımlı, tuzaklı sorular; tek adımlı kolay soru yok. Doğru şık hep aynı harfte olmaz.
- Anlatım içindeki sorular widget içindedir (cevap beklenmez). `request_decision` kartı yalnız konunun son mesajıdır (≤4 şık, son şık "İpucu ver").
- Konu anlatımı dışındaki soru setleri (dosya, deneme sınavı) `soru_testi.py` ile W24'tür.

## Yerleşik kartlar (HTML yazılmaz)
K1 yol haritası `step_card_display_v0` · K3 basit çizgi/çubuk grafik `chart_display_v0` (eksen başlıkları zorunlu). Sohbet içi widget için ek beceri (dataviz, artifact-design) YÜKLENMEZ; motor bu kuralları taşır. Ayrı Artifact sayfası yalnız kullanıcı isterse.
