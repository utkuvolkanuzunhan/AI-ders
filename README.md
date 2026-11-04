# AI-ders

Claude sohbetlerinde ders anlatımını tutarlı, kaynağa sadık ve düşük token'la yaptırmak için kural deposu. Kurallar modülerdir: her sohbet yalnız rolüne ve ayar koduna ait parçaları okur.

## Hızlı başlangıç

1. Projenin talimatına [kurulum/proje-talimati.md](kurulum/proje-talimati.md) içindeki 3 satırı yapıştır.
2. Sohbete konuyu yaz. İstersen bir ayar kodu ekle, örn. `Kod: A2B3C3D1E3F1G2H1I1`.
3. Sohbet [BASLA.md](BASLA.md)'yi uygular: depoyu klonlar, `araclar/paket.py` ile tek okuma paketini üretir ve başlar.

## Kişisel ayarlar

Her projede `yerel/ayarlar.md` bulunur (yoksa ilk sohbet şablondan oluşturur) ve kişiye özel her şey yalnız orada tutulur: kod, alan, ders listesi, takvim, tercihler. Depodaki varsayılanı depoya dokunmadan ezer. Şablon: [kurulum/yerel-ayarlar-sablonu.md](kurulum/yerel-ayarlar-sablonu.md), EEE örneği: [kurulum/yerel-ayarlar-eee.md](kurulum/yerel-ayarlar-eee.md). Alanlar için bkz. [alanlar/README.md](alanlar/README.md).

## Ayar kodu

Her ayar bir harf, her seçenek bir rakamdır. Depo varsayılanı: **`A1B3C3D1E3F1G2H1I1J2`**.

| Harf | Ayar | Varsayılan |
|---|---|---|
| A | Kaynağa bağlılık | A1 slayt temel, ek bilgi yalnız Ekstra'da (A2 sıkı kaynak, A3 slayt + kitap, A4 kitap temel) |
| B | Ton | B3 anlatım ciddi, sohbet samimi |
| C | Terimler | C3 Türkçe (İngilizce) + ders sözlüğü |
| D | Kaynak gösterimi | D1 yalnız sondaki Ekstra düğmesi |
| E | Adım doluluğu | E3 konu tipine göre |
| F | Widget seçimi | F1 sohbet seçer (F2 = beğenilen liste) |
| G | Ekran testi | G2 yalnız yapı değişince |
| H | Palet | H1 yumuşak palet |
| I | Devir | I1 10 mesaj, adım bitince |
| J | Tempo | J2 normal; J1 yavaş, J3 hızlı (sohbette "daha hızlı / daha yavaş" denince değişir ve devredilir) |

A'nın dördüncü seçeneği **A4** kitap temelli derslere (EEE alanının varsayılanı) göredir: kitap temel, genel bilgiyle tamamlanır, yüklenen kaynak varsa o üstündür.

Tüm seçenekler: [KOD.md](KOD.md). Kodu görsel olarak seçmek için galeri: [gorsel/galeri/galeri.html](gorsel/galeri/galeri.html).

## Klasörler

| Klasör | İçerik |
|---|---|
| `cekirdek/` | Her sohbetin okuduğu temel kurallar (dil, hız, mesaj biçimi, formül, soru, gizlilik) |
| `roller/` | ünite, ders yöneticisi, koordinatör, PDF çevirici, soru çözümü, soru seti |
| `gorevler/` | kaynak okuma, PDF yönlendirme, konu anlatma, anlatım denetimi, soru sorma, özet/test, devir, PDF çevirme, kural güncelleme |
| `secenekler/<harf>/` | Ayar kodunun her seçeneği ayrı dosya |
| `gorsel/` | Stil rehberi, şablon kataloğu (W01–W24), şablonlar, ekran testi, galeri; `soru-testi/` W24 örnek verisi; `motor/` Neobrutalism widget motoru (CSS, motor, kişisiz tema) |
| `dersler/<ders>/` | Derse özel kaynak önceliği, tuzaklar ve TR–EN sözlük |
| `claude-sorunlari/` | Claude arayüzünün bilinen sorunları ve denenmiş yazım kuralları (formül/KaTeX vb.), alandan bağımsız, her paketle gelir |
| `kurulum/` | Proje talimatı, yerel ayar şablonu, Drive ve PDF bölme kurulumu |
| `alanlar/<alan>/` | Alana özgü katman: kurallar, widget kataloğu, varsayılan kod (`eee`) |
| `kisiler/` | Kişiye özel katman (ileride) |
| `araclar/` | `kod.json` (kodun tek kaynağı), `paket.py` (okuma paketi, PDF kapısı), `kaynak.py` (pdf-metin'den sayfa aralığı okur; PDF'i reddeder), `uret.py` (KOD.md + galeri üretir), `soru_testi.py` (soru seti JSON'u → W24 test HTML'i), `anlatim_testi.py` (anlatım mesajını formül, boşluk ve biçim kurallarına karşı denetler, hata raporu üretir; ek kurallar `anlatim_testi_ek.py`: terim dili, emoji serisi, widget ve test soruları), `widget.py` (Neobrutalism widget motoru: JSON spec → HTML, `--test` ekran testi, `--karsilastir`; bkz. `gorsel/motor/README.md`), `profil.py` (kişisel ölçülebilir tercihler `yerel/profil.json`: okur, doğrular, katmanları birleştirir; `--goster`) |

## Araçlar

```bash
python3 araclar/paket.py --rol unite --kod A1B3C3D1E3F1G2H1I1J2 --ders statistics   # okuma paketi
python3 araclar/paket.py --kod-coz A2F2                                            # kodu açıkla
python3 araclar/kaynak.py dersler/<ders>/pdf-metin/<ad>.md 9 16                    # kaynaktan basılı s.9–16
python3 araclar/uret.py                                                            # KOD.md ve galeriyi yeniden üret
python3 araclar/soru_testi.py veri.json cikti.html                                 # çoktan seçmeli soru seti → test widget'ı (gorevler/soru-seti.md)
python3 araclar/anlatim_testi.py mesaj.md [--rapor]                                 # anlatım mesajı denetimi (gorevler/anlatim-kontrol.md); --kendini-dene kuralların denemesi
python3 araclar/anlatim_testi.py widget.html|sorular.json --test-turu mini --ders <ders>  # widget ve test sorusu denetimi (dil, konu ipucu, karışık sorular)
```

## Çeviri ve anlatım ayrı

PDF/slayt yüklenen sohbet onu çevirmez ve anlatmaz; çeviri sohbeti ister. Çeviri sohbeti yalnız metni yazar ve yeni anlatım sohbeti ister. Anlatım sohbeti kaynağı yalnız `kaynak.py` ile okur. `paket.py --ek` ve `kaynak.py` çevrilmemiş dosyada durur.

## Gizlilik

Depo herkese açıktır. Kişi adı, e-posta, Drive/sohbet kimliği, not veya hoca materyali yazılmaz. Kişiye özel her şey proje dosyalarındaki `yerel/ayarlar.md` içinde kalır.

## Değişiklikler

Kural değişiklikleri doğrudan `main`'e yazılır ve [DEGISIKLIKLER.md](DEGISIKLIKLER.md)'ye bir satır eklenir.
