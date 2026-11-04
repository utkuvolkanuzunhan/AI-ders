# Widget motoru (Neobrutalism)

Model widget için HTML yazmaz, CSS yazmaz: kısa bir **JSON spec** yazar, `araclar/widget.py` HTML'i üretir. Sohbet içi `show_widget` içindir (Artifact değil).

```
python3 araclar/widget.py spec.json cikti.html [--yuk cikti.yuk.json] [--test [--goruntu klasor]] [--karsilastir eski.html]
python3 araclar/widget.py --ornek        # örnek spec
```

| Dosya | Ne |
|---|---|
| `neo.css` | Tek CSS kaynağı (kök `.nb`); renk değeri yok, hepsi `var(--k1)` gibi değişken |
| `engine.js` | Ortak motor: sekme, tema algılama, sınıflama, test, olay yönlendirme; `/*@ad*/` blokları kullanılmıyorsa üretimde atılır |
| `tema-varsayilan.json` | Kişisiz renkler (Neobrutalism resmi değerleri). Kişisel renk depoya girmez: projedeki `yerel/tema.json` yalnız değişenleri yazar, bunun üstüne biner. `roller`: doğru, yanlış, dikkat hangi renk sınıfı |

Renk sınıfları: `k1`–`k6` (kavram renkleri; aynı kavram her derste aynı renk), `rd` (yanlış cevap). Kullanılmayan CSS ve motor kodu üretimde budanır.

## Spec

```json
{"id": "ders-adim-03", "sekmeler": ["Açıklama", "Alıştırma", "Mini test"], "paneller": [[bileşen, ...], [...], [...]]}
```
`id` küçük harf-kebab olur (yayın başlığı da budur). Sekme sayısı = panel sayısı. Metinler düz yazılır (`<`, `&` otomatik kaçışlanır); yalnız `<b>…</b>` ve `<br>` serbest. Terim ve test dili kuralları spec içinde de geçerlidir (anlatim_testi.py denetler).

| `tur` | Alanlar |
|---|---|
| `etiket` | `metin`, `renk` (isteğe bağlı): sarı bölüm etiketi |
| `not` | `yap`, `gor` → "Ne yapacaksın: … Ne göreceksin: …" (ya da serbest `metin`) |
| `formul` | `ogeler`: düğümler `{kod, en, tr, renk}` ve işaret dizeleri (`"+"`, `"="`) |
| `secici` | Çip seçince çubuklar ve sonuç kartı değişir: `baslik`, `secenekler` `[{etiket, degerler:{id:sayı}, sonuc}]`, `cubuklar` `[{id, ad, renk}]`, `eksen` `[0, üst]`, `onek` |
| `kartlar` | Çipe basınca açıklama kartı: `kolon` (2–4), `ogeler` `[{etiket, alt, renk, sk, baslik, metin}]` |
| `cubuklar` | `mx`, `satirlar` `[{ad, alt, deger, etiket, renk, ayrinti}]`, `tikla` (satıra basınca `ayrinti`), `eksen` `[[değer, yazı], ...]` |
| `siniflama` | `baslik`, `secenekler` `[[ad, tr, renk], ...]`, `ogeler` `[[İngilizce, Türkçe, doğru no, açıklama], ...]` |
| `tablo` | `baslik` (hücre `"yazı"` ya da `["yazı", "k1"]`), `satirlar` |
| `zincir` | `dugumler` (`"yazı"` ya da `{metin, alt, renk}`), isteğe bağlı `kollar` (sonda ikiye ayrılan) |
| `kaydirici` | `baslik`, `on_ayarlar` `[{etiket, alt, renk, deger}]`, `baslangic`, `durumlar` `[{alt (alt sınır 0–100), renk, sk, baslik, metin}]`, `grafik` `{svg, x:[x0,x1], y:"140-420*(u-0.5)**2", baslik}` (svg içine `data-dot` işaretli daire), `ek_html` + `ek_js` (`function(s, durumNo)`; alana özgü çizim) |
| `svg` | `svg`: sabit eksenli grafik kutusu |
| `ham` | `html`, `js`: kaçışsız; yalnız hiçbir bileşenin karşılamadığı çizim için |
| `test` | `sorular` `[[soru "İngilizce (Türkçe)", [şıklar], doğru no, açıklama, ipucu, konu etiketi], ...]`; panelin SON bileşeni, panel başına bir tane |

`siniflama` ve `test` tamamlanınca sekmede yeşil onay çıkar. Sorular `var Q=[...]` olarak yazılır (denetim aracı okur); 6. eleman görünmez konu etiketidir.

## Kural özeti (motor zorlar)
`<button>` yok (`div role="button" tabindex="0"`), emoji yok, `text-transform` yok, animasyon/geçiş yok, `color-mix` yok, dış betik/stil/yazı tipi yok, en küçük yazı 13 px, dokunma hedefi ≥ 44 px, açık/koyu tema kendi kartıyla (ana bilgisayar rengi yalnız tema algılamak için). `--test` bunların hepsini ve JS hatasını ölçer.

## Yayın
`--yuk` ile `{"title","widget_code"}` JSON'u yazılır (UTF-8, `\u` kaçışı yok). `widget_code` bu dosyadan birebir yapıştırılır, elle yeniden yazılmaz; yayından sonra oturum kaydıyla karşılaştırma `araclar/ders.py dogrula`dır.
