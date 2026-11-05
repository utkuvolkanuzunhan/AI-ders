# Görev: sohbet devri

Eşik profilde `devir_esik` (ayar I); adım ortasında devretme. 8. ve 9. mesajda `ders.py sonraki` tek satırlık uyarıyı verir.

1. `python3 araclar/ders.py devir`: `dersler/<ders>/devir/<ad>-<n>.md` notunu durumdan üretir (kod, tempo, tam kaldığı yer, açık soru, zayıf noktalar, açık kusurlar, kullanıcı tercihleri) ve koordinatöre gidecek tek satırı basar. Kuralları nota kopyalama.
2. Koordinatöre: "devam sohbeti aç: <başlık> (devam n), Kod: <geçerli kod>, not: <yol>".
3. Koordinatör bağlantıyı verince kullanıcıya tek satır: "[Buradan devam](#…) ediyoruz, kaldığın yer oraya taşındı." Sonra sohbeti kapat.
4. Ünite sohbetiysen yeni bağlantıyı ders sohbetine raporla birlikte bildir.
