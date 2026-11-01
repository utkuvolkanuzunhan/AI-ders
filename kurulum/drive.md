# Drive klasör yapısı (nasıl kurulur)

Drive yalnız ham arşivdir; sohbetler PDF'i Drive'dan değil, bir kez çevrilmiş metinden okur (gorevler/kaynak-oku.md).

## Yapı
```
<Kök klasör>/
  <Dönem>/
    01 <Ders adı>/
      1 Ders Notları
      2 Slaytlar
      3 Çıkmış Sorular
      4 Ödev-Lab
      5 El Notları-Fotoğraf
    02 <Ders adı>/ ...
  _sistem/            (PDF bölme betiğinin çalışma klasörü; elle dokunma)
```
- Haftalık klasör açma; hafta dosya adından ya da içerikten anlaşılır. Dosya adlandırma zorunlu değil, doğru ders + alt klasör yeter.

## Kurulum yolları
1. **Claude yapar:** Drive bağlayıcısı açıksa sohbete "Drive ders klasörlerimi AI-ders yapısına göre kur, dersler: …" de. Klasörleri açar, id'leri senin `yerel/ayarlar.md`'ne yazar (depoya değil).
2. **Elle:** yukarıdaki yapıyı kendin aç, kök klasör adresini `yerel/ayarlar.md`'ye yaz.

## PDF'ler otomatik metne (isteğe bağlı)
`pdf-bolme/Kod.gs` bir Google Apps Script betiğidir:
1. script.google.com → Yeni proje → kodu yapıştır.
2. `KOK_ID` satırına kök klasör id'sini yaz (adres çubuğunda `folders/` sonrası).
3. Üstten `kur` fonksiyonunu seçip ▶ Çalıştır, izin ver. Sonrası her 10 dakikada bir kendisi çalışır.
4. Betik 12+ sayfalık her PDF'i sayfa sayfa OCR ile `_sistem/harita` altında `[[SAYFA n]]` işaretli Google Dokümanına çevirir. Claude bu metinden `pdf-metin/` dosyasını üretirken basılı sayfa numaralarını doğrular (gorevler/pdf-cevir.md).

## Yeni dosya kontrolü
Günde bir kez bir rutin (ör. akşam) Drive'da yeni dosya var mı bakar; varsa çeviri işçisini başlatır. Yoksa sessiz biter.
