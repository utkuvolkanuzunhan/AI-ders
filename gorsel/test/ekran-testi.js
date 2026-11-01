// Kullanım: node ekran-testi.js <widget.html> <genişlik> <yükseklik> <çıktı.png> [koyu|acik] [tikla-secici]
// Örnek: node ekran-testi.js W01.html 390 800 w01-dikey.png koyu ".t"
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [f,W,H,out,tema='koyu',tik]=process.argv.slice(2);
const T=tema==='acik'?'#ffffff;--text-primary:#1f2328;--text-secondary:#5d6670;--surface-1:#f1f3f5;--border:#d7dce1':'#17212c;--text-primary:#e6ecf2;--text-secondary:#9aa8b6;--surface-1:#202d3a;--border:#2a3745';
const b=await chromium.launch();const p=await b.newPage({viewport:{width:+W,height:+H},isMobile:true,hasTouch:true});
const w=fs.readFileSync(f,'utf8').replace(/<!--[\s\S]*?-->/,'');
await p.setContent('<meta name=viewport content="width=device-width,initial-scale=1"><body style="margin:0;background:'+T+';font-family:system-ui;font-size:16px;padding:8px">'+w+'</body>');
await p.waitForTimeout(300);
if(tik){const el=await p.$(tik);if(el){await el.click();await p.waitForTimeout(300)}}
await p.screenshot({path:out,fullPage:true});await b.close()})()
