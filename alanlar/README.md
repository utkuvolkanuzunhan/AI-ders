# Alan katmanı

Çekirdek kurallar (cekirdek/, roller/, gorevler/, secenekler/, gorsel/) her alan için aynıdır. Bir alanın (ör. gıda mühendisliği, elektrik-elektronik) kendine özgü kuralları varsa `alanlar/<alan>/` altında durur ve yalnız o alanın sohbetlerine eklenir. Çekirdek ve diğer alanlar değişmez.

```
alanlar/<alan>/
  alan.json      ad, varsayilan_kod (depo varsayılanının üstüne biner), kurallar, katalog
  kurallar.md    o alanın kuralları (her rol okur)
  katalog.md     o alanın widget'ları (anlatım rolleri okur; şablonlar gorsel/sablonlar/ içinde)
```

## Bir sohbet hangi alanda?
Sırayla: `paket.py --alan <ad>` (BASLA.md, kullanıcının `yerel/ayarlar.md` dosyasındaki `Alan:` satırından verir) → ders kartının başındaki `alan: <ad>` satırı → yok. Alanı olmayan sohbet yalnız çekirdek kurallarla çalışır (gıda dersleri şu an böyle).

## Önceliğin sırası
çekirdek → alan kuralları → rol ve görevler → ayar kodu seçenekleri → ders kartı → kullanıcının sohbette söyledikleri.

## Yeni alan eklemek
1. `alanlar/<alan>/alan.json`, `kurallar.md`, `katalog.md` oluştur.
2. O alanın ders kartlarının başına `---`, `alan: <alan>`, `---` yaz.
3. `python3 araclar/paket.py --rol unite --ders <ders>` ile paketi dene.

Alanlar: `eee` (Elektrik-Elektronik Mühendisliği, varsayılan kod `A4`).
