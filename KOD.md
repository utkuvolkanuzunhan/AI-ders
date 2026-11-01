# Ayar kodu

Her ayar bir harf, her seçenek bir rakam. Kod harf sırasıyla yazılır; eksik harf varsayılandır.
Depo varsayılanı: **`A1B3C3D1E3F1G2H1I1J2`**

Örnekler: `A2` (sıkı kaynak modu, gerisi varsayılan) · `B2C2` (ciddi ton, İngilizce terim önce) · `F2/W01.W06-W03` (W01 ve W06 öncelikli, W03 hiç).

Kodu tıklayarak üretmek için galeri sayfası: `gorsel/galeri/galeri.html` (Artifact olarak yayınlanır).

| Harf | Ayar | Seçenekler | Varsayılan |
|---|---|---|---|
| A | Kaynağa bağlılık | **A1** Slayt temel, slayt dışı yalnız Ekstra'da<br>**A2** Sıkı kaynak modu: yalnız kaynakta yazan<br>**A3** Slayt + kitap, ikisi metinde etiketli<br>**A4** Kitap temel, kitap ve genel bilgiyle tamamlanır (yüklenen kaynak varsa o üstün) | A1 |
| B | Ton | **B1** Samimi ve esprili her yerde<br>**B2** Sade ve ciddi her yerde<br>**B3** Anlatım ciddi, sohbet samimi | B3 |
| C | Terim dili | **C1** Türkçe (İngilizce)<br>**C2** İngilizce (Türkçe)<br>**C3** Türkçe (İngilizce) + ders sözlüğü | C3 |
| D | Kaynak gösterimi | **D1** Yalnız sondaki Ekstra düğmesi<br>**D2** Her mesajın altında tek satır<br>**D3** Kısa satır + Ekstra | D1 |
| E | Adım doluluğu | **E1** Hep 6 parça<br>**E2** Hep kısa (tanım, formül, örnek)<br>**E3** Konu tipine göre | E3 |
| F | Widget seçimi | **F1** Sohbet katalogdan kendisi seçer<br>**F2** Beğenilen şablonlar öncelikli<br>**F3** Her konuda önizleme sunar | F1 |
| G | Ekran testi | **G1** Her widget test edilir<br>**G2** Yalnız yapı değişince<br>**G3** Test yok | G2 |
| H | Renk paleti | **H1** Açık tonlar (varsayılan)<br>**H2** Koyu sakin | H1 |
| I | Sohbet devri | **I1** 10 mesaj, adım bitince<br>**I2** 20 mesaj, adım bitince<br>**I3** Bağlam özetlenince | I1 |
| J | Tempo | **J1** Yavaş: tek kavram, her adımda teyit<br>**J2** Normal: adım başına bir alt parça<br>**J3** Hızlı: kısa adımlar, soru blok sonunda | J2 |

Alan varsayılanları (alanlar/<alan>/alan.json; verilen kod bunu da geçer): `eee` (Elektrik-Elektronik Mühendisliği): `A4` depo varsayılanının üstüne biner.

Her seçeneğin tam metni: `secenekler/<harf>/<harf><rakam>.md`. Yeni seçenek eklemek: gorevler/kural-guncelle.md.
