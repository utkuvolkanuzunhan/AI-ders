# Görev: her mesajı ve widget'ı kodla denetlemek

Göndermeden önce her mesaj ve widget `python3 araclar/ders.py adim NN taslak.md [spec.json]` ile geçer (mesaj, widget, karışık soru, sadakat denetimi). HATA varsa gönderme: düzelt, yeniden çalıştır (en çok 2 tur); UYARI'ya bak, haklıysa düzelt. Gönderilen metin denetlenenle aynı olmalı. Düzelmeyen hata kalırsa yine gönder ama hemen 2 satır rapor yaz; gizleme.

- Durum dosyası yoksa: `python3 araclar/anlatim_testi.py taslak.md [--ilk|--idari] --ders <ders>`; widget `.html` ise `--test-turu mini --konu "<adım adı>"`. Kodların anlamı: `anlatim_testi.py --kodlar`.
- Kişisel ölçülebilir tercihler (terim dili, emoji, mini test sayısı, test dili) `yerel/profil.json`'dadır; araç kendisi bulur (`python3 araclar/profil.py --goster`). Yeni ölçülebilir tercih hem `ayarlar.md`'ye hem profile yazılır.
- Gönderdikten sonra: `ders.py yayinlandi NN`, `ders.py dogrula NN` (yayın birebir mi). Formül ham görünüyorsa mesajı düzelt ve kaçan kalıbı `claude-sorunlari/formuller.md` ile `anlatim_testi.py` testlerine ekle (`gorevler/kural-guncelle.md`).
- Konu sonu: `ders.py rapor` iki satırını sohbete olduğu gibi yaz ("0 hata" dahil).
