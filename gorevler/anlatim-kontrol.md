# Görev: her anlatım mesajını kodla denetlemek

Anlatım mesajı (formül, boşluk, biçim) göndermeden önce `araclar/anlatim_testi.py` ile denenir. Kuralların kendisi `cekirdek/temel.md` §3–§4 ve `claude-sorunlari/formuller.md`'dedir; test onları kodla uygular, burada kopyalanmaz. Bulgu kodu hangi kurala bağlı olduğunu söyler (F formül, B boşluk, S metin biçimi).

## Her mesaj (konunun ilk metni dahil)
1. Mesajı taslak dosyaya yaz ve testi tek `Bash` çağrısında çalıştır (süre saniyenin altında; ilk metin ≤ 30 sn kuralını bozmaz):
   ```
   mkdir -p /tmp/anlatim/<konu> && cat > /tmp/anlatim/<konu>/NN.md <<'EOF'
   <mesajın tam metni, gönderilecek haliyle>
   EOF
   python3 /tmp/ai-ders/araclar/anlatim_testi.py /tmp/anlatim/<konu>/NN.md
   ```
   Konunun ilk mesajında `--ilk`, idari mesajda `--idari` ekle. Dersin sözlüğü varsa her komuta `--ders <ders-klasörü>` ekle: terim dili de denetlenir (aşağıda). Taslakta `[widget]` satırı yazarsan widget sınırı sayılır (önü ve sonu çift boşluk); gönderirken o satırı sil.
2. HATA çıkarsa düzelt ve yeniden çalıştır (en çok 2 tur). UYARI'ya bak; haklıysa düzelt.
3. Gönderilen metin test edilen metinle aynı olmalı; testten sonra elle değiştirme.
4. Düzelmeyen hata kaldıysa mesajı yine gönder ama sohbete hemen 2 satırlık rapor yaz (aşağıda). Hatayı gizleme.

## Kişisel ayarlar: yerel/denetim.json
Kişiye özel ölçülebilir tercihler (terim dili, emoji, mini test sayısı...) kullanıcının proje klasöründe `yerel/denetim.json` dosyasındadır (şablon: `kurulum/yerel-denetim-sablonu.json`; depoya yazılmaz). Test bu dosyayı kendisi bulur (`--profil` ya da `AI_DERS_PROFIL` ile de verilebilir); komut satırı bayrakları profili geçer. Dosya yoksa yalnız depo kuralları denetlenir. `yerel/ayarlar.md`'de yeni ölçülebilir bir tercih yazılırsa aynı turda profile de yazılır.

## Terim dili (T01–T04)
`--ders <ders>` (ya da `--sozluk dosya`) verilince mesajdaki sözlük terimleri ayar C'ye göre denetlenir; profildeki `terim_dili` ayar kodunu geçer.
- C2: terim İngilizce yazılır, Türkçesi parantezde (`water activity (su aktivitesi)`); `terim_her_gecis` açıksa her geçişte, kapalıysa Türkçe çıplak yazım yine hatadır. Başlık, tablo ve widget metni dahil.
- C1/C3: Türkçe önce, İngilizcesi parantezde; ters sıra hatadır.
- Sözlük: `dersler/<ders>/sozluk.md` ve projedeki `dersler/<ders>/sozluk/sozluk.json` (alan terimleri). Sözlükte olmayan terim denetlenmez; yeni terimi sözlüğe ekle (ayar C3).

## Emoji (E01–E03)
Kişisel işaret emojisi (ör. sınav ihtimali) profilde `emoji` ve `emoji_seri` ile tanımlıdır: emoji yalnız o uzunlukta seri olarak yazılır (`3-4` ise 🙉🙉🙉 ya da 🙉🙉🙉🙉; tek ya da çift yok), widget'ın içine konmaz. `--emoji-adet` ayrı bir şeydir: konu başına toplam emoji sınırı; yalnız kullanıcı toplam adet isterse kullanılır.

## Widget ve test dosyaları (W01–W07, Q01–Q15)
Widget'ı yayınlamadan önce taslağı `.html` olarak yaz ve aynı testi çalıştır (`--test-turu mini` ya da `tam`, soruda geçmemesi gereken adım adını `--konu "<adım adı>"` ile ver):
```
python3 /tmp/ai-ders/araclar/anlatim_testi.py /tmp/anlatim/<konu>/NN-widget.html --test-turu mini --konu "<adım adı>"
```
- W: `<button>`, `ResizeObserver`, `setInterval`, dış kütüphane yok; yazı ≥ 13 px; sabit hex yok (gorsel/stil.md).
- Q: W10 (`var Q=[[soru, [şıklar], doğru, açıklama, ipucu, konu]...]`), W24 widget'ı ve W24 JSON'u okunur. Soru ve şıklar profildeki `test_dil` `en-tr` ise İngilizce yazılır, Türkçesi parantezde olur; soruda ve şıklarda sayfa/slayt/adım numarası ve (verilmişse) adım adı geçmez; mini test `mini_test_soru` kadar soru; doğru cevap hep aynı şıkta olmaz; aynı şık/soru tekrar etmez; açıklama boş değildir.
- Karışık sorular (profilde `karisik_test`): her soruya görünmez konu etiketi yaz (W10'da sorunun 6. elemanı, ipucu yoksa `''`; W24 JSON'da `bolum`). Mini testin soruları tek konudan olamaz ve hepsi güncel konudan olamaz; tam testte art arda iki soru aynı konudan olmaz.

## Konu sonunda rapor
Konunun bütün taslaklarını tek dizinde topla ve dizini çalıştır: çift boşluk payı (hedef ~%40, en az 10 geçişte %20–%70 dışı hata), toplam hata ve uyarı bu çalıştırmadan çıkar.
```
python3 /tmp/ai-ders/araclar/anlatim_testi.py /tmp/anlatim/<konu> --rapor
```
Çıktı 2 satırdır; sohbete olduğu gibi yaz (idari mesaj kuralı, en çok 2 satır). Hata 0 ise yine yaz ("0 hata"), kullanıcı kuralın uygulandığını görsün.
Emoji serisi her mesajda denetlenir (yukarıda); konu başına toplam emoji sınırı ayrıca istenmişse son çalıştırmaya `--emoji <emoji> --emoji-adet <alt>-<üst>` ekle.

## Gönderdikten sonra
Formül ham kod görünüyorsa mesajı düzelt (claude-sorunlari/formuller.md kural 7) ve testin kaçırdığı kalıbı kural dosyasına ve teste ekle (aşağıda).

## Yeni kural ya da yeni formül sorunu çıkınca
Kural `cekirdek/temel.md` ya da `claude-sorunlari/`na yazılır (gorevler/kural-guncelle.md). Kod ile denetlenebiliyorsa `araclar/anlatim_testi.py`'ye kontrol ve `--kendini-dene` listesine bir yanlış, bir doğru örnek eklenir; `python3 araclar/anlatim_testi.py --kendini-dene` geçmeden depoya girmez.
