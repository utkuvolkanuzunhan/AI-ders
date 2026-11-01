# BAŞLA: her sohbet önce bunu uygular

Bu depo, AI ile ders çalışırken anlatımın nasıl yapılacağını tek yerden yönetir. Bir sohbet şöyle başlatılır:

> AI-ders oku. Rol: unite. Ders: reaction-kinetics, Ü2 Reaksiyon mertebeleri. Kod: A1B3C3D1E3F1G2H1I1J2

Rol, ders ya da kod eksik olabilir; aşağıdaki adımlar eksiği tamamlar.

## 1. Depoyu al
```
git clone --depth 1 https://github.com/utkuvolkanuzunhan/AI-ders /tmp/ai-ders 2>/dev/null || git -C /tmp/ai-ders pull -q
```
(Depo sohbete zaten ekliyse o klasörü kullan.)

## 2. Rolü bul
| Başlangıç mesajında | Rol |
|---|---|
| Kullanıcı bu sohbete PDF/slayt yüklediyse (başka rol yazsa bile) | `pdf-cevirici`: bu sohbet anlatım yapmaz |
| "Rol: …" yazıyorsa | o |
| Bir konu/ünite anlatılacaksa | `unite` |
| Ders yönetimi, ünite listesi, hafıza | `ders-yoneticisi` |
| Projenin ana sohbeti | `koordinator` |
| PDF/slayt metne çevrilecekse | `pdf-cevirici` |
| Tek soru / çıkmış soru çözümü | `soru-cozumu` |
Emin değilsen `unite`.

## 3. Kodu bul
Sırayla: başlangıç mesajındaki "Kod:" → kullanıcının proje klasöründeki `yerel/ayarlar.md` içindeki "Kod:" satırı → alanın varsayılan kodu (alanlar/<alan>/alan.json) → depo varsayılanı (araclar/kod.json). Kod bir kısmı yazılmışsa (ör. yalnız `A2`) eksik harfler varsayılandır. Kişisel kod depodaki varsayılanı ezer; depoya dokunmadan değiştirilir.

## 3b. Alanı bul
Kullanıcının proje klasöründeki `yerel/ayarlar.md` içinde "Alan:" satırı varsa (ör. `Alan: eee`) o alandır; yoksa paket.py alanı ders kartından bulur (kartın başındaki `alan:` satırı). İkisi de yoksa alan yoktur ve yalnız çekirdek kurallar geçerlidir. Alan katmanı (`alanlar/<alan>/`) alanın kurallarını, widget'larını ve varsayılan kodunu ekler (alanlar/README.md).

## 4. Paketi oluştur ve OKU
```
python3 /tmp/ai-ders/araclar/paket.py --rol <rol> --kod <kod> --ders <ders-klasörü> [--alan <alan>]
```
Çıktının tamamı bu sohbetin kuralıdır; başka kural dosyası okuma. Ders klasör adları: `ls /tmp/ai-ders/dersler`.

## 5. Yerel durumu oku
Kullanıcının proje klasöründe (varsa): `yerel/ayarlar.md` (yoksa çekirdek §7'ye göre oluşturulur), `dersler/<ders>/hafiza.md`, devir notu (brief'te verildiyse). Kaynak metni yalnız gerektiği kadar (gorevler/kaynak-oku.md).

## 6. Başla
Selamlama ve kural özeti yazmadan doğrudan işe başla. Kullanıcıya paketten ya da depodan söz etme; yalnız işi yap.

## Sorun çıkarsa
- Klon başarısızsa: GitHub'dan dosyaları tek tek oku (BASLA → paket.py'nin okuduğu dosyalar: cekirdek/temel.md, roller/<rol>.md, gorevler/…, secenekler/…).
- Python yoksa: aynı dosyaları elle sırayla oku.
- Kod hatalıysa paket.py hangi harfin yanlış olduğunu ve seçenekleri yazar; kullanıcıya tek satırla sor ya da varsayılanla devam et.
