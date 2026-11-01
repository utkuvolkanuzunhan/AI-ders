# AI-ders

Claude sohbetlerinde ders anlatımını tutarlı, kaynağa sadık ve düşük token'la yaptırmak için kural deposu. Kurallar modülerdir: her sohbet yalnız rolüne ve ayar koduna ait parçaları okur.

## Hızlı başlangıç

1. Projenin talimatına [kurulum/proje-talimati.md](kurulum/proje-talimati.md) içindeki 3 satırı yapıştır.
2. Sohbete konuyu yaz. İstersen bir ayar kodu ekle, örn. `Kod: A2B3C3D1E3F1G2H1I1`.
3. Sohbet [BASLA.md](BASLA.md)'yi uygular: depoyu klonlar, `araclar/paket.py` ile tek okuma paketini üretir ve başlar.

## Ayar kodu

Her ayar bir harf, her seçenek bir rakamdır. Depo varsayılanı: **`A1B3C3D1E3F1G2H1I1J1`**.

| Harf | Ayar | Varsayılan |
|---|---|---|
| A | Kaynağa bağlılık | A1 slayt temel, ek bilgi yalnız Ekstra'da (A2 = sıkı kaynak modu) |
| B | Ton | B3 anlatım ciddi, sohbet samimi |
| C | Terimler | C3 Türkçe (İngilizce) + ders sözlüğü |
| D | Kaynak gösterimi | D1 yalnız sondaki Ekstra düğmesi |
| E | Adım doluluğu | E3 konu tipine göre |
| F | Widget seçimi | F1 sohbet seçer (F2 = beğenilen liste) |
| G | Ekran testi | G2 yalnız yapı değişince |
| H | Palet | H1 yumuşak palet |
| I | Devir | I1 10 mesaj, adım bitince |
| J | Tempo | J1 normal (sohbette "daha hızlı / daha yavaş" denince değişir ve devredilir) |

Tüm seçenekler: [KOD.md](KOD.md). Kodu görsel olarak seçmek için galeri: [gorsel/galeri/galeri.html](gorsel/galeri/galeri.html).

## Klasörler

| Klasör | İçerik |
|---|---|
| `cekirdek/` | Her sohbetin okuduğu temel kurallar (dil, hız, mesaj biçimi, formül, soru, gizlilik) |
| `roller/` | ünite, ders yöneticisi, koordinatör, PDF çevirici, soru çözümü |
| `gorevler/` | kaynak okuma, konu anlatma, soru sorma, özet/test, devir, PDF çevirme, kural güncelleme |
| `secenekler/<harf>/` | Ayar kodunun her seçeneği ayrı dosya |
| `gorsel/` | Stil rehberi, şablon kataloğu (W01–W14), şablonlar, ekran testi, galeri |
| `dersler/<ders>/` | Derse özel kaynak önceliği, tuzaklar ve TR–EN sözlük |
| `kurulum/` | Proje talimatı, yerel ayar şablonu, Drive ve PDF bölme kurulumu |
| `kisiler/` | Kişiye özel katman (ileride) |
| `araclar/` | `kod.json` (kodun tek kaynağı), `paket.py` (okuma paketi), `uret.py` (KOD.md + galeri üretir) |

## Araçlar

```bash
python3 araclar/paket.py --rol unite --kod A1B3C3D1E3F1G2H1I1J1 --ders statistics   # okuma paketi
python3 araclar/paket.py --kod-coz A2F2                                            # kodu açıkla
python3 araclar/uret.py                                                            # KOD.md ve galeriyi yeniden üret
```

## Gizlilik

Depo herkese açıktır. Kişi adı, e-posta, Drive/sohbet kimliği, not veya hoca materyali yazılmaz. Kişiye özel her şey proje dosyalarındaki `yerel/ayarlar.md` içinde kalır.

## Değişiklikler

Kural değişiklikleri doğrudan `main`'e yazılır ve [DEGISIKLIKLER.md](DEGISIKLIKLER.md)'ye bir satır eklenir.
