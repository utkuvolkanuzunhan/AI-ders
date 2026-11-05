# Görev: yeni kural çıkınca depoyu güncelle

Kullanıcı kalıcı tercih söylerse ("bundan sonra hep ...", "şu kötü olmuş"):
1. Kuralı o an uygula.
2. Genel mi kişisel mi: genel (kişi bilgisi yok) → depo; kişiye özel → kullanıcının `yerel/ayarlar.md`'si (ölçülebilirse `yerel/profil.json`).
3. Depoya yazarken doğru dosyayı bul (çekirdek / görev / seçenek / gorsel), en küçük değişikliği yap, kural kopyalama. Seçenekli tercih: yeni `secenekler/<harf>/<harf><n>.md` + `araclar/kod.json` satırı, varsayılanı değiştirme. Kod ile denetlenebiliyorsa `anlatim_testi.py`'ye kontrol ve `--kendini-dene` örneği ekle.
4. `DEGISIKLIKLER.md`'nin en üstüne `- tarih · dosya · ne değişti · neden` (ad yazmadan).
5. Doğrudan main'e commit + push (`git pull --rebase` sonra `git push`), commit mesajı `kural: <kısa>`.
6. Kullanıcıya tek satır: hangi dosyada ne değişti.
