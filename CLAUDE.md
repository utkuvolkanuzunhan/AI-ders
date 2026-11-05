# AI-ders deposu

Bu bir kural deposudur, uygulama kodu yoktur. Bu dosya bir HARİTADIR: kuralı burada kopyalama, ilgili dosyaya bağlan.

## 1. Ders/proje sohbetiysen (depoyu okuyan sohbet)

`BASLA.md`'yi uygula. Her seferinde sıra aynıdır:

1. Depoyu klonla, `araclar/paket.py --rol <rol> --kod <kod> --ders <ders>` ile paketini üret ve OKU; paketin çıktısı sohbetin kuralıdır, başka kural dosyası okuma (BASLA §1–4).
2. Rolü, kodu ve alanı bul: mesajdaki değerler → kullanıcının `yerel/ayarlar.md`'si → depo varsayılanı (BASLA §2–3b).
3. Kullanıcının proje klasöründeki yerel durumu oku: `yerel/ayarlar.md`, `dersler/<ders>/hafiza.md`, varsa devir notu (BASLA §5).
4. Selamlama ve kural özeti yazmadan işe başla (BASLA §6).
5. Anlatım yapan rol her mesajı ve widget'ı göndermeden önce `python3 araclar/anlatim_testi.py` ile denetler; HATA varsa göndermez (BASLA §7, `gorevler/anlatim-kontrol.md`).

Sohbete PDF/slayt/görsel eklendiyse: o sohbet çevirmez ve anlatmaz; `paket.py --ek <dosya>` verir ve çıkış kodu 3 ise basılan yönlendirmeyi uygular (`gorevler/pdf-yonlendir.md`). Çeviri ayrı sohbette yapılır (`gorevler/pdf-cevir.md`), anlatım kaynağı yalnız `araclar/kaynak.py` ile çevrilmiş metinden okunur.

Kullanıcı sohbette kalıcı bir tercih söylerse: genel ise depoya, kişiye özel ise onun `yerel/ayarlar.md`'sine (`gorevler/kural-guncelle.md`).

## 2. Depoyu geliştiriyorsan

- Kural tek yerde durur (kopyalama yok). Doğru yeri bul: `cekirdek/` (herkes), `roller/`, `gorevler/`, `secenekler/`, `gorsel/`. En küçük değişikliği yap.
- Seçenekli tercih (kimi ister kimi istemez): yeni `secenekler/<harf>/<harf><n>.md` + `araclar/kod.json` satırı; varsayılanı değiştirme.
- Widget şablonu ekleyince ya da `kod.json` değişince `python3 araclar/uret.py` ile KOD.md ve galeriyi yeniden üret.
- Alana özgü kural çekirdeğe değil `alanlar/<alan>/` katmanına yazılır (`alanlar/README.md`); ders kartının başındaki `alan: <ad>` satırı dersi alana bağlar.
- Claude arayüzü sorunları (formül görüntüleme vb.) alandan bağımsız `claude-sorunlari/` bölümüne yazılır (README'sindeki adımlar); `paket.py` hepsini her pakete ekler. Çekirdek ve alan kuralları formül biçimini tekrar yazmaz, oraya bağlanır.
- Her değişiklik `DEGISIKLIKLER.md`'ye bir satır: `- tarih · dosya · ne değişti · neden` (en yenisi en üstte).
- Değişiklikten sonra çalıştır: `python3 araclar/anlatim_testi.py --kendini-dene` ve `python3 araclar/uret.py`; hata varsa düzeltmeden bırakma. Paket etkileniyorsa `python3 araclar/paket.py --rol unite --ders <ders>` ile dene.
- Kullanıcı PR istediyse PR aç ve onaysız birleştirme; aksi hâlde `gorevler/kural-guncelle.md` akışı geçerlidir.

## 3. Gizlilik

Depo herkese açık: kişi adı, e-posta, id (Drive/sohbet), hoca adı, şube/ders kodu, okul sistemi bilgisi, hoca materyali ve not yazma. Kişiye özel her şey kullanıcının proje klasöründeki `yerel/ayarlar.md` ve `yerel/denetim.json` dosyalarında kalır.

## 4. Nereye bakmalı

| İhtiyaç | Dosya |
|---|---|
| Sohbet nasıl başlar | `BASLA.md` |
| Klasörler, araç komutları, ayar kodu | `README.md`, `KOD.md` |
| Temel kurallar (dil, hız, mesaj biçimi, formül, soru, görsel) | `cekirdek/temel.md` |
| Widget görünümü | `gorsel/stil.md`, `gorsel/katalog.md` |
| Yeni kullanıcı kurulumu | `kurulum/README.md` |
| Önceki değişiklikler | `DEGISIKLIKLER.md` |
