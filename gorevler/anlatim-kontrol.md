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
   Konunun ilk mesajında `--ilk`, idari mesajda `--idari` ekle. Taslakta `[widget]` satırı yazarsan widget sınırı sayılır (önü ve sonu çift boşluk); gönderirken o satırı sil.
2. HATA çıkarsa düzelt ve yeniden çalıştır (en çok 2 tur). UYARI'ya bak; haklıysa düzelt.
3. Gönderilen metin test edilen metinle aynı olmalı; testten sonra elle değiştirme.
4. Düzelmeyen hata kaldıysa mesajı yine gönder ama sohbete hemen 2 satırlık rapor yaz (aşağıda). Hatayı gizleme.

## Konu sonunda rapor
Konunun bütün taslaklarını tek dizinde topla ve dizini çalıştır: çift boşluk payı (hedef ~%40, en az 10 geçişte %20–%70 dışı hata), toplam hata ve uyarı bu çalıştırmadan çıkar.
```
python3 /tmp/ai-ders/araclar/anlatim_testi.py /tmp/anlatim/<konu> --rapor
```
Çıktı 2 satırdır; sohbete olduğu gibi yaz (idari mesaj kuralı, en çok 2 satır). Hata 0 ise yine yaz ("0 hata"), kullanıcı kuralın uygulandığını görsün.
Kişisel emoji ayarı varsa (`yerel/ayarlar.md`, ör. sınav ihtimali emojisi) bu son çalıştırmaya `--emoji <emoji> --emoji-adet <alt>-<üst>` ekle (örnek `3-4`): emoji sayısı konu başına toplam sayılır, tek mesajda sayılmaz.

## Gönderdikten sonra
Formül ham kod görünüyorsa mesajı düzelt (claude-sorunlari/formuller.md kural 7) ve testin kaçırdığı kalıbı kural dosyasına ve teste ekle (aşağıda).

## Yeni kural ya da yeni formül sorunu çıkınca
Kural `cekirdek/temel.md` ya da `claude-sorunlari/`na yazılır (gorevler/kural-guncelle.md). Kod ile denetlenebiliyorsa `araclar/anlatim_testi.py`'ye kontrol ve `--kendini-dene` listesine bir yanlış, bir doğru örnek eklenir; `python3 araclar/anlatim_testi.py --kendini-dene` geçmeden depoya girmez.
