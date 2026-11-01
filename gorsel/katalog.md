# Widget kataloğu

Konuya göre seç (ayar F). Şablonu kopyala, yalnız veriyi (dizi, metin, sayı) değiştir; yapı değişirse ekran testi (ayar G). Renkler `--c1 … --c5` (ayar H).

| Kimlik | Tür | Ne zaman | Dosya |
|---|---|---|---|
| W01 | Dokunulabilir kutulu formül | Formülün terimleri; kesir ve üs | sablonlar/W01-formul-kutulu.html |
| W02 | Satır satır türetme | Formül nereden geliyor | sablonlar/W02-turetme-satir-satir.html |
| W03 | Sabit eksenli doğru + kaydırıcı | Doğrusallaştırma, eğimden değer | sablonlar/W03-grafik-dogru.html |
| W04 | Sabit eksenli eğri + iki nokta | Bir değişkenin etkisi, iki durum | sablonlar/W04-grafik-egri.html |
| W05 | Ekstra düğmesi | Konu sonu: kaynaklar, slayt dışı bilgi, ipucu | sablonlar/W05-ekstra.html |
| W06 | Adım adım çözümlü hesap | Sınav tipi çözümlü örnek | sablonlar/W06-adim-adim-hesap.html |
| W07 | Sınıflama ağacı (ikonlu) | Sınıflar ve alt türler | sablonlar/W07-siniflama-agaci.html |
| W08 | Karşılaştırma tablosu | İki-üç yöntem/durum yan yana | sablonlar/W08-karsilastirma-tablosu.html |
| W09 | Doğru/yanlış kartları | Tuzak kontrolü | sablonlar/W09-dogru-yanlis-kartlari.html |
| W10 | Mini test / tek soru | Anlatım içi soru (1 soru, İpucu düğmeli) ya da blok/konu sonu 3 soru | sablonlar/W10-mini-test.html |
| W11 | Özet kartları + sözlük | Konu sonu özet, TR–EN sözlük | sablonlar/W11-ozet-kartlari.html |
| W12 | Akış şeması | Yöntem/süreç sırası | sablonlar/W12-akis-semasi.html |
| W13 | Kimyasal yapı kartı | Fonksiyonel grup/molekül adı geçince: ad + formül + yapı çizimi | sablonlar/W13-kimyasal-yapi.html |
| W14 | Etken kartları | Bir olayı etkileyen etkenler ve yönleri | sablonlar/W14-etken-kartlari.html |

## Yerleşik kartlar (HTML yazılmaz)
| Kimlik | Ne | Nasıl |
|---|---|---|
| K1 | Yol haritası | `post_widget` · `step_card_display_v0` |
| K2 | Cevabı dönen soru (yalnız konunun son mesajı) | `request_decision` (≤4 şık, son şık "İpucu ver", önerilen o); anlatım ortasında kullanılmaz, akışı durdurur |
| K3 | Basit çizgi/çubuk grafik | `post_widget` · `chart_display_v0` (eksen başlıkları zorunlu) |

## Şablonu olmayan türler (stil.md'ye göre sıfırdan, sonra şablona eklenir)
- Seçenek düğmeleri + sonuç kartı ("eğer ... ise" durumları)
- Sürükle-bırak / eşleştirme (terim–tanım)
- Sıralama (çözüm adımlarını doğru sıraya diz)
- Büyük sayı kartı (sonuç, birim, yorum)
- Ölçek şeridi / zaman çizelgesi (büyüklük sıralaması)
- Simülasyon (parçacık, dağılım, enerji tepesi)
- Kavram haritası (dokunulabilir düğümler)
- Ekipman/süreç çizimi (SVG; artifact-diagramming becerisi)

Yeni bir tür iyi çalışırsa `W13…` olarak buraya ve `sablonlar/`a ekle (gorevler/kural-guncelle.md), galeriyi yeniden üret (`python3 araclar/uret.py`).
