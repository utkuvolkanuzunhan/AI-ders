#!/usr/bin/env python3
"""Süreli kota istisnaları: "Gemini 3 saat yok", "Claude %20 kaldı, 3 gün dayanmalı" gibi anlık durumlar.

Yazım tarifi: mimari/is-tarifleri/kota.md
Sözleşme    : mimari/02-sozlesmeler.md ("Kota istisnası")

İstisna dosyası `<VOLKAN_KASA>/90-Sistem/Kota/istisna.json` (ya da `VOLKAN_KOTA_DOSYA`). Her kaydın bitişi vardır;
bitişi geçmiş kayıt hiçbir okuyucuda etkili değildir, yani süre bitince sistem kendiliğinden temele döner.
Kademeler, takma adlar ve dönem uzunlukları koda yazılmaz: `harita.json` içindeki `kota_kademeleri` bölümünden okunur.

Kullanım:
  python araclar/kota.py kapat <havuz|takma ad> --sure 3s [--neden METIN]
  python araclar/kota.py kis   <havuz|takma ad> (--kalan 20 --gun 3 | --kademe orta) [--sure 3g]
  python araclar/kota.py kaldir <kimlik|havuz|takma ad|hepsi>
  python araclar/kota.py durum [--json]     # etkin istisnalar ve kalan süre
  python araclar/kota.py ozet               # oturum başı için tek satır (etkin istisna yoksa hiçbir şey basmaz)
  python araclar/kota.py kanca              # Claude Code PreToolUse kancası (T3 görev açan araçlar)
  python araclar/kota.py denetle            # tavan kuralı: resmi API sınırın tamamı, ban riskli web %80 (1 = ihlal)

Süre biçimi: 45dk, 3s / 3saat / 3h, 2g / 2gun / 2d. `--bitis 2026-11-20T09:00+03:00` de verilebilir.
Çıkış kodu: 0 tamam, 2 hatalı girdi. `kanca` ve `ozet` her zaman 0 ile çıkar.
Yalnızca standart kitaplık. Model çağırmaz.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import secrets
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HARITA_YOLU = KOK / "harita.json"
SURUM = 1
DOSYA_DEGISKENI = "VOLKAN_KOTA_DOSYA"
HAVUZ_YAPILANDIRMASI = "havuz/litellm.yaml"  # varsa `denetle` bunu da ölçer (is/havuz dalı)
_SURE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*(dk|dakika|m|min|s|sa|saat|h|g|gun|gün|d)\s*$", re.IGNORECASE)
_BIRIM = {"dk": 60, "dakika": 60, "m": 60, "min": 60, "s": 3600, "sa": 3600, "saat": 3600, "h": 3600,
          "g": 86400, "gun": 86400, "gün": 86400, "d": 86400}
MODEL_ALANLARI = ("model", "modelId", "model_id", "modelName")


class KotaHatasi(Exception):
    """Kullanıcıya gösterilecek girdi hatası."""


# --- Zaman ---------------------------------------------------------------------

def simdi_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _zaman_oku(metin) -> dt.datetime | None:
    if not isinstance(metin, str):
        return None
    try:
        z = dt.datetime.fromisoformat(metin.replace("Z", "+00:00"))
    except ValueError:
        return None
    return z if z.tzinfo else z.replace(tzinfo=dt.timezone.utc)


def _zaman_yaz(z: dt.datetime) -> str:
    return z.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sure_coz(metin: str) -> dt.timedelta:
    m = _SURE.match(metin or "")
    if not m:
        raise KotaHatasi(f"Süre anlaşılmadı: '{metin}'. Örnek: 45dk, 3s, 2g")
    deger = float(m.group(1).replace(",", "."))
    if deger <= 0:
        raise KotaHatasi("Süre sıfırdan büyük olmalı.")
    return dt.timedelta(seconds=deger * _BIRIM[m.group(2).lower()])


def kalan_metni(bitis: dt.datetime, simdi: dt.datetime) -> str:
    saniye = max(0, int((bitis - simdi).total_seconds()))
    gun, saniye = divmod(saniye, 86400)
    saat, saniye = divmod(saniye, 3600)
    dakika = saniye // 60
    parca = ([f"{gun} gün"] if gun else []) + ([f"{saat} saat"] if saat else []) + ([f"{dakika} dk"] if dakika and not gun else [])
    return " ".join(parca) or "1 dk'dan az"


# --- Harita ----------------------------------------------------------------------

def harita_yukle(yol: Path = HARITA_YOLU) -> dict:
    return json.loads(Path(yol).read_text(encoding="utf-8"))


def ayar(harita: dict) -> dict:
    return harita.get("kota_kademeleri") or {}


def havuzlar(harita: dict) -> list[str]:
    """Ajanların kota havuzları ve istek sınırı yazılı hizmetler (web-chatgpt gibi; onları okuyan betik kapalıysa atlar)."""
    ajan = {a["kota_havuzu"] for a in harita.get("ajanlar", {}).values() if a.get("kota_havuzu")}
    hizmet = {ad for ad, k in (harita.get("istek_sinirlari") or {}).items() if isinstance(k, dict) and "resmi" in k}
    return sorted(ajan | hizmet)


def havuz_coz(harita: dict, ad: str) -> list[str]:
    """Havuz adı ya da takma ad (claude, gemini ...) -> havuz listesi. Bilinmezse KotaHatasi."""
    bilinen = havuzlar(harita)
    if ad in bilinen:
        return [ad]
    takma = {k.lower(): v for k, v in (ayar(harita).get("takma_adlar") or {}).items()}
    if ad.lower() in takma:
        return [h for h in takma[ad.lower()] if h in bilinen]
    raise KotaHatasi(f"Bilinmeyen havuz '{ad}'. Havuzlar: {', '.join(bilinen)}; takma adlar: {', '.join(sorted(takma))}")


def kademe_bul(harita: dict, ad: str) -> dict:
    for k in ayar(harita).get("kademeler") or []:
        if k.get("ad") == ad:
            return k
    adlar = [k.get("ad") for k in ayar(harita).get("kademeler") or []]
    raise KotaHatasi(f"Bilinmeyen kademe '{ad}'. Kademeler: {', '.join(map(str, adlar))}")


def kademe_hesapla(harita: dict, havuz: str, kalan_yuzde: float, gun: float) -> tuple[dict | None, float]:
    """Kalan payı ve dayanılacak günü normal harcama hızıyla karşılaştırır.

    oran = (kalan / 100) / (gun / dönem). 1 ve üstü: kısıt gerekmez (None). Altında: eşiği orandan büyük olan en sıkı kademe.
    """
    if not 0 <= kalan_yuzde <= 100:
        raise KotaHatasi("Kalan yüzde 0 ile 100 arasında olmalı.")
    if gun <= 0:
        raise KotaHatasi("Gün sayısı sıfırdan büyük olmalı.")
    a = ayar(harita)
    donem = float((a.get("donem_gun") or {}).get(havuz, a.get("varsayilan_donem_gun", 7)))
    oran = (kalan_yuzde / 100.0) / (gun / donem)
    secilen = None
    for k in sorted(a.get("kademeler") or [], key=lambda x: x["oran_alti"], reverse=True):
        if oran < k["oran_alti"]:
            secilen = k
    return secilen, oran


# --- Dosya -----------------------------------------------------------------------

def dosya_yolu(kasa: str | os.PathLike | None = None) -> Path | None:
    elle = os.environ.get(DOSYA_DEGISKENI)
    if elle:
        return Path(elle)
    kasa = kasa if kasa is not None else os.environ.get("VOLKAN_KASA")
    return Path(kasa) / "90-Sistem" / "Kota" / "istisna.json" if kasa else None


def oku(yol: Path | None) -> list[dict]:
    """Bütün kayıtlar (süresi geçmişler dahil). Dosya yoksa ya da bozuksa boş liste: bozuk dosya hiçbir şeyi kısmaz."""
    if yol is None:
        return []
    try:
        veri = json.loads(Path(yol).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    kayitlar = veri.get("istisnalar") if isinstance(veri, dict) else None
    return [k for k in kayitlar if isinstance(k, dict)] if isinstance(kayitlar, list) else []


def yaz(yol: Path, kayitlar: list[dict], simdi: dt.datetime) -> None:
    yol.parent.mkdir(parents=True, exist_ok=True)
    veri = {"surum": SURUM, "guncellendi": _zaman_yaz(simdi), "istisnalar": kayitlar}
    gecici = yol.with_name(yol.name + ".tmp")
    gecici.write_text(json.dumps(veri, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(gecici, yol)


def etkin(kayitlar: list[dict], simdi: dt.datetime | None = None) -> list[dict]:
    """Başlamış ve bitmemiş kayıtlar. Bitişi okunamayan kayıt etkin sayılmaz."""
    simdi = simdi or simdi_utc()
    sonuc = []
    for k in kayitlar:
        bitis, baslangic = _zaman_oku(k.get("bitis")), _zaman_oku(k.get("baslangic"))
        if bitis is None or bitis <= simdi or (baslangic and baslangic > simdi):
            continue
        sonuc.append(k)
    return sonuc


# --- Okuyuculara verilen kısıt -------------------------------------------------------

def kisitlar(harita: dict, kayitlar: list[dict], simdi: dt.datetime | None = None) -> dict:
    """{"kapali": [havuz], "havuz": {havuz: {"kademe", "sinif_tavani", "efor_tavani", "geri_cek", "bitis"}}}.

    Aynı havuzda birden çok kayıt varsa en sıkısı geçerlidir (kapalı > küçük sınıf tavanı > küçük efor tavanı)."""
    eforlar = harita.get("eforlar") or []
    kapali: set[str] = set()
    kisit: dict[str, dict] = {}
    for k in etkin(kayitlar, simdi):
        for havuz in k.get("havuzlar") or []:
            if k.get("tur") == "kapat":
                kapali.add(havuz)
                continue
            if k.get("tur") != "kis":
                continue
            try:
                kd = kademe_bul(harita, k.get("kademe"))
            except KotaHatasi:
                continue
            yeni = {"kademe": kd["ad"], "sinif_tavani": kd.get("sinif_tavani"), "efor_tavani": kd.get("efor_tavani"),
                    "geri_cek": bool(kd.get("geri_cek")), "bitis": k.get("bitis")}
            eski = kisit.get(havuz)
            if eski is None:
                kisit[havuz] = yeni
                continue
            for alan in ("sinif_tavani",):
                if yeni[alan] is not None and (eski[alan] is None or yeni[alan] < eski[alan]):
                    eski[alan], eski["kademe"] = yeni[alan], yeni["kademe"]
            if yeni["efor_tavani"] in eforlar and (eski["efor_tavani"] not in eforlar
                                                   or eforlar.index(yeni["efor_tavani"]) < eforlar.index(eski["efor_tavani"])):
                eski["efor_tavani"] = yeni["efor_tavani"]
            eski["geri_cek"] = eski["geri_cek"] or yeni["geri_cek"]
            eski["bitis"] = max(eski["bitis"], yeni["bitis"])
    return {"kapali": sorted(kapali), "havuz": {h: v for h, v in kisit.items() if h not in kapali}}


def kasadan_kisitlar(harita: dict, kasa: str | os.PathLike | None = None, simdi: dt.datetime | None = None) -> dict:
    return kisitlar(harita, oku(dosya_yolu(kasa)), simdi)


# --- Yazan komutlar ---------------------------------------------------------------

def _bitis(harita: dict, simdi: dt.datetime, sure: str | None, bitis: str | None, varsayilan: str | None) -> dt.datetime:
    if bitis:
        z = _zaman_oku(bitis)
        if z is None:
            raise KotaHatasi(f"Bitiş zamanı anlaşılmadı: '{bitis}'. Örnek: 2026-11-20T09:00+03:00")
    else:
        if not (sure or varsayilan):
            raise KotaHatasi("--sure ya da --bitis gerekli.")
        z = simdi + sure_coz(sure or varsayilan)
    if z <= simdi:
        raise KotaHatasi("Bitiş şimdiden sonra olmalı.")
    tavan_gun = float(ayar(harita).get("en_uzun_gun", 31))
    if z - simdi > dt.timedelta(days=tavan_gun):
        raise KotaHatasi(f"İstisna en çok {tavan_gun:g} gün sürebilir; daha uzun durum harita.json değişikliğidir.")
    return z


def ekle(harita: dict, yol: Path, tur: str, ad: str, simdi: dt.datetime | None = None, sure: str | None = None,
         bitis: str | None = None, kalan: float | None = None, gun: float | None = None, kademe: str | None = None,
         neden: str | None = None) -> dict:
    """Yeni kaydı ekler, süresi geçmiş kayıtları atar, kaydı döner. Kısıt gerekmiyorsa (oran >= 1) kayıt yazılmaz."""
    simdi = simdi or simdi_utc()
    hedefler = havuz_coz(harita, ad)
    if not hedefler:
        raise KotaHatasi(f"'{ad}' hiçbir havuza karşılık gelmiyor.")
    kayit = {"kimlik": secrets.token_hex(3), "tur": tur, "havuzlar": hedefler, "baslangic": _zaman_yaz(simdi)}
    if tur == "kis":
        if kademe:
            kd, oran = kademe_bul(harita, kademe), None
        elif kalan is not None and gun is not None:
            kd, oran = kademe_hesapla(harita, hedefler[0], kalan, gun)
            if kd is None:
                return {"yazilmadi": True, "oran": round(oran, 2), "havuzlar": hedefler}
            kayit.update({"kalan_yuzde": kalan, "gun": gun, "oran": round(oran, 2)})
        else:
            raise KotaHatasi("kis için --kalan ve --gun ya da --kademe gerekli.")
        kayit["kademe"] = kd["ad"]
        # --sure verilmediyse dayanılacak gün kadar sürer.
        varsayilan = f"{gun}g" if gun else None
        kayit["bitis"] = _zaman_yaz(_bitis(harita, simdi, sure, bitis, varsayilan))
    elif tur == "kapat":
        kayit["bitis"] = _zaman_yaz(_bitis(harita, simdi, sure, bitis, None))
    else:
        raise KotaHatasi(f"Bilinmeyen tür '{tur}'.")
    if neden:
        kayit["neden"] = " ".join(str(neden).split())[:200]
    kayitlar = etkin(oku(yol), simdi) + [kayit]
    yaz(yol, kayitlar, simdi)
    return kayit


def kaldir(harita: dict, yol: Path, hedef: str, simdi: dt.datetime | None = None) -> int:
    """Kimliği, havuzu ya da takma adı eşleşen etkin kayıtları siler. Kaç kayıt silindiğini döner."""
    simdi = simdi or simdi_utc()
    kayitlar = etkin(oku(yol), simdi)
    if hedef == "hepsi":
        kalan: list[dict] = []
    else:
        try:
            hedef_havuzlar = set(havuz_coz(harita, hedef))
        except KotaHatasi:
            hedef_havuzlar = set()
        kalan = [k for k in kayitlar if k.get("kimlik") != hedef and not (hedef_havuzlar & set(k.get("havuzlar") or []))]
    yaz(yol, kalan, simdi)
    return len(kayitlar) - len(kalan)


# --- Okuyan komutlar ---------------------------------------------------------------

def _yerel(z: dt.datetime) -> str:
    return z.astimezone().strftime("%d.%m %H:%M")


def kayit_satiri(harita: dict, k: dict, simdi: dt.datetime) -> str:
    bitis = _zaman_oku(k["bitis"])
    hav = ", ".join(k.get("havuzlar") or [])
    if k.get("tur") == "kapat":
        ne = f"{hav} KAPALI"
    else:
        try:
            kd = kademe_bul(harita, k.get("kademe"))
            ne = (f"{hav} tasarruf ({kd['ad']}): en çok sınıf {kd.get('sinif_tavani')}, efor en çok {kd.get('efor_tavani')}"
                  + (", önce öteki havuz" if kd.get("geri_cek") else ""))
        except KotaHatasi:
            ne = f"{hav} tasarruf (bilinmeyen kademe {k.get('kademe')})"
    return f"[{k.get('kimlik')}] {ne}; {_yerel(bitis)} bitiyor ({kalan_metni(bitis, simdi)} kaldı)" + \
        (f"; neden: {k['neden']}" if k.get("neden") else "")


def ozet_metni(harita: dict, kayitlar: list[dict], simdi: dt.datetime | None = None) -> str:
    simdi = simdi or simdi_utc()
    satirlar = [kayit_satiri(harita, k, simdi) for k in etkin(kayitlar, simdi)]
    if not satirlar:
        return ""
    return "\n".join(["KOTA İSTİSNASI (yon.py bunlara göre seçer; süre bitince kendiliğinden kalkar):"] +
                     [f"  - {s}" for s in satirlar])


# --- Kanca: T3 görev açan araçlar -------------------------------------------------------

def _model_metinleri(dugum, derinlik: int = 0):
    if derinlik > 6:
        return
    if isinstance(dugum, dict):
        for anahtar, deger in dugum.items():
            if anahtar in MODEL_ALANLARI:
                if isinstance(deger, str):
                    yield deger
                elif isinstance(deger, dict):
                    for alt in ("id", "slug", "name", "model"):
                        if isinstance(deger.get(alt), str):
                            yield deger[alt]
            if isinstance(deger, (dict, list)):
                yield from _model_metinleri(deger, derinlik + 1)
    elif isinstance(dugum, list):
        for oge in dugum:
            yield from _model_metinleri(oge, derinlik + 1)


def _sozcukler(metin: str) -> list[str]:
    return [s for s in re.split(r"[^a-z0-9]+", metin.lower()) if s]


def model_tani(harita: dict, metin: str) -> str | None:
    """Serbest model metnini (ör. 'claude-opus-5-5', 'gemini-4-carbon', 'Opus') haritadaki model anahtarına çevirir."""
    sade = metin.strip().lower()
    for anahtar, m in (harita.get("modeller") or {}).items():
        if sade in {anahtar.lower(), str(m.get("ad") or "").lower(), str(m.get("api_adi") or "").lower()}:
            return anahtar
    kelimeler = set(_sozcukler(sade))
    for anahtar in (harita.get("modeller") or {}):
        if anahtar.lower() in kelimeler:
            return anahtar
    return None


def model_havuzlari(harita: dict, model: str) -> set[str]:
    return {a["kota_havuzu"] for a in harita.get("ajanlar", {}).values() if model in (a.get("modeller") or [])}


def kanca_karari(veri: dict, harita: dict, kayitlar: list[dict], simdi: dt.datetime | None = None) -> dict | None:
    """Etkin istisnaya aykırı model seçen görev açma çağrısını reddeder; aykırılık yoksa None."""
    girdi = veri.get("tool_input") if isinstance(veri, dict) else None
    if not isinstance(girdi, (dict, list)):
        return None
    k = kisitlar(harita, kayitlar, simdi)
    if not k["kapali"] and not k["havuz"]:
        return None
    gerekceler = []
    for metin in _model_metinleri(girdi):
        model = model_tani(harita, metin)
        if model is None:
            continue
        sinif = harita["modeller"][model].get("sinif")
        for havuz in sorted(model_havuzlari(harita, model)):
            if havuz in k["kapali"]:
                gerekceler.append(f"'{metin}' modelinin kotası ({havuz}) süreli istisnayla kapalı. Öteki sağlayıcının modelini seç "
                                  "ya da istisna bitene kadar bekle (python araclar/kota.py durum).")
            elif havuz in k["havuz"]:
                tavan = k["havuz"][havuz].get("sinif_tavani")
                if tavan is not None and sinif is not None and sinif > tavan:
                    uygun = [a for a, m in harita["modeller"].items()
                             if havuz in model_havuzlari(harita, a) and (m.get("sinif") or 0) <= tavan]
                    gerekceler.append(f"{havuz} tasarruf kipinde ({k['havuz'][havuz]['kademe']}): en çok sınıf {tavan}. "
                                      f"'{metin}' yerine şunlardan birini seç: {', '.join(uygun) or 'yok'}.")
    if not gerekceler:
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": " ".join(dict.fromkeys(gerekceler))}}


def kanca(girdi: bytes, harita_yolu: Path = HARITA_YOLU, yol: Path | None = None,
          simdi: dt.datetime | None = None) -> dict | None:
    """Kanca çekirdeği. Girdi, harita ya da istisna dosyası okunamazsa izin verilir (None)."""
    try:
        veri = json.loads(girdi.decode("utf-8", errors="replace") or "{}")
        harita = harita_yukle(harita_yolu)
    except (OSError, ValueError):
        return None
    if not isinstance(veri, dict) or not isinstance(harita, dict):
        return None
    return kanca_karari(veri, harita, oku(yol if yol is not None else dosya_yolu()), simdi)


# --- Tavan kuralı: hiçbir tavan resmi istek sınırının türüne göre oranını aşmaz -------------------------
# Türler (Volkan, 2026-11-17): "resmi-api" (ban riski olmayan resmi API) %99, "web" (web arayüzü otomasyonu ya da ban
# riski olan her şey) %80; ilk sözü (%99) aynı gün "risk yoksa max kullanım" diye düzeltildi. Türü yazılmamış kayıt sıkı
# taraftadır: en küçük oran.


def tavan_orani(harita: dict, kayit: dict) -> float:
    oranlar = ayar(harita).get("istek_tavan_oranlari") or {"web": 0.8}
    tur = kayit.get("tur") if isinstance(kayit, dict) else None
    if tur in oranlar:
        return float(oranlar[tur])
    return float(min(oranlar.values()))

_YAML_ALAN = re.compile(r"\b(rpm|rpd|tpm)\s*:\s*(\d+)")


def _havuz_yapilandirmasi(metin: str) -> list[tuple[str, dict[str, int]]]:
    """litellm.yaml satırlarından (model, {rpm, rpd, tpm}) çiftleri. Tam YAML ayrıştırıcısı değildir: tek satırlık
    `litellm_params: { model: ..., rpm: N }` biçimini (iki satıra bölünmüş olsa da) okur."""
    adaylar: list[tuple[str, dict[str, int]]] = []
    for blok in re.split(r"\n\s*-\s*model_name:", metin):
        m = re.search(r"\bmodel:\s*([^\s,}]+)", blok)
        if not m:
            continue
        adaylar.append((m.group(1), {a: int(d) for a, d in _YAML_ALAN.findall(blok)}))
    return adaylar


def denetle(harita: dict, havuz_yaml: str | None = None) -> list[str]:
    """Tavan kuralının ihlalleri (oran kaydın türünden: tavan_orani). Boş liste temizdir.

    - `istek_sinirlari.<hizmet>.resmi.<alan>` olan her hizmette aynı adlı tavan alanı oran x resmi değerini aşmaz.
    - Havuz yapılandırması verilirse: her aday izinli bir sağlayıcının önekiyle başlar; resmi sınırı yazılı alanlar oranı
      aşmaz; `ortak_gunluk` sağlayıcıda günlük tavanların toplamı da oranı aşmaz."""
    sorunlar: list[str] = []
    sinirlar = harita.get("istek_sinirlari") or {}
    for hizmet, kayit in sinirlar.items():
        if not isinstance(kayit, dict):
            continue
        oran = tavan_orani(harita, kayit)
        for alan, resmi in (kayit.get("resmi") or {}).items():
            deger = kayit.get(alan)
            if deger is None:
                sorunlar.append(f"{hizmet}.{alan}: resmi sınır ({resmi}) yazılı ama tavan yok")
            elif deger > oran * resmi:
                sorunlar.append(f"{hizmet}.{alan} = {deger}, resmi sınırın %{oran * 100:g}'i ({oran * resmi:g}) aşılıyor")
    if havuz_yaml is not None:
        api = sinirlar.get("ucretsiz_api") or {}
        saglayicilar = api.get("saglayicilar") or {}
        toplam: dict[str, int] = {}
        for model, alanlar in _havuz_yapilandirmasi(havuz_yaml):
            sahip = next((ad for ad, s in sorted(saglayicilar.items(), key=lambda x: -len(x[1].get("onek", "")))
                          if model.startswith(s.get("onek", "\0"))), None)
            if sahip is None:
                sorunlar.append(f"havuz: '{model}' izinli bir ücretsiz sağlayıcıya ait değil")
                continue
            resmi = saglayicilar[sahip].get("resmi") or {}
            oran = tavan_orani(harita, saglayicilar[sahip])
            for alan, deger in alanlar.items():
                if alan in resmi and deger > oran * resmi[alan]:
                    sorunlar.append(f"havuz: '{model}' {alan} = {deger}, {sahip} resmi sınırının %{oran * 100:g}'i "
                                    f"({oran * resmi[alan]:g}) aşılıyor")
            if saglayicilar[sahip].get("ortak_gunluk") and "rpd" in alanlar:
                toplam[sahip] = toplam.get(sahip, 0) + alanlar["rpd"]
        for sahip, t in toplam.items():
            resmi = (saglayicilar[sahip].get("resmi") or {}).get("rpd")
            oran = tavan_orani(harita, saglayicilar[sahip])
            if resmi and t > oran * resmi:
                sorunlar.append(f"havuz: {sahip} günlük sınırı bütün modellerde ortak; tavanların toplamı {t}, "
                                f"%{oran * 100:g} sınırı {oran * resmi:g}")
    return sorunlar


# --- Komut satırı -------------------------------------------------------------------

def _ayristirici() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Süreli kota istisnaları.")
    alt = p.add_subparsers(dest="komut", required=True)
    k = alt.add_parser("kapat", help="havuzu süreli kapat")
    k.add_argument("havuz")
    k.add_argument("--sure")
    k.add_argument("--bitis")
    k.add_argument("--neden")
    s = alt.add_parser("kis", help="havuzu süreli tasarruf kipine al")
    s.add_argument("havuz")
    s.add_argument("--kalan", type=float, help="kalan pay, yüzde")
    s.add_argument("--gun", type=float, help="bu payın dayanması gereken gün")
    s.add_argument("--kademe", help="kademeyi elle seç (harita.json kota_kademeleri)")
    s.add_argument("--sure")
    s.add_argument("--bitis")
    s.add_argument("--neden")
    r = alt.add_parser("kaldir", help="istisnayı erken kaldır")
    r.add_argument("hedef")
    d = alt.add_parser("durum", help="etkin istisnalar")
    d.add_argument("--json", action="store_true")
    alt.add_parser("ozet", help="oturum başı satırı")
    alt.add_parser("kanca", help="PreToolUse kancası")
    return p


def main(argv: list[str] | None = None) -> int:
    for akis in (sys.stdout, sys.stderr):
        if hasattr(akis, "reconfigure"):
            akis.reconfigure(encoding="utf-8", errors="replace")
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["kanca"]:
        try:
            ret = kanca(sys.stdin.buffer.read())
        except Exception:  # noqa: BLE001 - kanca işi hiçbir koşulda bozmaz
            ret = None
        if ret is not None:
            print(json.dumps(ret, ensure_ascii=True))
        return 0
    if argv[:1] == ["denetle"]:
        try:
            harita = harita_yukle()
        except (OSError, ValueError) as h:
            print(f"KOTA: harita okunamadı: {h}", file=sys.stderr)
            return 2
        yaml_yolu = KOK / HAVUZ_YAPILANDIRMASI
        sorunlar = denetle(harita, yaml_yolu.read_text(encoding="utf-8") if yaml_yolu.is_file() else None)
        if sorunlar:
            print(f"KOTA: tavan kuralı {len(sorunlar)} yerde aşılıyor")
            for s in sorunlar:
                print(f"  - {s}")
            return 1
        print("KOTA: tavan kuralı temiz")
        return 0
    if argv[:1] == ["ozet"]:
        try:
            metin = ozet_metni(harita_yukle(), oku(dosya_yolu()))
        except Exception:  # noqa: BLE001
            metin = ""
        if metin:
            print(metin)
        return 0
    a = _ayristirici().parse_args(argv)
    try:
        harita = harita_yukle()
        yol = dosya_yolu()
        simdi = simdi_utc()
        if a.komut == "durum":
            kayitlar = etkin(oku(yol), simdi)
            if a.json:
                print(json.dumps({"dosya": str(yol) if yol else None, "istisnalar": kayitlar,
                                  "kisit": kisitlar(harita, kayitlar, simdi)}, ensure_ascii=False, indent=2))
            else:
                print(ozet_metni(harita, kayitlar, simdi) or "Etkin kota istisnası yok: temel düzen geçerli.")
            return 0
        if yol is None:
            raise KotaHatasi(f"İstisna dosyası yeri yok: VOLKAN_KASA ya da {DOSYA_DEGISKENI} tanımlı değil.")
        if a.komut == "kaldir":
            n = kaldir(harita, yol, a.hedef, simdi)
            print(f"{n} istisna kaldırıldı." + ("" if n else " (eşleşen etkin istisna yoktu)"))
            return 0
        kayit = ekle(harita, yol, a.komut, a.havuz, simdi, sure=a.sure, bitis=a.bitis,
                     kalan=getattr(a, "kalan", None), gun=getattr(a, "gun", None), kademe=getattr(a, "kademe", None),
                     neden=a.neden)
        if kayit.get("yazilmadi"):
            print(f"Kısıt gerekmiyor: oran {kayit['oran']} (1 ve üstü normal hıza yetiyor). Hiçbir şey yazılmadı.")
        else:
            print("Yazıldı: " + kayit_satiri(harita, kayit, simdi))
        return 0
    except KotaHatasi as h:
        print(f"HATA: {h}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
