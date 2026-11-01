# Görev: yeni kural çıkınca depoyu güncelle

Kullanıcı sohbette kalıcı bir tercih söylerse ("bundan sonra hep ...", "şu kötü olmuş, ... olsun"):

1. Kuralı o an bu sohbette uygula.
2. Genel mi kişisel mi karar ver:
   - Genel (herkese iyi gelir, kişi bilgisi yok) → depo.
   - Kişiye özel (bir kişinin ders listesi, odak süresi, zayıf noktası) → kullanıcının `yerel/ayarlar.md`'si (dosya yoksa çekirdek §7'ye göre oluştur).
3. Depoya yazarken: doğru dosyayı bul (çekirdek / görev / seçenek / gorsel), en küçük değişikliği yap, kural kopyalama (aynı kural tek yerde).
   - Seçenekli bir tercihse (kimi ister kimi istemez) yeni seçenek dosyası ekle (`secenekler/<harf>/<harf><n>.md`) ve `araclar/kod.json`'a satır ekle; varsayılanı değiştirme.
4. `DEGISIKLIKLER.md`'nin en üstüne bir satır: `- 2026-11-01 · <dosya> · <ne değişti> · <neden / kim istedi (ad yazmadan: "kullanıcı")>`.
5. Doğrudan main'e commit + push (`git pull --rebase` sonra `git push`). Commit mesajı: `kural: <kısa>`.
6. Kullanıcıya tek satır: hangi dosyada ne değişti. Diğer sohbetlere haber verme; bir sonraki açılışta depodan okurlar.
