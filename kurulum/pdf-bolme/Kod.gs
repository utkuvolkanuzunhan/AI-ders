/**
 * AI-ders — PDF konu bölücü (Google Apps Script)
 *
 * 1) haritala: kök klasör altındaki (tüm dönemler) 12+ sayfalık her PDF'i sayfa sayfa
 *    Google Dokümanına çevirip okur (taranmış PDF'lerde de çalışır, Drive OCR kullanır) ve
 *    _sistem/harita klasörüne "<dosyaId>__<ad> (metin)" dokümanını yazar; her sayfanın
 *    başında "[[SAYFA n]]" var. Uzun PDF'ler birkaç turda biter; o sırada adı "YARIM " ile başlar.
 *    Claude bu dokümanı okuyup konu → sayfa aralığı planını _sistem/planlar'a
 *    plan_<dosyaId>.tsv olarak yazar.
 * 2) bol: her planı okuyup PDF'in yanına "<ad> (konular)" klasörü açar, her konuyu
 *    ayrı PDF yapar (adında sayfa aralığı var) ve "00 İçindekiler" dokümanı ekler.
 *
 * Kurulum: bu kodu yapıştır, üstten "kur" fonksiyonunu seçip ▶ Çalıştır, izin ver.
 * Sonrası otomatik: her 10 dakikada bir kendisi çalışır.
 */

const KOK_ID = 'BURAYA_KOK_KLASOR_ID';   // Drive'daki ana ders klasörünün id'si (adres çubuğunda folders/ sonrası)
const MIN_SAYFA = 12;          // bundan kısa PDF'ler bölünmez
const SURE_SINIRI_MS = 4.5 * 60 * 1000;
const PDF_LIB_URL = 'https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/dist/pdf-lib.min.js';
const ISARET_METIN = '[bolme:metin]';
const ISARET_KUCUK = '[bolme:kucuk]';
const ISARET_BOLUNDU = '[bolme:bolundu]';
const BITMIS_ISARETLER = [ISARET_METIN, ISARET_KUCUK, ISARET_BOLUNDU, '[bolme:okunamadi]'];

var baslangic_ = Date.now();

async function kur() {
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('calistir').timeBased().everyMinutes(10).create();
  sistemKlasoru_('harita'); sistemKlasoru_('planlar'); sistemKlasoru_('islendi');
  await calistir();
}

async function calistir() {
  const kilit = LockService.getScriptLock();
  if (!kilit.tryLock(1000)) return;   // önceki tur hâlâ çalışıyor
  try {
    baslangic_ = Date.now();
    await bol();
    await haritala();
  } finally {
    kilit.releaseLock();
  }
}

/* ---------- 1. adım: sayfa sayfa metin ---------- */

async function haritala() {
  const harita = sistemKlasoru_('harita');
  const pdfler = [];
  pdfleriTopla_(DriveApp.getFolderById(KOK_ID), pdfler, 0);
  for (const dosya of pdfler) {
    if (zamanDoldu_()) return;
    const acik = dosya.getDescription() || '';
    if (BITMIS_ISARETLER.some(function (x) { return acik.indexOf(x) !== -1; })) continue;
    const L = pdfLib_();
    let src;
    try {
      src = await L.PDFDocument.load(baytlar_(dosya.getBlob()), { ignoreEncryption: true });
    } catch (e) {
      dosya.setDescription(acik + ' [bolme:okunamadi]');
      continue;
    }
    const toplam = src.getPageCount();
    if (toplam < MIN_SAYFA) { dosya.setDescription(acik + ' ' + ISARET_KUCUK); continue; }

    const temel = dosya.getId() + '__' + dosya.getName().replace(/\.pdf$/i, '') + ' (metin)';
    let metin = dosyaBul_(harita, 'YARIM ' + temel);
    if (!metin) {
      const d = DocumentApp.create('YARIM ' + temel);
      d.getBody().appendParagraph(dosya.getName() + ' — ' + toplam + ' sayfa');
      d.saveAndClose();
      metin = DriveApp.getFileById(d.getId());
      metin.moveTo(harita);
    }
    const doc = DocumentApp.openById(metin.getId());
    const govde = doc.getBody();
    const sayfalar = govde.getText().match(/\[\[SAYFA \d+\]\]/g) || [];
    let n = sayfalar.length + 1;
    while (n <= toplam && !zamanDoldu_()) {
      const tek = await L.PDFDocument.create();
      tek.addPage((await tek.copyPages(src, [n - 1]))[0]);
      const yazi = sayfaMetni_(await tek.save(), harita.getId()) || '(boş sayfa)';
      govde.appendParagraph('[[SAYFA ' + n + ']]');
      govde.appendParagraph(yazi);
      n++;
    }
    doc.saveAndClose();
    if (n > toplam) {
      metin.setName(temel);
      dosya.setDescription(acik + ' ' + ISARET_METIN);
    }
  }
}

/** Tek sayfalık PDF'i Drive'a Google Dokümanı olarak yükler (Drive OCR yapar), metnini alır, geçici dokümanı siler. */
function sayfaMetni_(u8, klasorId) {
  const sinir = 'gidamuh' + Date.now();
  const meta = JSON.stringify({ name: '_gecici_ocr', mimeType: 'application/vnd.google-apps.document', parents: [klasorId] });
  const bas = Utilities.newBlob('--' + sinir + '\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n' + meta +
    '\r\n--' + sinir + '\r\nContent-Type: application/pdf\r\n\r\n').getBytes();
  const son = Utilities.newBlob('\r\n--' + sinir + '--').getBytes();
  const govde = bas.concat(Array.from(new Int8Array(u8.buffer, u8.byteOffset, u8.length)), son);
  const yetki = { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() };
  const cevap = UrlFetchApp.fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart', {
    method: 'post', contentType: 'multipart/related; boundary=' + sinir, payload: govde, headers: yetki, muteHttpExceptions: true
  });
  if (cevap.getResponseCode() >= 300) return '(okunamadı: ' + cevap.getResponseCode() + ')';
  const id = JSON.parse(cevap.getContentText()).id;
  const yazi = DocumentApp.openById(id).getBody().getText().trim();
  UrlFetchApp.fetch('https://www.googleapis.com/drive/v3/files/' + id, { method: 'delete', headers: yetki, muteHttpExceptions: true });
  return yazi;
}

function pdfleriTopla_(klasor, liste, derinlik) {
  const ad = klasor.getName();
  if (derinlik > 4 || ad === '_sistem' || / \(konular\)$/.test(ad)) return;
  const dosyalar = klasor.getFilesByType(MimeType.PDF);
  while (dosyalar.hasNext()) liste.push(dosyalar.next());
  const alt = klasor.getFolders();
  while (alt.hasNext()) pdfleriTopla_(alt.next(), liste, derinlik + 1);
}

/* ---------- 2. adım: plana göre bölme ---------- */

async function bol() {
  const planlar = sistemKlasoru_('planlar');
  const islendi = sistemKlasoru_('islendi');
  const it = planlar.getFiles();
  while (it.hasNext()) {
    if (zamanDoldu_()) return;
    const plan = it.next();
    const m = plan.getName().match(/^plan_(.+)\.tsv$/);
    if (!m) continue;
    const kaynak = DriveApp.getFileById(m[1]);
    const satirlar = planOku_(plan.getBlob().getDataAsString('UTF-8'));
    const L = pdfLib_();
    const src = await L.PDFDocument.load(baytlar_(kaynak.getBlob()), { ignoreEncryption: true });
    const toplam = src.getPageCount();

    const ust = kaynak.getParents().next();
    const temelAd = kaynak.getName().replace(/\.pdf$/i, '');
    const hedef = klasorBulVeyaAc_(ust, temelAd + ' (konular)');
    const uretilen = [];

    for (const s of satirlar) {
      const a = Math.max(1, s.bas), b = Math.min(toplam, s.bit);
      if (a > b) continue;
      const ad = s.sira + '_' + dosyaAdi_(s.konu) + '_s' + a + '-' + b + '.pdf';
      let f = dosyaBul_(hedef, ad);
      if (!f) {
        const yeni = await L.PDFDocument.create();
        const idx = [];
        for (let i = a - 1; i < b; i++) idx.push(i);
        (await yeni.copyPages(src, idx)).forEach(function (p) { yeni.addPage(p); });
        f = hedef.createFile(blob_(await yeni.save(), ad));
      }
      uretilen.push({ sira: s.sira, konu: s.konu, a: a, b: b, url: f.getUrl() });
    }

    icindekiler_(hedef, kaynak, uretilen, toplam);
    kaynak.setDescription((kaynak.getDescription() || '') + ' ' + ISARET_BOLUNDU);
    plan.moveTo(islendi);
    const eskiler = sistemKlasoru_('harita').getFiles();
    while (eskiler.hasNext()) {
      const f = eskiler.next();
      if (f.getName().indexOf(kaynak.getId() + '__') !== -1) f.setTrashed(true);
    }
  }
}

function planOku_(metin) {
  return metin.split(/\r?\n/).slice(1).filter(function (x) { return x.trim(); }).map(function (x) {
    const c = x.split('\t');
    return { sira: String(c[0]).padStart(2, '0'), konu: c[1], bas: parseInt(c[2], 10), bit: parseInt(c[3], 10) };
  });
}

function icindekiler_(klasor, kaynak, liste, toplam) {
  const eski = klasor.getFilesByName('00 İçindekiler');
  while (eski.hasNext()) eski.next().setTrashed(true);
  const doc = DocumentApp.create('00 İçindekiler');
  const g = doc.getBody();
  g.appendParagraph(kaynak.getName()).setHeading(DocumentApp.ParagraphHeading.HEADING1);
  g.appendParagraph('Toplam ' + toplam + ' sayfa. Asıl dosya: ').appendText(kaynak.getName()).setLinkUrl(kaynak.getUrl());
  liste.forEach(function (k) {
    const p = g.appendParagraph(k.sira + '  ' + k.konu + '  —  s. ' + k.a + '–' + k.b);
    p.editAsText().setLinkUrl(k.url);
  });
  doc.saveAndClose();
  DriveApp.getFileById(doc.getId()).moveTo(klasor);
}

/* ---------- yardımcılar ---------- */

function pdfLib_() {
  if (typeof PDFLib === 'undefined') {
    globalThis.self = globalThis;
    // pdf-lib setTimeout ister; Apps Script'te yok. Burada tanımlanır ki fonksiyon listesinde görünmesin.
    globalThis.setTimeout = function (f, t) {
      if (typeof f !== 'function') return 0;
      if (t) Utilities.sleep(Math.min(t, 1000));
      f.apply(null, Array.prototype.slice.call(arguments, 2));
      return 0;
    };
    globalThis.clearTimeout = function () {};
    (0, eval)(UrlFetchApp.fetch(PDF_LIB_URL).getContentText());
  }
  return PDFLib;
}

function baytlar_(blob) { return new Uint8Array(blob.getBytes()); }

function blob_(u8, ad) {
  return Utilities.newBlob(Array.from(new Int8Array(u8.buffer, u8.byteOffset, u8.length)), MimeType.PDF, ad);
}

function sistemKlasoru_(ad) {
  const kok = DriveApp.getFolderById(KOK_ID);
  const sistem = klasorBulVeyaAc_(kok, '_sistem');
  return klasorBulVeyaAc_(sistem, ad);
}

function klasorBulVeyaAc_(ust, ad) {
  const it = ust.getFoldersByName(ad);
  return it.hasNext() ? it.next() : ust.createFolder(ad);
}

function dosyaBul_(klasor, ad) {
  const it = klasor.getFilesByName(ad);
  return it.hasNext() ? it.next() : null;
}

function dosyaAdi_(s) {
  return String(s).trim().replace(/[\\\/:*?"<>|]/g, '').replace(/\s+/g, '-').slice(0, 60);
}

function zamanDoldu_() { return Date.now() - baslangic_ > SURE_SINIRI_MS; }
