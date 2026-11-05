// Widget ekran testi (araclar/widget.py --test ya da doğrudan): node araclar/widget_test.js widget.html [--goruntu klasor] [--yalniz-goruntu]
// 390 ve 900 px, açık ve koyu ana bilgisayar teması, her sekme, her çip/kaydırıcı, sınıflamada ve testte doğru ve yanlış cevap durumları.
// Rapor: JS hatası, 13 px altı yazı, 44 px altı dokunma hedefi, yatay taşma. Çıkış kodu 1 = sorun var, 2 = çalışmadı.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const gi = args.indexOf('--goruntu');
const dosya = args.find((a, i) => !a.startsWith('--') && !(gi >= 0 && i === gi + 1));
const goruntuKlasor = gi >= 0 ? args[gi + 1] : null;
const yalnizGoruntu = args.includes('--yalniz-goruntu');
if (!dosya) { console.error('kullanım: node widget_test.js widget.html [--goruntu klasor]'); process.exit(2); }
const parca = fs.readFileSync(dosya, 'utf8');

function sayfa(koyu) {
  const v = koyu
    ? '--text-primary:#ececec;--text-secondary:#b4b2a7;--text-muted:#8a887f;--surface-1:#30302e;--border:rgba(255,255,255,.15);'
    : '--text-primary:#1f1e1d;--text-secondary:#5d5c57;--text-muted:#8a887f;--surface-1:#ffffff;--border:rgba(0,0,0,.15);';
  const bg = koyu ? '#262624' : '#faf9f5';
  return '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>:root{' + v +
    '}html,body{margin:0;background:' + bg + ';font-family:system-ui,sans-serif}body{padding:12px 6px}</style></head><body>' + parca + '</body></html>';
}

// sayfa içinde çalışır: sorunları toplar
function olc() {
  const R = document.querySelector('.nb');
  const gorunur = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const ad = e => (e.tagName.toLowerCase() + (e.className && e.className.baseVal === undefined ? '.' + String(e.className).trim().split(/\s+/).join('.') : '')) + ' "' + (e.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 24) + '"';
  const out = { yazi: [], hedef: [], tasma: [] };
  const w = document.createTreeWalker(R, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    if (!n.nodeValue.trim()) continue;
    const e = n.parentElement;
    if (!e || ['STYLE', 'SCRIPT'].includes(e.tagName) || !gorunur(e)) continue;
    const fs_ = parseFloat(getComputedStyle(e).fontSize);
    if (fs_ < 13) out.yazi.push(fs_ + ' px: ' + ad(e));
  }
  R.querySelectorAll('[role=button]').forEach(e => {
    if (!gorunur(e)) return;
    const r = e.getBoundingClientRect();
    if (Math.min(r.width, r.height) < 44) out.hedef.push(Math.round(r.width) + 'x' + Math.round(r.height) + ': ' + ad(e));
  });
  const kok = R.getBoundingClientRect();
  if (document.documentElement.scrollWidth > window.innerWidth + 1) out.tasma.push('sayfa yatay kayıyor: ' + document.documentElement.scrollWidth + ' > ' + window.innerWidth);
  R.querySelectorAll('*').forEach(e => {
    if (!gorunur(e) || e.closest('.tw')) return;
    const r = e.getBoundingClientRect();
    if (r.right > kok.right + 1) out.tasma.push('kökün dışına taşıyor ' + Math.round(r.right - kok.right) + ' px: ' + ad(e));
  });
  return out;
}

(async () => {
  const b = await chromium.launch();
  const hata = { js: new Set(), yazi: new Set(), hedef: new Set(), tasma: new Set() };
  let durum = 0;
  if (goruntuKlasor) fs.mkdirSync(goruntuKlasor, { recursive: true });
  for (const koyu of [false, true]) {
    for (const vw of [390, 900]) {
      const ctx = await b.newContext({ viewport: { width: vw, height: 900 }, deviceScaleFactor: 1 });
      const p = await ctx.newPage();
      const etiket = (vw) + (koyu ? 'k' : 'a');
      p.on('pageerror', e => hata.js.add(etiket + ' ' + e.message));
      p.on('console', m => { if (m.type() === 'error') hata.js.add(etiket + ' console: ' + m.text()); });
      await p.setContent(sayfa(koyu));
      const adim = async (ad) => {
        durum++;
        if (goruntuKlasor) await p.screenshot({ path: path.join(goruntuKlasor, `${etiket}_${String(durum).padStart(3, '0')}_${ad}.png`), fullPage: true });
        if (yalnizGoruntu) return;
        const o = await p.evaluate(olc);
        o.yazi.forEach(x => hata.yazi.add(x)); o.hedef.forEach(x => hata.hedef.add(`${etiket} ${x}`)); o.tasma.forEach(x => hata.tasma.add(`${etiket} ${x}`));
      };
      await adim('acilis');
      const sekmeSayisi = await p.locator('.tb').count();
      for (let i = 0; i < sekmeSayisi; i++) {
        await p.locator('.tb').nth(i).click();
        await adim(`sekme${i + 1}`);
        const panel = p.locator('.pn').nth(i);
        // çipler (seçici, kart, ön ayar): hepsine sırayla bas
        const cipler = panel.locator('[data-act=sc],[data-act=rv],[data-act=pg],[data-act=q],[data-act=pre]');
        const nc = await cipler.count();
        for (let k = 0; k < nc; k++) { await cipler.nth(k).click(); await adim(`sekme${i + 1}_cip${k + 1}`); }
        // kaydırıcı: uçlar ve orta
        const kay = panel.locator('input.sl');
        for (let k = 0; k < await kay.count(); k++) {
          for (const v of [0, 50, 100]) {
            await kay.nth(k).evaluate((el, val) => { el.value = val; el.dispatchEvent(new Event('input', { bubbles: true })); }, v);
            await adim(`sekme${i + 1}_kay${k + 1}_${v}`);
          }
        }
        // sınıflama: ilk karttan başlayarak seçenekleri döndür (bir kısmı doğru bir kısmı yanlış olur)
        const kartlar = panel.locator('.it');
        for (let k = 0; k < await kartlar.count(); k++) {
          const sec = kartlar.nth(k).locator('[data-act=srt]');
          await sec.nth(k % (await sec.count())).click();
          await adim(`sekme${i + 1}_sinif${k + 1}`);
        }
        // test: ipucu, sonra bir soruda ilk şık, diğerinde son şık
        const sorular = panel.locator('.q');
        for (let k = 0; k < await sorular.count(); k++) {
          const ip = sorular.nth(k).locator('.hn');
          if (await ip.count() && await ip.first().isVisible()) { await ip.first().click(); await adim(`sekme${i + 1}_ipucu${k + 1}`); }
          const o = sorular.nth(k).locator('.o');
          await o.nth(k % 2 === 0 ? 0 : (await o.count()) - 1).click();
          await adim(`sekme${i + 1}_soru${k + 1}`);
        }
      }
      await ctx.close();
    }
  }
  await b.close();
  if (yalnizGoruntu) { console.log(`${durum} durum görüntülendi`); return; }
  const bol = (ad, set) => { if (set.size) { console.log(`HATA · ${ad} (${set.size}):`); [...set].slice(0, 12).forEach(x => console.log('  ' + x)); if (set.size > 12) console.log(`  ... +${set.size - 12}`); } };
  bol('JS hatası', hata.js); bol('13 px altı yazı', hata.yazi); bol('44 px altı dokunma hedefi', hata.hedef); bol('yatay taşma', hata.tasma);
  const toplam = hata.js.size + hata.yazi.size + hata.hedef.size + hata.tasma.size;
  console.log(toplam ? `SONUÇ: ${toplam} sorun (${durum} durum denendi)` : `SONUÇ: GEÇTİ (${durum} durum: 390/900 px, açık/koyu, her sekme, doğru ve yanlış cevaplar)`);
  process.exit(toplam ? 1 : 0);
})().catch(e => { console.error(String(e)); process.exit(2); });
