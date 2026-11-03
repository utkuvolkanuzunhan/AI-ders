# Görev: PDF'i metne çevir (bir kez)

Anlatım sohbetinde değil, ayrı bir işçide yapılır.

## Yöntem: karma (önce kod, model yalnız gereken sayfalarda)
Sayfaları modelle okumak en pahalı yoldur. Önce MarkItDown (kod, token harcamaz) çevirir; model yalnız aracın işaretlediği sayfalara bakar.
1. Kur (bir kez): `pip install 'markitdown[pdf,pptx,docx]'`
2. Çevir: `python3 /tmp/ai-ders/araclar/pdf_cevir.py cevir <dosya> --cikti dersler/<ders>/pdf-metin/<ad>.md --baslik "<PDF adı>"` (PDF, .pptx, .docx). Araç sayfa işaretlerini ve basılı numarayı kendisi yazar, numarayı aşağıdaki kurala göre doğrular, "model görmeli" sayfaları listeler ve resimlerini üretir.
3. Model görmeli sayfalar: tablo, grafik/şekil/diyagram, görsel, metni boş ya da bozuk sayfa, basılı numarası belirsiz sayfa. Yalnız bunların resmine bak (Read). Dosyada her birinin altında `[[MODEL-OKU | neden: …]]` satırı var: sil; çizim, şema, grafik ve tabloyu `[ŞEKİL …]` / `[TABLO …]` ile mantık diliyle yaz (aşağıdaki Çıktı); kodun bozuk çıkardığı yazıyı (dağınık eksen harfleri, karışık tablo satırları) düzelt; numara `?` ise resimden oku. İşaretsiz sayfayı okuma ve değiştirme: kod metni aynen çıkarmıştır.
4. Kontrol (zorunlu): `python3 /tmp/ai-ders/araclar/pdf_cevir.py dogrula <md>`. HATA (çıkış kodu 1: bekleyen `[[MODEL-OKU`, sayfa sırası bozukluğu) düzelmeden iş bitmez; UYARI'ları oku.
5. İndeks: `python3 /tmp/ai-ders/araclar/pdf_cevir.py indeks <md>` sayfa başına başlık taslağı verir; aşağıdaki İndeks biçiminde konu aralıklarına topla.

Sınırlar: OCR yok. Metin katmanı olmayan fotoğraf slayt ya da taranmış sayfalar "metin yok" diye işaretlenir; dosyanın hepsi böyleyse tasarruf %0'dır ve model eskisi gibi hepsini okur. Word'de sayfa resmi üretilmez (görselli bölüm için dosyayı önce PDF'e çevir). MarkItDown kurulamıyorsa (ağ yok) modelle sayfa sayfa oku ve aşağıdaki Çıktı biçimine uy. `kaynak.py`, içinde `[[MODEL-OKU` kalan sayfayı anlatım sohbetine okutmaz.

## Girdi
- Proje klasörüne ya da sohbete yüklenmiş PDF, ya da Drive'daki PDF'in OCR metni (kurulum/pdf-bolme betiği `[[SAYFA n]]` işaretli Google Dokümanı üretir; bu metinde araç gerekmez).
- Slayt dosyası (.pptx) da olabilir: araç metni ve not alanını slayt slayt çıkarır, slayt sırası numaradır; diyagram/görsel/grafik içeren slaytlar model görmeli sayfa olur. Word (.docx) başlıklara göre bölümlere ayrılır, bölüm sırası numaradır.

## Çıktı
`dersler/<ders>/pdf-metin/<kısa-ad>.md` (kullanıcının proje klasöründe):
```
# <PDF adı> (<sayfa sayısı> sayfa)
sayfa eşlemesi: basılı = pdf − 3 (s.1–120), araç doğruladı
[[SAYFA 9 | pdf 12]]
<sayfadaki yazı aynen>
[ŞEKİL 1.2: <ne gösteriyor; eksenler, birimler, oklar, değerler, ilişkiler; mantık diliyle>]
[TABLO 3: <markdown tablo olarak aynen>]
[[SAYFA 10 | pdf 13]]
...
```
- Yazılar aynen; özetleme, yorum ekleme yok. Kodla gelen yazı (düz metin formüller dahil, `TR = P × Q`) aynen kalır.
- Çizim, şema, grafik, tablo: mantık diliyle (ne gösteriyor, eksenler, oklar, değerler, ilişkiler). Numarası korunur.
- Modelin yazdığı formüller LaTeX olarak (`$\dfrac{k_{2}}{k_{1}}$`); sohbet yazım kuralları `claude-sorunlari/formuller.md`.
- PDF numarası ve her sayfanın basılı numarası + PDF sıra numarası korunur (aşağıya bak).

## Sayfa numarası: kitabın kendi numarası esas
Kaynak gösterirken kullanılan numara, sayfanın ÜZERİNDE BASILI olan numaradır (genelde en altta; bazen üst köşede, kenarda ya da başlık satırında). PDF görüntüleyicinin sıra numarası değil. Araç bunu sayfa kenarındaki (alt %15, üst %10) tek başına sayıdan bulur, en çok oy alan sabit farkla doğrular ve numara satırını metinden çıkarır; model yalnız aracın `?` ya da `not:` bıraktığı sayfalarda devreye girer.
1. İşaret `[[SAYFA <basılı> | pdf <sıra>]]`: ikisi de her sayfada var. Araç bulamadığı sayfaya komşulardan fark çıkarabilirse `~n`, çıkaramazsa `?` yazar; ikisi için model resme bakar (`?` sayfalar model görmeli sayılır).
2. Doğrulama (araç `cevir` ve `dogrula` ile yapar, model sonucu okur):
   - Basılı numaralar ardışık mı? Atlama ya da tekrar varsa o sayfaları yeniden oku.
   - Fark sabit mi? (basılı = pdf − k). Fark bir yerde değişirse (boş sayfa, ek, bölüm kapağı) işarete nedeni yazılır: `[[SAYFA 23 | pdf 27 | not: s.22'den sonra numarasız ek sayfa]]`; araç farkı değişince `not:` ekler, nedenini model resimden yazar.
   - Tahmini numara kaynak olarak kesinmiş gibi kullanılmaz: `~23` için "s.~23" yazılır, `?` için sayfa numarası verilmez.
   - Roma rakamı (ön sözler) ayrı yazılır: `[[SAYFA xii | pdf 14]]`.
   - Slaytta basılı numara yoksa slayt sırası kullanılır ve dosya başına `numara: slayt sırası` yazılır.
3. Dosyanın başındaki `sayfa eşlemesi` ya da `numara:` satırını araç yazar.

## İndeks
Aynı klasördeki `indeks.md`'ye ekle:
```
## <PDF adı> (<kısa-ad>.md) · basılı = pdf − 3
- s.1–3 (pdf 4–6): <konu>
- s.4–8 (pdf 7–11): <konu>
```
Konu listesini kullanıcıya değil, ilgili dersin sohbetine gönder.

## Büyük PDF
- Araç tüm dosyayı birkaç saniyede çevirir; yarım kalan iş yalnız model görmeli sayfalardadır. Yarıda kalırsa dosyada kalan `[[MODEL-OKU` satırları ilerlemeyi gösterir (`dogrula` bekleyen sayfaları listeler); sonraki tur oradan devam eder.
