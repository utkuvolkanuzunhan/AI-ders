# Claude sorunları

Claude arayüzünün (sohbet uygulaması, tablet, telefon) bilinen sorunları ve bunlara karşı **denenmiş** yazım kuralları. Alandan bağımsızdır: hangi dersi ya da alanı çalışırsan çalış, bu sorunlar aynıdır. Claude ile ders çalışan herkesin işine yarasın diye ayrı tutulur.

## Neden ayrı bir bölüm?
Bir sohbet arayüzü her LaTeX komutunu ya da biçimi göstermez; gösteremediğinde formül yerine ham kod görünür. Bu, ders anlatımını okunmaz yapar. Burada her sorun için belirti, işe yarayan kalıp ve test tarihi tutulur; böylece aynı hata ikinci kez yapılmaz.

## İçindekiler
| Dosya | Konu |
|---|---|
| [formuller.md](formuller.md) | Sohbet mesajlarında formül (KaTeX) yazımı: hangi komutlar ham görünür, hangi kalıplar güvenli; kurallar `araclar/formul_denetle.py` ile kodla denetlenir |

## Okuma paketi
`araclar/paket.py` bu klasördeki her `.md` dosyasını (README hariç) tüm rollerin paketine ekler; yani buraya yazılan kural her alanda ve her sohbette geçerlidir. Bu yüzden dosyalar kısa ve emir kipinde tutulur.

## Yeni sorun eklemek
1. `claude-sorunlari/<konu>.md` oluştur. Sırayla: **Belirti** (ne görünüyor), **Kural** (ne yazılır, ne yazılmaz; doğru ve yanlış örnek), **Test** (tarih, nerede denendi).
2. Yukarıdaki tabloya satır ekle.
3. Kural kodla denetlenebiliyorsa betiğe (ör. `araclar/formul_denetle.py`) ve testine ekle; kural yazıyla bırakılmaz.
4. Kuralı başka dosyada tekrar yazma; çekirdek ya da alan kuralı gerekiyorsa bu dosyaya bağla.
5. `DEGISIKLIKLER.md`'ye bir satır ekle.

Teyit edilmemiş bir varsayım kural gibi yazılmaz; ilgili dosyanın "Teyit bekleyen" bölümüne gider ve test edilince taşınır. Arayüz değişince kurallar yeniden denenir (dosyadaki test tarihine bak).
