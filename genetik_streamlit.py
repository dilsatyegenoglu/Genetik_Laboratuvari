# -*- coding: utf-8 -*-
"""
Genetik Laboratuvarı - Öğretici Streamlit Uygulaması
====================================================
© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır.

Ön lisans Genetik dersi için etkileşimli öğretim aracı: genetiğe giriş, tarihçe,
hücre, kromozom, hücre döngüsü, mitoz, mayoz, gametogenez, nükleik asitler,
sentral dogma ve mutasyon, temel terimler. Her konunun sonunda 10 seçmeli
alıştırma ve adım adım çözüm.

Kurulum   : pip install -r requirements.txt
Çalıştırma: streamlit run genetik_streamlit.py
"""

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Genetik Laboratuvarı", page_icon="🧬", layout="wide")

TELIF = "© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır."

# Renkler
MAVI, PEMBE, YESIL, TURUNCU = "#3B6FB6", "#D9577A", "#3C9A5F", "#E8A33B"
MOR, GRI_K, SARI = "#8E5BB5", "#5F6B7A", "#F2C94C"
K_ANNE_R, K_BABA_R = "#5B8DD6", "#E06C8C"          # anneden / babadan gelen kromozom
BAZ_RENK = {"A": "#E15759", "T": "#4E79A7", "U": "#76B7B2", "G": "#59A14F", "C": "#EDC948"}
YAZI = 'font-family="Source Sans Pro, Segoe UI, Arial, sans-serif"'

st.markdown("""
<style>
.kutucuk {border-left:5px solid #3B6FB6; background:rgba(59,111,182,0.08);
          padding:10px 14px; border-radius:6px; margin:6px 0 10px 0;}
.uyari {border-left:5px solid #D9534F; background:rgba(217,83,79,0.08);
        padding:10px 14px; border-radius:6px; margin:6px 0 10px 0;}
.ipucu {border-left:5px solid #3C9A5F; background:rgba(60,154,95,0.08);
        padding:10px 14px; border-radius:6px; margin:6px 0 10px 0;}
.kartlar {display:flex; flex-wrap:wrap; gap:12px; margin:8px 0 14px 0;}
.kart {flex:1 1 220px; border:1px solid rgba(128,128,128,0.35); border-radius:10px;
       padding:12px 14px; background:rgba(128,128,128,0.05);}
.kart h4 {margin:0 0 6px 0; font-size:1.02rem;}
.kart p {margin:0; font-size:0.93rem;}
.dizi {font-family:monospace; font-size:18px; letter-spacing:1px; line-height:2.0;
       overflow-x:auto; white-space:nowrap; padding:6px 10px; border-radius:8px;
       background:rgba(128,128,128,0.07);}
.baz {display:inline-block; min-width:20px; text-align:center; border-radius:4px;
      margin:1px; padding:0 2px; color:#111; font-weight:700;}
.kodon {display:inline-block; border:1.5px solid rgba(128,128,128,0.6); border-radius:6px;
        padding:2px 6px; margin:3px; text-align:center; font-family:monospace;}
.kodon small {display:block; font-family:sans-serif; font-size:11px;}
.zaman {border-left:4px solid #3B6FB6; padding:4px 0 4px 12px; margin:6px 0;}
.zaman b.yil {color:#3B6FB6; font-size:1.05rem;}
.flash {border:2px solid #3B6FB6; border-radius:14px; padding:26px; text-align:center;
        font-size:1.4rem; font-weight:700; margin:10px 0;}
.flash-cevap {font-size:1.05rem; font-weight:400; margin-top:12px;}
.adim-baslik {font-size:1.15rem; font-weight:700; color:#3B6FB6; margin-top:18px;
              border-bottom:2px solid rgba(59,111,182,0.3);}
</style>
""", unsafe_allow_html=True)


def ipucu(metin):
    st.markdown(f'<div class="ipucu">{metin}</div>', unsafe_allow_html=True)


def kartlar(liste):
    """liste: [(başlık, metin), ...]"""
    icerik = "".join(f'<div class="kart"><h4>{b}</h4><p>{m}</p></div>' for b, m in liste)
    st.markdown(f'<div class="kartlar">{icerik}</div>', unsafe_allow_html=True)


# ===========================================================================
# Yardımcılar
# ===========================================================================
def kutu(metin):
    st.markdown(f'<div class="kutucuk">{metin}</div>', unsafe_allow_html=True)


def uyari(metin):
    st.markdown(f'<div class="uyari">{metin}</div>', unsafe_allow_html=True)


def ciz(fig, yukseklik=380):
    fig.update_layout(height=yukseklik, margin=dict(l=40, r=20, t=50, b=40),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def tablo(df):
    try:
        st.dataframe(df, hide_index=True, width="stretch")
    except TypeError:
        st.dataframe(df, hide_index=True, use_container_width=True)


def rng():
    if "rng" not in st.session_state:
        st.session_state.rng = np.random.default_rng()
    return st.session_state.rng


# ===========================================================================
# Alıştırma motoru
# ===========================================================================
SORU_SAYISI = 10


def _md(t):
    return ("md", t)


def _tx(t):
    return ("tex", t)


def _fmt(x, ondalik=4):
    if abs(x - round(x)) < 1e-9 and abs(x) >= 1:
        return f"{int(round(x))}"
    return f"{x:.{ondalik}f}"


def soru_sayi(metin, dogru, cozum, yanlis=(), ondalik=4, tol=None):
    """Sayısal soru; sık yapılan hatalardan türetilen yanlış seçeneklerle seçmeliye çevrilir."""
    return {"tip": "sayi", "metin": metin, "dogru": float(dogru), "yanlis": list(yanlis),
            "ondalik": ondalik, "cozum": cozum}


def soru_secim(r, metin, dogru, yanlislar, cozum):
    return {"tip": "secim", "metin": metin, "dogru": dogru, "yanlis": list(yanlislar),
            "cozum": cozum}


def _secmeliye_cevir(r, s):
    if s["tip"] == "secim":
        secenekler = [s["dogru"]] + s["yanlis"]
    else:
        x, od = s["dogru"], s["ondalik"]
        dogru = _fmt(x, od)
        olasilik = 0 < x < 1
        secenekler = [dogru]
        for v in s["yanlis"]:
            if v is None or not math.isfinite(v) or (v < 0 <= x) or (olasilik and v > 1):
                continue
            t = _fmt(v, od)
            if t not in secenekler:
                secenekler.append(t)
            if len(secenekler) == 4:
                break
        deneme = 0
        while len(secenekler) < 4 and deneme < 200:
            deneme += 1
            if abs(x - round(x)) < 1e-9 and abs(x) >= 1:
                adim_ = max(3, int(round(abs(x) * 0.25)))
                v = x + int(r.choice([-1, 1])) * int(r.integers(1, adim_ + 1))
            elif deneme > 40 or abs(x) < 10 ** (-od + 1):
                v = abs(x) + float(r.integers(5, 400)) * 10 ** (-od)
            else:
                v = x * (1 + float(r.choice([-1, 1])) * float(r.uniform(0.12, 0.6)))
            if (v < 0 <= x) or (olasilik and v >= 1):
                continue
            t = _fmt(v, od)
            if t not in secenekler:
                secenekler.append(t)
        s = dict(s, dogru=dogru)
    sira = r.permutation(len(secenekler))
    s["secenekler"] = [secenekler[i] for i in sira]
    return s


def _sec(r, liste):
    return liste[int(r.integers(0, len(liste)))]


def _kavram_sec(r, havuz, adet):
    idx = r.permutation(len(havuz))[:adet]
    return [havuz[i] for i in idx]


def _al_cevapla(k, i):
    v = st.session_state.get(f"{k}_c{i}")
    if v is not None and f"{k}_cevap{i}" not in st.session_state:
        st.session_state[f"{k}_cevap{i}"] = v


ADET_SECENEK = [10, 20, 30]


def _temizle(k):
    for i in range(1, max(ADET_SECENEK) + 1):
        for ek in ("c", "cevap", "kilit"):
            st.session_state.pop(f"{k}_{ek}{i}", None)


def _al_yenile(k, uretici):
    _temizle(k)
    st.session_state[k] = _uret(uretici, st.session_state.get(f"{k}_adet", SORU_SAYISI))


def _uret(uretici, adet=SORU_SAYISI):
    """Üreticiyi gerektiği kadar çağırıp metni tekrarlanmayan 'adet' soru toplar."""
    r = rng()
    sorular, gorulen = [], set()
    for _ in range(40):
        for s in uretici(r):
            if s["metin"] not in gorulen:
                gorulen.add(s["metin"])
                sorular.append(_secmeliye_cevir(r, s))
            if len(sorular) >= adet:
                return sorular
    return sorular


def alistirma_blogu(anahtar, baslik, uretici):
    st.divider()
    st.subheader(f"✍️ Alıştırmalar: {baslik}")
    st.caption("Her soruda bir seçenek işaretleyin. Yanıtınız kilitlenir; doğru ya da yanlış "
               "olduğu ve **adım adım çözüm** o zaman açılır. Önce kâğıt-kalemle hesaplayın!")
    k = f"al_{anahtar}"
    st.radio("Kaç soru?", ADET_SECENEK, horizontal=True, key=f"{k}_adet",
             on_change=_al_yenile, args=(k, uretici))
    if k not in st.session_state:
        st.session_state[k] = _uret(uretici, st.session_state.get(f"{k}_adet", SORU_SAYISI))
    sorular = st.session_state[k]
    dogru_say = cevap_say = 0
    for i, s in enumerate(sorular, 1):
        with st.container(border=True):
            st.markdown(f"**Soru {i} / {len(sorular)}.** {s['metin']}")
            secili = st.session_state.get(f"{k}_cevap{i}")
            if secili is None:
                st.radio("Seçiniz", s["secenekler"], index=None, key=f"{k}_c{i}",
                         label_visibility="collapsed", on_change=_al_cevapla, args=(k, i))
            else:
                cevap_say += 1
                st.radio("Yanıtınız", s["secenekler"], index=s["secenekler"].index(secili),
                         key=f"{k}_kilit{i}", disabled=True, label_visibility="collapsed")
                if secili == s["dogru"]:
                    dogru_say += 1
                    st.success("✅ Doğru!")
                else:
                    st.error(f"❌ Yanlış. Doğru yanıt: **{s['dogru']}**")
                with st.expander("📖 Nasıl hesaplanır?", expanded=True):
                    for tur, icerik in s["cozum"]:
                        if tur == "tex":
                            for parca in icerik.split(r"\qquad"):
                                st.latex(parca)
                        else:
                            st.markdown(icerik)
    st.progress(cevap_say / len(sorular),
                text=f"Yanıtlanan: {cevap_say} / {len(sorular)}  ·  Doğru: {dogru_say}")
    if cevap_say == len(sorular):
        oran = dogru_say / len(sorular)
        mesaj = (f"🎉 Tebrikler! {dogru_say}/{len(sorular)}" if oran >= 0.8 else
                 f"👍 {dogru_say}/{len(sorular)}: yanlışların çözümlerini tekrar inceleyin"
                 if oran >= 0.5 else
                 f"📚 {dogru_say}/{len(sorular)}: konuyu yukarıdan bir kez daha okuyup yeni "
                 "sorularla deneyin")
        (st.success if oran >= 0.8 else st.info if oran >= 0.5 else st.warning)(mesaj)
    st.button("🎲 Yeni sorular", key=f"{k}_yeni", on_click=_al_yenile, args=(k, uretici))


# ===========================================================================
# SVG yardımcıları
# ===========================================================================
def svg_goster(svg):
    import base64
    veri = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    st.markdown(f'<div style="width:100%;margin:6px 0 14px 0;text-align:center">'
                f'<img src="data:image/svg+xml;base64,{veri}" style="width:100%;'
                f'max-width:1000px;background:white;border-radius:12px"/></div>',
                unsafe_allow_html=True)


def _krom(x, y, h, w, renk, sent=0.33):
    yc = y + h * sent
    return (f'<rect x="{x - w / 2}" y="{y}" width="{w}" height="{yc - y - 3}" rx="{w / 2}" '
            f'fill="{renk}" stroke="#444" stroke-width="1.4"/>'
            f'<rect x="{x - w / 2}" y="{yc + 3}" width="{w}" height="{y + h - yc - 3}" '
            f'rx="{w / 2}" fill="{renk}" stroke="#444" stroke-width="1.4"/>'
            f'<ellipse cx="{x}" cy="{yc}" rx="{w * 0.3}" ry="5" fill="{renk}" stroke="#444" '
            f'stroke-width="1.2"/>')


def _bant(x, y, w, renk, h=12):
    return (f'<rect x="{x - w / 2 + 1.5}" y="{y - h / 2}" width="{w - 3}" height="{h}" '
            f'fill="{renk}" stroke="#222" stroke-width="0.8"/>')


def _yazi(x, y, t, boy=14, renk="#222", hiza="middle", kalin=False):
    k = ' font-weight="700"' if kalin else ""
    return (f'<text x="{x}" y="{y}" {YAZI} font-size="{boy}" fill="{renk}" '
            f'text-anchor="{hiza}"{k}>{t}</text>')


def _ok(x1, y1, x2, y2, renk="#555"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{renk}" stroke-width="2.2" '
            f'marker-end="url(#okucu)"/>')


_OK_TANIM = ('<defs><marker id="okucu" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
             'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
             'fill="#555"/></marker></defs>')


def _yarim_daire(cx, cy, r, sol, sag):
    return (f'<path d="M{cx},{cy - r} A{r},{r} 0 0 0 {cx},{cy + r} Z" fill="{sol}"/>'
            f'<path d="M{cx},{cy - r} A{r},{r} 0 0 1 {cx},{cy + r} Z" fill="{sag}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#333" stroke-width="1.4"/>')




K_ANNE, K_BABA, K_GRI = "#BFD3EE", "#F3C6D3", "#D5D9E0"
B_A, B_a, B_B, B_c = "#2B5DA8", "#E8A33B", "#3C9A5F", "#8E5BB5"
_YAZI_HW = 'font-family="Source Sans Pro, Segoe UI, Arial, sans-serif"'


def svg_homolog_lokus():
    s = [f'<svg viewBox="0 0 920 430" width="100%" style="max-width:920px" '
         f'xmlns="http://www.w3.org/2000/svg">']
    xm, xp = 190, 330
    s.append(_yazi(xm, 28, "Anneden gelen", 14, kalin=True))
    s.append(_yazi(xp, 28, "Babadan gelen", 14, kalin=True))
    s.append(_krom(xm, 45, 330, 38, K_ANNE, 0.3))
    s.append(_krom(xp, 45, 330, 38, K_BABA, 0.3))
    s.append(_yazi(120, 148, "sentromer", 12, "#666", "end"))
    s.append(f'<line x1="124" y1="144" x2="{xm - 14}" y2="144" stroke="#999"/>')
    loci = [(100, "A", "a", B_A, B_a, "Lokus A", "genotip <tspan font-weight='700'>Aa</tspan> → heterozigot"),
            (240, "B", "B", B_B, B_B, "Lokus B", "genotip <tspan font-weight='700'>BB</tspan> → homozigot"),
            (320, "c", "c", B_c, B_c, "Lokus C", "genotip <tspan font-weight='700'>cc</tspan> → homozigot")]
    for y, am, ab, rm, rb, ad, aciklama in loci:
        s.append(f'<line x1="150" y1="{y}" x2="560" y2="{y}" stroke="#888" stroke-dasharray="5 4"/>')
        s.append(_bant(xm, y, 38, rm, 14))
        s.append(_bant(xp, y, 38, rb, 14))
        s.append(f'<rect x="{xm - 62}" y="{y - 13}" width="26" height="26" rx="5" fill="{rm}"/>')
        s.append(_yazi(xm - 49, y + 6, am, 17, "white", kalin=True))
        s.append(f'<rect x="{xp + 34}" y="{y - 13}" width="26" height="26" rx="5" fill="{rb}"/>')
        s.append(_yazi(xp + 47, y + 6, ab, 17, "white", kalin=True))
        s.append(_yazi(575, y - 4, ad, 15, "#222", "start", True))
        s.append(f'<text x="575" y="{y + 15}" {YAZI} font-size="13" fill="#333">{aciklama}</text>')
    s.append('<rect x="575" y="370" width="335" height="50" rx="8" fill="#EEF3FA" stroke="#9DB4D8"/>')
    s.append(_yazi(588, 391, "Lokus = adres (iki homologda aynı yerde)", 13, "#1F3F73", "start", True))
    s.append(_yazi(588, 410, "Allel = o adresteki DNA dizisinin bir varyantı", 13, "#1F3F73", "start", True))
    s.append("</svg>")
    return "".join(s)


def svg_genotipler():
    s = [f'<svg viewBox="0 0 760 250" width="100%" style="max-width:760px" '
         f'xmlns="http://www.w3.org/2000/svg">']
    for cx, (a1, a2), ad, alt in [(130, ("A", "A"), "AA", "homozigot baskın"),
                                  (380, ("A", "a"), "Aa", "heterozigot"),
                                  (630, ("a", "a"), "aa", "homozigot çekinik")]:
        for dx, al in [(-24, a1), (24, a2)]:
            s.append(_krom(cx + dx, 20, 160, 26, K_GRI, 0.35))
            s.append(_bant(cx + dx, 110, 26, B_A if al == "A" else B_a, 14))
            s.append(_yazi(cx + dx + (-26 if dx < 0 else 26), 115, al, 15,
                           B_A if al == "A" else "#B37400", kalin=True))
        s.append(_yazi(cx, 210, ad, 20, kalin=True))
        s.append(_yazi(cx, 232, alt, 14, "#444"))
    s.append("</svg>")
    return "".join(s)


def html_snp():
    sol, sag = "GGATCCTAG", "TTAGGCA"
    st.markdown(f"""
<div style="font-family:monospace;font-size:19px;line-height:1.9;background:rgba(0,0,0,0.03);
padding:10px 16px;border-radius:8px;margin:4px 0 12px 0">
<span style="display:inline-block;width:110px;font-family:sans-serif;font-size:14px">Allel <b style="color:{B_A}">A</b>:</span>
5′-{sol}<b style="background:{B_A};color:white;padding:1px 5px;border-radius:4px">C</b>{sag}-3′<br>
<span style="display:inline-block;width:110px;font-family:sans-serif;font-size:14px">Allel <b style="color:#B37400">a</b>:</span>
5′-{sol}<b style="background:{B_a};color:white;padding:1px 5px;border-radius:4px">T</b>{sag}-3′
</div>""", unsafe_allow_html=True)


def html_baskinlik_mekanizma():
    def dot(c):
        return (f'<span style="display:inline-block;width:20px;height:20px;border-radius:50%;'
                f'background:{c};border:1.5px solid #555;vertical-align:middle"></span>')
    satir = [("AA", "2 sağlam kopya", "bol enzim → bol pigment", dot("#E9C21A") + " sarı",
              dot("#C62828") + " kırmızı", "yalnızca A ürünü"),
             ("Aa", "1 sağlam kopya", "yarı miktarda enzim", dot("#E9C21A") + " sarı (1 kopya yeter)",
              dot("#F48FB1") + " pembe (yarı pigment)", "A ve a ürünleri birlikte (ör. MN kan grubu)"),
             ("aa", "0 sağlam kopya", "işlevsiz enzim → pigment yok", dot("#7CB342") + " yeşil",
              dot("#FFFFFF") + " beyaz", "yalnızca a ürünü")]
    govde = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td>"
                    f"<td>{f}</td></tr>" for a, b, c, d, e, f in satir)
    st.markdown(f"""
<table style="width:100%;border-collapse:collapse;font-size:15px;margin:6px 0 10px 0">
<thead><tr style="background:rgba(59,111,182,0.12)">
<th style="padding:6px">Genotip</th><th>A allelinden</th><th>Sonuç</th>
<th>Tam baskın<br><small>(bezelye tohumu)</small></th>
<th>Eksik baskın<br><small>(aslanağzı çiçeği)</small></th>
<th>Kodominant<br><small>(a da işlevli ürün verir;<br>her ürün ayrı görünür)</small></th></tr></thead>
<tbody>{govde}</tbody></table>""", unsafe_allow_html=True)


# ===========================================================================
# ŞEMALAR (SVG) — tamamı bu uygulama için çizilmiştir
# ===========================================================================
def svg_ac(w, h, maks=None):
    m = f"max-width:{maks}px;" if maks else ""
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" style="{m}" '
            f'xmlns="http://www.w3.org/2000/svg">' + _OK_TANIM +
            f'<rect x="0" y="0" width="{w}" height="{h}" rx="12" fill="white"/>')


def _g(icerik, opaklik=1.0, donus=None, tx=0, ty=0):
    t = f' transform="translate({tx},{ty})' + (f' rotate({donus})"' if donus is not None else '"')
    return f'<g opacity="{opaklik}"{t}>{icerik}</g>'


def kromatit(x, y, L, w, renk, uc=None):
    """Dikey tek kromatit (y'den y+L'ye). uc=(renk2, oran): alt uçtaki farklı renkli parça."""
    s = (f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w}" height="{L:.1f}" rx="{w / 2}" '
         f'fill="{renk}" stroke="#333" stroke-width="1"/>')
    if uc:
        r2, oran = uc
        y2 = y + L * (1 - oran)
        h2 = L * oran
        s += (f'<rect x="{x - w / 2:.1f}" y="{y2:.1f}" width="{w}" height="{h2:.1f}" rx="{w / 2}" '
              f'fill="{r2}" stroke="none"/>'
              f'<rect x="{x - w / 2:.1f}" y="{y2:.1f}" width="{w}" height="{min(w / 2, h2):.1f}" '
              f'fill="{r2}" stroke="none"/>'
              f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w}" height="{L:.1f}" rx="{w / 2}" '
              f'fill="none" stroke="#333" stroke-width="1"/>')
    return s


def kromozom_tek(x, y, L, w, renk, uc=None, sent=0.4):
    """Eşlenmemiş kromozom (tek kromatit) + sentromer boğumu."""
    yc = y + L * sent
    return (kromatit(x, y, L, w, renk, uc) +
            f'<ellipse cx="{x}" cy="{yc:.1f}" rx="{w * 0.62:.1f}" ry="2.2" fill="#333"/>')


def kromozom_cift(x, y, L, w, renk, uclar=(None, None), sent=0.4, aralik=1.0):
    """Eşlenmiş kromozom: iki kardeş kromatit sentromerden bağlı."""
    x1 = x - w / 2 - aralik / 2
    x2 = x + w / 2 + aralik / 2
    yc = y + L * sent
    return (kromatit(x1, y, L, w, renk, uclar[0]) + kromatit(x2, y, L, w, renk, uclar[1]) +
            f'<ellipse cx="{x}" cy="{yc:.1f}" rx="{w * 1.05:.1f}" ry="3.2" fill="#333"/>')


def _hucre(cx, cy, rx, ry, dolgu="#FFF6E8", cizgi="#B9935A", kalinlik=2.2):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{dolgu}" '
            f'stroke="{cizgi}" stroke-width="{kalinlik}"/>')


def _sentrozom(x, y, aster=True, r=14):
    s = ""
    if aster:
        for a in range(0, 360, 30):
            s += (f'<line x1="{x}" y1="{y}" x2="{x + r * math.cos(math.radians(a)):.1f}" '
                  f'y2="{y + r * math.sin(math.radians(a)):.1f}" stroke="#9AA5B1" stroke-width="1"/>')
    s += (f'<rect x="{x - 4}" y="{y - 1.5}" width="8" height="3" fill="#444"/>'
          f'<rect x="{x - 1.5}" y="{y - 4}" width="3" height="8" fill="#444"/>')
    return s


def _ig(x1, y1, x2, y2):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#8FA3BF" '
            f'stroke-width="1.1"/>')


def _cekirdek(cx, cy, r, kesikli=False, dolgu="#E3ECF8"):
    k = ' stroke-dasharray="6 5"' if kesikli else ""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{dolgu}" stroke="#5A7FB8" '
            f'stroke-width="2"{k}/>')


def _kromatin(cx, cy, r, tohum=1):
    rr = np.random.default_rng(tohum)
    s = ""
    for renk in (K_ANNE_R, K_BABA_R, K_ANNE_R, K_BABA_R):
        nok = []
        x, y = cx + rr.uniform(-r / 2, r / 2), cy + rr.uniform(-r / 2, r / 2)
        for _ in range(14):
            x = min(max(x + rr.uniform(-9, 9), cx - r * 0.75), cx + r * 0.75)
            y = min(max(y + rr.uniform(-9, 9), cy - r * 0.75), cy + r * 0.75)
            nok.append(f"{x:.1f},{y:.1f}")
        s += (f'<polyline points="{" ".join(nok)}" fill="none" stroke="{renk}" '
              f'stroke-width="1.6" stroke-linejoin="round" opacity="0.9"/>')
    return s


# 2n = 4 örnek hücre: uzun çift + kısa çift (mavi: anneden, pembe: babadan)
_KROMOZOMLAR = [(50, K_ANNE_R), (50, K_BABA_R), (32, K_ANNE_R), (32, K_BABA_R)]
MITOZ_EVRELERI = ["İnterfaz", "Profaz", "Prometafaz", "Metafaz", "Anafaz", "Telofaz", "Sitokinez"]


def svg_mitoz(evre):
    W, H, cx, cy = 460, 320, 230, 150
    s = [svg_ac(W, H, 560)]
    w = 7
    if evre == "İnterfaz":
        s.append(_hucre(cx, cy, 200, 128))
        s.append(_cekirdek(cx - 10, cy, 72))
        s.append(_kromatin(cx - 10, cy, 72, 3))
        s.append(f'<circle cx="{cx + 12}" cy="{cy - 14}" r="15" fill="#3E4C8A"/>')
        s.append(_sentrozom(cx + 120, cy - 70))
        s.append(_yazi(cx, H - 22, "kromatin gevşek hâldedir; DNA S evresinde eşlenir", 12, "#333"))
        s.append(_yazi(cx, H - 6, "(G1 → S → G2)", 12, "#333"))
        s.append(_yazi(cx + 120, cy - 92, "sentrozom", 12, "#333"))
        s.append(_yazi(cx + 12, cy - 36, "çekirdekçik", 11, "#333"))
    elif evre == "Profaz":
        s.append(_hucre(cx, cy, 200, 128))
        s.append(_cekirdek(cx, cy, 82, kesikli=True))
        pozlar = [(cx - 40, cy - 52, -20), (cx + 30, cy - 50, 25), (cx - 30, cy + 8, 15),
                  (cx + 38, cy + 4, -30)]
        for (L, r), (x, y, d) in zip(_KROMOZOMLAR, pozlar):
            s.append(_g(kromozom_cift(0, -L * 0.4, L, w, r), donus=d, tx=x, ty=y))
        s.append(_sentrozom(cx - 120, cy - 80))
        s.append(_sentrozom(cx + 120, cy - 80))
        s.append(_yazi(cx, H - 22, "kromozomlar kısalıp kalınlaşır, görünür hâle gelir", 12, "#333"))
        s.append(_yazi(cx, H - 6, "çekirdek zarı dağılmaya başlar · sentrozomlar kutuplara gider",
                       12, "#333"))
    elif evre == "Prometafaz":
        s.append(_hucre(cx, cy, 200, 128))
        sol, sag = (cx - 175, cy), (cx + 175, cy)
        pozlar = [(cx - 50, cy - 45, -35), (cx + 25, cy - 55, 20), (cx - 20, cy + 30, 50),
                  (cx + 55, cy + 20, -15)]
        for (L, r), (x, y, d) in zip(_KROMOZOMLAR, pozlar):
            s.append(_ig(sol[0], sol[1], x, y))
            s.append(_ig(sag[0], sag[1], x, y))
        for (L, r), (x, y, d) in zip(_KROMOZOMLAR, pozlar):
            s.append(_g(kromozom_cift(0, -L * 0.4, L, w, r), donus=d, tx=x, ty=y))
        s.append(_sentrozom(*sol))
        s.append(_sentrozom(*sag))
        s.append(_yazi(cx, H - 22, "çekirdek zarı kayboldu", 12, "#333"))
        s.append(_yazi(cx, H - 6, "iğ iplikleri sentromerlere (kinetokorlara) bağlanıyor", 12, "#333"))
    elif evre == "Metafaz":
        s.append(_hucre(cx, cy, 200, 128))
        sol, sag = (cx - 175, cy), (cx + 175, cy)
        s.append(f'<line x1="{cx}" y1="{cy - 118}" x2="{cx}" y2="{cy + 118}" stroke="#D9534F" '
                 f'stroke-dasharray="5 4" stroke-width="1.4"/>')
        ys = [cy - 92, cy - 30, cy + 26, cy + 70]
        for (L, r), y in zip(_KROMOZOMLAR, ys):
            yc = y + L * 0.4
            s.append(_ig(sol[0], sol[1], cx - 5, yc))
            s.append(_ig(sag[0], sag[1], cx + 5, yc))
        for (L, r), y in zip(_KROMOZOMLAR, ys):
            s.append(kromozom_cift(cx, y, L, w, r))
        s.append(_sentrozom(*sol))
        s.append(_sentrozom(*sag))
        s.append(_yazi(cx + 8, cy - 112, "ekvator (metafaz plağı)", 11, "#D9534F", "start"))
        s.append(_yazi(cx, H - 6, "her kromozom TEK TEK ekvatora dizilir", 12, "#333"))
    elif evre == "Anafaz":
        s.append(_hucre(cx, cy, 205, 120))
        sol, sag = (cx - 180, cy), (cx + 180, cy)
        ys = [cy - 80, cy - 30, cy + 20, cy + 64]
        for (L, r), y in zip(_KROMOZOMLAR, ys):
            s.append(_ig(sol[0], sol[1], cx - 140, y))
            s.append(_ig(sag[0], sag[1], cx + 140, y))
            s.append(_g(kromozom_tek(0, 0, L, w, r, sent=0.06), donus=-90, tx=cx - 140, ty=y))
            s.append(_g(kromozom_tek(0, 0, L, w, r, sent=0.06), donus=90, tx=cx + 140, ty=y))
        s.append(_sentrozom(*sol))
        s.append(_sentrozom(*sag))
        s.append(_ok(cx - 15, cy + 100, cx - 85, cy + 100))
        s.append(_ok(cx + 15, cy + 100, cx + 85, cy + 100))
        s.append(_yazi(cx, H - 4, "kardeş kromatitler ayrılıp zıt kutuplara çekilir", 12, "#333"))
    elif evre == "Telofaz":
        s.append(_hucre(cx - 100, cy, 112, 115))
        s.append(_hucre(cx + 100, cy, 112, 115))
        s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="18" ry="62" fill="#FFF6E8"/>')
        for kx in (cx - 115, cx + 115):
            s.append(_cekirdek(kx, cy, 52, kesikli=True))
            for (L, r), dx in zip(_KROMOZOMLAR, (-22, -7, 8, 22)):
                s.append(kromozom_tek(kx + dx, cy - L / 2, L * 0.9, 5, r))
        s.append(_yazi(cx, H - 6, "iki yeni çekirdek oluşur · kromozomlar gevşer · boğumlanma "
                                  "başlar", 12, "#333"))
    else:  # Sitokinez
        for kx in (cx - 115, cx + 115):
            s.append(_hucre(kx, cy, 100, 105))
            s.append(_cekirdek(kx, cy, 50))
            for (L, r), dx in zip(_KROMOZOMLAR, (-22, -7, 8, 22)):
                s.append(kromozom_tek(kx + dx, cy - L / 2 + 2, L * 0.85, 5, r))
        s.append(_yazi(cx, H - 10, "genetik olarak ÖZDEŞ iki yavru hücre (2n)", 13, "#1F3F73", kalin=True))
    s.append("</svg>")
    return "".join(s)


def svg_sitokinez_karsilastir():
    s = [svg_ac(620, 230, 700)]
    s.append(_yazi(150, 22, "Hayvan hücresi: boğumlanma", 14, kalin=True))
    s.append(f'<path d="M40,115 C40,40 140,40 150,85 C160,40 260,40 260,115 C260,190 160,190 150,145 '
             f'C140,190 40,190 40,115 Z" fill="#FFF6E8" stroke="#B9935A" stroke-width="2.2"/>')
    s.append(_ok(150, 40, 150, 78, "#D9534F"))
    s.append(_ok(150, 190, 150, 152, "#D9534F"))
    s.append(_cekirdek(95, 115, 26))
    s.append(_cekirdek(205, 115, 26))
    s.append(_yazi(150, 215, "zar dışarıdan içe doğru büzülür", 12, "#333"))
    s.append(_yazi(470, 22, "Bitki hücresi: hücre plağı", 14, kalin=True))
    s.append('<rect x="345" y="45" width="250" height="140" rx="6" fill="#F3FAEE" stroke="#6BAA4A" '
             'stroke-width="6"/>')
    for y in range(58, 175, 11):
        s.append(f'<circle cx="470" cy="{y}" r="4" fill="#9DCB7A" stroke="#4E8A2E"/>')
    s.append(_cekirdek(405, 115, 26))
    s.append(_cekirdek(535, 115, 26))
    s.append(_yazi(470, 215, "ortada keseciklerden çeper (hücre plağı) oluşur", 12, "#333"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Mayoz
# ---------------------------------------------------------------------------
MAYOZ_EVRELERI = ["Profaz I", "Metafaz I", "Anafaz I", "Telofaz I",
                  "Profaz II", "Metafaz II", "Anafaz II", "Telofaz II"]


def _homologlar(krossing=True):
    """Her çift için [anne kromozomu kromatitleri, baba kromozomu kromatitleri].
    Kromatit = (renk, uç parçası)."""
    L_uzun, L_kisa = 50, 32
    if krossing:
        uzun = [[(K_ANNE_R, None), (K_ANNE_R, (K_BABA_R, 0.35))],
                [(K_BABA_R, (K_ANNE_R, 0.35)), (K_BABA_R, None)]]
    else:
        uzun = [[(K_ANNE_R, None), (K_ANNE_R, None)], [(K_BABA_R, None), (K_BABA_R, None)]]
    kisa = [[(K_ANNE_R, None), (K_ANNE_R, None)], [(K_BABA_R, None), (K_BABA_R, None)]]
    return [(L_uzun, uzun), (L_kisa, kisa)]


def _cift_ciz(x, y, L, kromatitler, w=7, aralik=1.0):
    (r1, u1), (r2, u2) = kromatitler
    x1, x2 = x - w / 2 - aralik / 2, x + w / 2 + aralik / 2
    yc = y + L * 0.4
    return (kromatit(x1, y, L, w, r1, u1) + kromatit(x2, y, L, w, r2, u2) +
            f'<ellipse cx="{x}" cy="{yc:.1f}" rx="{w * 1.05:.1f}" ry="3.2" fill="#333"/>')


def svg_mayoz(evre, dizilim=(0, 0), krossing=True):
    W, H, cx, cy = 460, 320, 230, 150
    s = [svg_ac(W, H, 560)]
    cift = _homologlar(krossing)
    w = 7
    # Metafaz I'de hangi homolog solda: dizilim[i] = 0 → anne solda
    sol_grup, sag_grup = [], []
    for (L, (anne, baba)), d in zip(cift, dizilim):
        a, b = (anne, baba) if d == 0 else (baba, anne)
        sol_grup.append((L, a))
        sag_grup.append((L, b))
    if evre == "Profaz I":
        s.append(_hucre(cx, cy, 200, 128))
        s.append(_cekirdek(cx, cy, 95, kesikli=True))
        for (L, (anne, baba)), (x, y) in zip(cift, [(cx - 30, cy - 62), (cx + 40, cy - 30)]):
            s.append(_cift_ciz(x - 8, y, L, anne))
            s.append(_cift_ciz(x + 8, y, L, baba))
            if krossing and L == 50:
                yk = y + L * 0.72
                s.append(f'<circle cx="{x}" cy="{yk:.1f}" r="9" fill="none" stroke="#D9534F" '
                         f'stroke-width="1.6"/>')
                s.append(_yazi(x + 14, yk + 22, "kiazma", 11, "#D9534F", "start"))
        s.append(_yazi(cx, H - 22, "homologlar eşleşir (sinaps) → tetrad (4 kromatit)", 12, "#333"))
        s.append(_yazi(cx, H - 6, "krossing-over: homolog kromatitler arasında parça değişimi",
                       12, "#333"))
    elif evre == "Metafaz I":
        s.append(_hucre(cx, cy, 200, 128))
        sol, sag = (cx - 175, cy), (cx + 175, cy)
        s.append(f'<line x1="{cx}" y1="{cy - 118}" x2="{cx}" y2="{cy + 118}" stroke="#D9534F" '
                 f'stroke-dasharray="5 4" stroke-width="1.4"/>')
        for (L, kr), y in zip(sol_grup, (cy - 80, cy + 10)):
            s.append(_ig(sol[0], sol[1], cx - 11, y + L * 0.4))
        for (L, kr), y in zip(sag_grup, (cy - 80, cy + 10)):
            s.append(_ig(sag[0], sag[1], cx + 11, y + L * 0.4))
        for (L, kr), y in zip(sol_grup, (cy - 80, cy + 10)):
            s.append(_cift_ciz(cx - 11, y, L, kr))
        for (L, kr), y in zip(sag_grup, (cy - 80, cy + 10)):
            s.append(_cift_ciz(cx + 11, y, L, kr))
        s.append(_sentrozom(*sol))
        s.append(_sentrozom(*sag))
        s.append(_yazi(cx, H - 6, "homolog ÇİFTLER (tetradlar) ekvatorda karşılıklı dizilir", 12, "#333"))
    elif evre == "Anafaz I":
        s.append(_hucre(cx, cy, 205, 120))
        sol, sag = (cx - 180, cy), (cx + 180, cy)
        for (L, kr), y in zip(sol_grup, (cy - 70, cy + 12)):
            s.append(_ig(sol[0], sol[1], cx - 95, y + L * 0.4))
            s.append(_cift_ciz(cx - 95, y, L, kr))
        for (L, kr), y in zip(sag_grup, (cy - 70, cy + 12)):
            s.append(_ig(sag[0], sag[1], cx + 95, y + L * 0.4))
            s.append(_cift_ciz(cx + 95, y, L, kr))
        s.append(_sentrozom(*sol))
        s.append(_sentrozom(*sag))
        s.append(_yazi(cx, H - 6, "HOMOLOGLAR ayrılır; kardeş kromatitler hâlâ bağlı", 12, "#333"))
    elif evre == "Telofaz I":
        for kx, grup in ((cx - 112, sol_grup), (cx + 112, sag_grup)):
            s.append(_hucre(kx, cy, 100, 108))
            for (L, kr), dx in zip(grup, (-14, 14)):
                s.append(_cift_ciz(kx + dx, cy - L / 2, L, kr))
        s.append(_yazi(cx, H - 6, "iki hücre, her biri n kromozomlu (kromozomlar hâlâ iki kromatitli)",
                       12, "#333"))
    elif evre in ("Profaz II", "Metafaz II"):
        for kx, grup in ((cx - 112, sol_grup), (cx + 112, sag_grup)):
            s.append(_hucre(kx, cy, 100, 108))
            p1, p2 = (kx - 88, cy), (kx + 88, cy)
            if evre == "Metafaz II":
                s.append(f'<line x1="{kx}" y1="{cy - 96}" x2="{kx}" y2="{cy + 96}" stroke="#D9534F" '
                         f'stroke-dasharray="5 4" stroke-width="1.2"/>')
                for (L, kr), y in zip(grup, (cy - 70, cy + 8)):
                    s.append(_ig(p1[0], p1[1], kx - 5, y + L * 0.4))
                    s.append(_ig(p2[0], p2[1], kx + 5, y + L * 0.4))
                    s.append(_cift_ciz(kx, y, L, kr))
            else:
                for (L, kr), (dx, dy, d) in zip(grup, ((-20, -30, -20), (22, 10, 25))):
                    s.append(_g(_cift_ciz(0, -L * 0.4, L, kr), donus=d, tx=kx + dx, ty=cy + dy))
            s.append(_sentrozom(*p1, r=10))
            s.append(_sentrozom(*p2, r=10))
        s.append(_yazi(cx, H - 6, "Mayoz II, mitoza benzer: kromozomlar tek tek dizilir" if evre ==
                       "Metafaz II" else "her hücrede yeni iğ iplikleri oluşur", 12, "#333"))
    elif evre == "Anafaz II":
        for kx, grup in ((cx - 112, sol_grup), (cx + 112, sag_grup)):
            s.append(_hucre(kx, cy, 104, 104))
            for y in (cy - 62, cy + 14):
                s.append(_ig(kx - 96, cy, kx - 74, y))
                s.append(_ig(kx + 96, cy, kx + 74, y))
            s.append(_sentrozom(kx - 96, cy, r=9))
            s.append(_sentrozom(kx + 96, cy, r=9))
            for (L, kr), y in zip(grup, (cy - 62, cy + 14)):
                (r1, u1), (r2, u2) = kr
                s.append(_g(kromozom_tek(0, 0, L * 0.85, 6, r1, u1, sent=0.06), donus=-90,
                            tx=kx - 74, ty=y))
                s.append(_g(kromozom_tek(0, 0, L * 0.85, 6, r2, u2, sent=0.06), donus=90,
                            tx=kx + 74, ty=y))
        s.append(_yazi(cx, H - 6, "kardeş kromatitler ayrılır", 12, "#333"))
    else:  # Telofaz II
        hucreler = []
        for grup in (sol_grup, sag_grup):
            for k in (0, 1):
                hucreler.append([(L, kr[k]) for L, kr in grup])
        for i, icerik in enumerate(hucreler):
            kx = 62 + i * 112
            s.append(_hucre(kx, cy - 10, 52, 62))
            for (L, (r, u)), dx in zip(icerik, (-10, 10)):
                s.append(kromozom_tek(kx + dx, cy - 10 - L / 2, L * 0.95, 7, r, u))
            s.append(_yazi(kx, cy + 72, f"gamet {i + 1}", 12, "#333", kalin=True))
        s.append(_yazi(cx, H - 18, "4 haploit (n) hücre; krossing-over ve bağımsız dağılım",
                       12, "#333"))
        s.append(_yazi(cx, H - 3, "yüzünden hepsi genetik olarak FARKLI", 12, "#333"))
    s.append("</svg>")
    return "".join(s)


def svg_krossing(nokta, genler="ABCDEF"):
    """İki homolog (anne: büyük harf, baba: küçük harf); 'nokta' iki gen arasındaki
    kırılma yeri (1..len-1). Mayoz sonunda oluşan 4 kromatit."""
    n = len(genler)
    W, H = 640, 300
    s = [svg_ac(W, H, 720)]
    bas, adim = 70, 46

    def kromatit_genli(y, alleller, renkler, etiket):
        out = (f'<rect x="{bas - 20}" y="{y - 12}" width="{adim * n + 10}" height="24" rx="12" '
               f'fill="#F4F6FA" stroke="#555"/>')
        for i, (al, rk) in enumerate(zip(alleller, renkler)):
            x = bas + i * adim
            out += (f'<rect x="{x - 16}" y="{y - 10}" width="{adim - 2}" height="20" fill="{rk}" '
                    f'opacity="0.85"/>' + _yazi(x + 6, y + 6, al, 15, "white", kalin=True))
        out += _yazi(bas + adim * n + 8, y + 5, etiket, 13, "#333", "start")
        return out

    s.append(_yazi(W / 2, 22, f"Kırılma noktası: {genler[nokta - 1]} ile {genler[nokta]} arası",
                   14, "#D9534F", kalin=True))
    xk = bas + nokta * adim - adim / 2 + 6
    s.append(f'<line x1="{xk}" y1="34" x2="{xk}" y2="{H - 6}" stroke="#D9534F" '
             f'stroke-dasharray="6 4" stroke-width="2"/>')
    A = list(genler)
    a = [g.lower() for g in genler]
    satirlar = [
        (A, [K_ANNE_R] * n, "1. kromatit: ata tipi (anneden)"),
        (A[:nokta] + a[nokta:], [K_ANNE_R] * nokta + [K_BABA_R] * (n - nokta),
         "2. kromatit: REKOMBİNANT"),
        (a[:nokta] + A[nokta:], [K_BABA_R] * nokta + [K_ANNE_R] * (n - nokta),
         "3. kromatit: REKOMBİNANT"),
        (a, [K_BABA_R] * n, "4. kromatit: ata tipi (babadan)"),
    ]
    for i, (al, rk, et) in enumerate(satirlar):
        s.append(kromatit_genli(70 + i * 58, al, rk, et))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Kromozom yapısı ve karyotip
# ---------------------------------------------------------------------------
def svg_kromozom_yapisi():
    W, H = 790, 370
    s = [svg_ac(W, H, 820)]
    x, y, L, w = 150, 40, 280, 30
    sent = 0.36
    yc = y + L * sent
    for xx in (x - w / 2 - 1, x + w / 2 + 1):
        s.append(f'<rect x="{xx - w / 2}" y="{y}" width="{w}" height="{yc - y - 6}" rx="{w / 2}" '
                 f'fill="{K_ANNE_R}" stroke="#333" stroke-width="1.5"/>')
        s.append(f'<rect x="{xx - w / 2}" y="{yc + 6}" width="{w}" height="{y + L - yc - 6}" rx="{w / 2}" '
                 f'fill="{K_ANNE_R}" stroke="#333" stroke-width="1.5"/>')
        for yy in (y + 3, y + L - 15):
            s.append(f'<rect x="{xx - w / 2 + 3}" y="{yy}" width="{w - 6}" height="12" rx="6" '
                     f'fill="{SARI}"/>')
    s.append(f'<ellipse cx="{x}" cy="{yc}" rx="{w * 1.1}" ry="7" fill="#333"/>')
    lab = [(y + 9, "telomer (uç bölge)"), ((y + yc) / 2, "p kolu (kısa kol)"),
           (yc, "sentromer (birincil boğum)"), ((yc + y + L) / 2, "q kolu (uzun kol)"),
           (y + L - 9, "telomer")]
    for yy, t in lab:
        s.append(f'<line x1="{x + w + 4}" y1="{yy}" x2="{x + 95}" y2="{yy}" stroke="#777"/>')
        s.append(_yazi(x + 100, yy + 5, t, 13, "#222", "start"))
    s.append(f'<path d="M{x - w - 2},{y + L + 12} L{x - w - 2},{y + L + 20} L{x + w + 2},{y + L + 20} '
             f'L{x + w + 2},{y + L + 12}" fill="none" stroke="#777"/>')
    s.append(_yazi(x, y + L + 38, "iki kardeş kromatit", 13, "#222"))
    # tipler
    tipler = [("Metasentrik", 0.5), ("Submetasentrik", 0.34), ("Akrosentrik", 0.12),
              ("Telosentrik", 0.0)]
    s.append(_yazi(625, 30, "Sentromerin yerine göre", 14, kalin=True))
    for i, (ad, sn) in enumerate(tipler):
        tx = 490 + i * 90
        yy, LL, ww = 70, 170, 12
        if sn == 0:
            s.append(f'<ellipse cx="{tx}" cy="{yy}" rx="{ww}" ry="5" fill="#333"/>')
            for xx in (tx - ww / 2 - 0.5, tx + ww / 2 + 0.5):
                s.append(f'<rect x="{xx - ww / 2}" y="{yy + 4}" width="{ww}" height="{LL - 4}" rx="{ww / 2}" '
                         f'fill="{TURUNCU}" stroke="#333"/>')
        else:
            s.append(kromozom_cift(tx, yy, LL, ww, TURUNCU, sent=sn))
        s.append(_yazi(tx, yy + LL + 22 + (14 if i % 2 else 0), ad, 12, "#222"))
    s.append("</svg>")
    return "".join(s)


_INSAN_KROMOZOM = {  # yaklaşık uzunluk (Mb) ve sentromer oranı (p/(p+q)), şematik
    1: (248, 0.50), 2: (242, 0.39), 3: (198, 0.46), 4: (190, 0.26), 5: (181, 0.27),
    6: (171, 0.35), 7: (159, 0.38), 8: (145, 0.31), 9: (138, 0.32), 10: (134, 0.30),
    11: (135, 0.40), 12: (133, 0.27), 13: (114, 0.15), 14: (107, 0.15), 15: (102, 0.17),
    16: (90, 0.40), 17: (83, 0.30), 18: (80, 0.23), 19: (59, 0.45), 20: (64, 0.44),
    21: (47, 0.25), 22: (51, 0.28), "X": (156, 0.39), "Y": (57, 0.18)}


def svg_karyotip(cinsiyet="Erkek (XY)"):
    W, H = 760, 440
    s = [svg_ac(W, H, 820)]
    satirlar = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11, 12], [13, 14, 15, 16, 17, 18],
                [19, 20, 21, 22, "XY"]]
    olcek = 0.33
    yb = [20, 120, 225, 320]
    for satir, y0 in zip(satirlar, yb):
        aralik = W / (len(satir) + 0.3)
        for i, no in enumerate(satir):
            x0 = aralik * (i + 0.65)
            if no == "XY":
                cifti = [("X", K_ANNE_R), ("X" if cinsiyet.startswith("Dişi") else "Y", K_BABA_R)]
                etiket = "XX" if cinsiyet.startswith("Dişi") else "XY"
            else:
                cifti = [(no, K_ANNE_R), (no, K_BABA_R)]
                etiket = str(no)
            for j, (k, renk) in enumerate(cifti):
                L, sn = _INSAN_KROMOZOM[k]
                LL = L * olcek
                s.append(kromozom_cift(x0 - 10 + j * 20, y0 + 4, LL, 5, renk, sent=sn, aralik=0.6))
            s.append(_yazi(x0, y0 + 4 + 248 * olcek + 14 if no in (1, 2, 3, 4, 5) else
                           y0 + 4 + max(_INSAN_KROMOZOM[c[0]][0] for c in cifti) * olcek + 14,
                           etiket, 12, "#333", kalin=(no == "XY")))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Hücre şemaları
# ---------------------------------------------------------------------------
ORGANELLER = {
    "zar": ("Hücre zarı", "Seçici geçirgen; fosfolipit çift tabaka ve proteinlerden oluşur. "
            "Hücreyi çevresinden ayırır, madde alışverişini denetler."),
    "cekirdek": ("Çekirdek", "Genetik materyali (DNA) taşır, hücrenin faaliyetlerini yönetir. "
                 "Çift katlı, porlu çekirdek zarıyla çevrilidir. İçinde kromatin bulunur; bölünme "
                 "sırasında kromatin yoğunlaşıp kromozomları oluşturur."),
    "cekirdekcik": ("Çekirdekçik", "Çekirdek içindeki koyu bölge; rRNA ve ribozom alt birimleri "
                    "burada yapılır. Zarı yoktur."),
    "mitokondri": ("Mitokondri", "Oksijenli solunumla ATP (enerji) üretir. Kendine ait DNA'sı "
                   "(mtDNA) vardır ve bu DNA genellikle anneden kalıtılır."),
    "ribozom": ("Ribozom", "Protein sentezinin yapıldığı zarsız yapı; rRNA ve proteinden oluşur. "
                "Sitoplazmada serbest ya da granüllü ER üzerinde bulunur."),
    "ger": ("Granüllü ER", "Üzerinde ribozom bulunan endoplazmik retikulum; protein sentezi ve "
            "taşınmasında görev alır."),
    "dger": ("Granülsüz ER", "Ribozomsuz ER; yağ (lipit) sentezi, zehirli maddelerin "
             "etkisizleştirilmesi ve madde taşınmasında görev alır."),
    "golgi": ("Golgi aygıtı", "Proteinleri ve lipitleri düzenler, paketler ve salgılar. "
              "Bitkilerde hücre çeperi maddelerinin yapımına da katılır."),
    "lizozom": ("Lizozom", "Sindirim enzimleri içeren kesecik; hücre içi sindirim yapar. "
                "Hayvan hücrelerinde belirgindir."),
    "sentrozom": ("Sentrozom (sentriyoller)", "Hayvan hücrelerinde bölünme sırasında iğ "
                  "ipliklerinin oluşumunu düzenler. Bitki hücrelerinde sentriyol yoktur."),
    "kloroplast": ("Kloroplast", "Fotosentez yapar; klorofil içerir. Kendine ait DNA'sı vardır. "
                   "Yalnızca bitki ve alg hücrelerinde bulunur."),
    "koful": ("Merkezi koful", "Bitki hücresinde büyük, su ve madde depolayan kesecik; hücreye "
              "turgor (dolgunluk) basıncı sağlar."),
    "ceper": ("Hücre çeperi", "Bitki hücresini dıştan saran, selülozdan yapılmış sağlam "
              "destek tabakası. Hayvan hücresinde yoktur."),
}
HAYVAN_ORGANEL = ["zar", "cekirdek", "cekirdekcik", "mitokondri", "ribozom", "ger", "dger",
                  "golgi", "lizozom", "sentrozom"]
BITKI_ORGANEL = ["ceper", "zar", "cekirdek", "cekirdekcik", "kloroplast", "koful", "mitokondri",
                 "ribozom", "ger", "golgi"]


def _mitokondri(x, y, rx=34, ry=16, don=0):
    zig = " ".join(f"{x - rx + 8 + i * (2 * rx - 16) / 8:.1f},{y + (6 if i % 2 else -6)}"
                   for i in range(9))
    return _g(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#F2A65A" stroke="#B5651D" '
              f'stroke-width="1.6"/><polyline points="{zig}" fill="none" stroke="#B5651D" '
              f'stroke-width="1.3"/>', donus=don, tx=0, ty=0) if don == 0 else \
        f'<g transform="rotate({don} {x} {y})"><ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" ' \
        f'fill="#F2A65A" stroke="#B5651D" stroke-width="1.6"/><polyline points="{zig}" ' \
        f'fill="none" stroke="#B5651D" stroke-width="1.3"/></g>'


def _golgi(x, y):
    s = ""
    for i in range(4):
        s += (f'<path d="M{x - 40 + i * 3},{y + i * 9} Q{x},{y - 14 + i * 9} {x + 40 - i * 3},{y + i * 9}" '
              f'fill="none" stroke="#C0577A" stroke-width="5" stroke-linecap="round"/>')
    for dx, dy in ((48, -6), (52, 14), (-48, 10)):
        s += f'<circle cx="{x + dx}" cy="{y + dy}" r="4.5" fill="#E58FAE" stroke="#C0577A"/>'
    return s


def _kloroplast(x, y, don=0):
    ic = "".join(f'<rect x="{x - 18 + i * 9}" y="{y - 6}" width="6" height="12" rx="1.5" '
                 f'fill="#2E7D32"/>' for i in range(5))
    return (f'<g transform="rotate({don} {x} {y})"><ellipse cx="{x}" cy="{y}" rx="30" ry="14" '
            f'fill="#7BC67E" stroke="#2E7D32" stroke-width="1.6"/>{ic}</g>')


def svg_hucre(tur="Hayvan", secili=None):
    W, H = 560, 400
    s = [svg_ac(W, H, 620)]
    parcalar, halolar, numaralar = {}, {}, {}
    rr = np.random.default_rng(7)
    if tur == "Hayvan":
        parcalar["zar"] = ('<path d="M60,200 C50,90 170,30 290,40 C420,45 520,110 510,210 '
                           'C500,320 400,370 280,365 C150,360 70,300 60,200 Z" fill="#FDF1E4" '
                           'stroke="#C9A27E" stroke-width="4"/>')
        halolar["zar"] = '<path d="M60,200 C50,90 170,30 290,40 C420,45 520,110 510,210 C500,320 400,370 280,365 C150,360 70,300 60,200 Z"'
        numaralar["zar"] = (505, 150)
        nx, ny, nr = 250, 200, 72
        ger_merkez = (nx, ny, nr + 14)
        parcalar["ger"] = "".join(
            f'<path d="M{nx + (nr + 14 + k * 11) * math.cos(math.radians(-60)):.1f},'
            f'{ny + (nr + 14 + k * 11) * math.sin(math.radians(-60)):.1f} '
            f'A{nr + 14 + k * 11},{nr + 14 + k * 11} 0 0 1 '
            f'{nx + (nr + 14 + k * 11) * math.cos(math.radians(50)):.1f},'
            f'{ny + (nr + 14 + k * 11) * math.sin(math.radians(50)):.1f}" fill="none" '
            f'stroke="#7E9CD1" stroke-width="5"/>' for k in range(3)) + "".join(
            f'<circle cx="{nx + (nr + 19 + k * 11) * math.cos(math.radians(a)):.1f}" '
            f'cy="{ny + (nr + 19 + k * 11) * math.sin(math.radians(a)):.1f}" r="2" fill="#333"/>'
            for k in range(3) for a in range(-58, 50, 9))
        halolar["ger"] = f'<circle cx="{nx + 70}" cy="{ny - 10}" r="70"'
        numaralar["ger"] = (nx + 118, ny - 40)
        parcalar["cekirdek"] = (f'<circle cx="{nx}" cy="{ny}" r="{nr + 4}" fill="#CFDDF5" '
                                f'stroke="#5A7FB8" stroke-width="2"/><circle cx="{nx}" cy="{ny}" '
                                f'r="{nr}" fill="#CFDDF5" stroke="#5A7FB8" stroke-width="1.5"/>'
                                + _kromatin(nx, ny, nr, 5))
        halolar["cekirdek"] = f'<circle cx="{nx}" cy="{ny}" r="{nr + 10}"'
        numaralar["cekirdek"] = (nx - 50, ny + 50)
        parcalar["cekirdekcik"] = f'<circle cx="{nx + 18}" cy="{ny - 15}" r="20" fill="#3E4C8A"/>'
        halolar["cekirdekcik"] = f'<circle cx="{nx + 18}" cy="{ny - 15}" r="27"'
        numaralar["cekirdekcik"] = (nx + 18, ny - 15)
        parcalar["mitokondri"] = (_mitokondri(420, 130, don=25) + _mitokondri(130, 290, don=-20)
                                  + _mitokondri(285, 338, don=-6))
        halolar["mitokondri"] = '<circle cx="420" cy="130" r="42"'
        numaralar["mitokondri"] = (420, 130)
        parcalar["dger"] = "".join(
            f'<path d="M{95 + k * 14},{120 + k * 6} q15,-14 30,0 t30,0 t30,0" fill="none" '
            f'stroke="#9DB3DA" stroke-width="4"/>' for k in range(3))
        halolar["dger"] = '<circle cx="150" cy="128" r="50"'
        numaralar["dger"] = (140, 105)
        parcalar["golgi"] = _golgi(370, 330 - 40)
        halolar["golgi"] = '<circle cx="370" cy="300" r="58"'
        numaralar["golgi"] = (370, 270)
        parcalar["lizozom"] = (f'<circle cx="470" cy="230" r="13" fill="#B07CC6" stroke="#6E3C88"/>'
                               f'<circle cx="190" cy="335" r="11" fill="#B07CC6" stroke="#6E3C88"/>')
        halolar["lizozom"] = '<circle cx="470" cy="230" r="22"'
        numaralar["lizozom"] = (470, 230)
        parcalar["sentrozom"] = _sentrozom(340, 80, aster=False)
        halolar["sentrozom"] = '<circle cx="340" cy="80" r="16"'
        numaralar["sentrozom"] = (360, 70)
        nok = []
        for _ in range(60):
            x, y = rr.uniform(90, 480), rr.uniform(70, 340)
            if (x - nx) ** 2 + (y - ny) ** 2 > (nr + 50) ** 2:
                nok.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2.2" fill="#333"/>')
        parcalar["ribozom"] = "".join(nok)
        halolar["ribozom"] = '<circle cx="110" cy="230" r="30"'
        numaralar["ribozom"] = (110, 230)
        sira = HAYVAN_ORGANEL
    else:
        parcalar["ceper"] = ('<rect x="30" y="30" width="500" height="340" rx="22" fill="#E8F5E0" '
                             'stroke="#5E9E3F" stroke-width="12"/>')
        halolar["ceper"] = '<rect x="20" y="20" width="520" height="360" rx="26"'
        numaralar["ceper"] = (30, 200)
        parcalar["zar"] = ('<rect x="44" y="44" width="472" height="312" rx="16" fill="#FBF6E9" '
                           'stroke="#C9A27E" stroke-width="3"/>')
        halolar["zar"] = '<rect x="44" y="44" width="472" height="312" rx="16"'
        numaralar["zar"] = (516, 100)
        parcalar["koful"] = ('<rect x="200" y="80" width="250" height="230" rx="40" fill="#D7ECFA" '
                             'stroke="#7FB3D9" stroke-width="2"/>')
        halolar["koful"] = '<rect x="195" y="75" width="260" height="240" rx="44"'
        numaralar["koful"] = (325, 195)
        nx, ny, nr = 120, 130, 50
        parcalar["cekirdek"] = (f'<circle cx="{nx}" cy="{ny}" r="{nr + 4}" fill="#CFDDF5" '
                                f'stroke="#5A7FB8" stroke-width="2"/><circle cx="{nx}" cy="{ny}" '
                                f'r="{nr}" fill="#CFDDF5" stroke="#5A7FB8" stroke-width="1.5"/>'
                                + _kromatin(nx, ny, nr, 9))
        halolar["cekirdek"] = f'<circle cx="{nx}" cy="{ny}" r="{nr + 10}"'
        numaralar["cekirdek"] = (nx - 30, ny + 30)
        parcalar["cekirdekcik"] = f'<circle cx="{nx + 12}" cy="{ny - 10}" r="14" fill="#3E4C8A"/>'
        halolar["cekirdekcik"] = f'<circle cx="{nx + 12}" cy="{ny - 10}" r="20"'
        numaralar["cekirdekcik"] = (nx + 12, ny - 10)
        parcalar["kloroplast"] = (_kloroplast(80, 318, 70) + _kloroplast(250, 335, 0) +
                                  _kloroplast(480, 140, 80) + _kloroplast(420, 335, 10) +
                                  _kloroplast(230, 60, 0))
        halolar["kloroplast"] = '<circle cx="250" cy="335" r="38"'
        numaralar["kloroplast"] = (250, 335)
        parcalar["mitokondri"] = _mitokondri(165, 288, rx=24, ry=11, don=-30) + \
            _mitokondri(480, 260, rx=24, ry=11, don=70)
        halolar["mitokondri"] = '<circle cx="165" cy="288" r="30"'
        numaralar["mitokondri"] = (165, 288)
        parcalar["ger"] = "".join(
            f'<path d="M{nx + 60},{ny - 40 + k * 14} q12,10 0,22" fill="none" stroke="#7E9CD1" '
            f'stroke-width="4"/>' for k in range(4))
        halolar["ger"] = f'<circle cx="{nx + 64}" cy="{ny}" r="34"'
        numaralar["ger"] = (nx + 70, ny - 50)
        parcalar["golgi"] = _golgi(110, 210 + 5)
        halolar["golgi"] = '<circle cx="110" cy="215" r="45"'
        numaralar["golgi"] = (70, 200)
        nok = []
        for _ in range(40):
            x, y = rr.uniform(60, 500), rr.uniform(60, 345)
            if not (190 < x < 460 and 70 < y < 320) and (x - nx) ** 2 + (y - ny) ** 2 > (nr + 30) ** 2:
                nok.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2" fill="#333"/>')
        parcalar["ribozom"] = "".join(nok)
        halolar["ribozom"] = '<circle cx="480" cy="330" r="22"'
        numaralar["ribozom"] = (490, 330)
        sira = BITKI_ORGANEL
    cizim_sirasi = (["zar"] if tur == "Hayvan" else ["ceper", "zar", "koful"])
    cizim_sirasi += [k for k in sira if k not in cizim_sirasi]
    for k in cizim_sirasi:
        op = 1.0 if (secili is None or secili == k or k in ("zar", "ceper") and secili not in
                     ("zar", "ceper")) else 0.28
        if secili is not None and k in ("zar", "ceper") and secili != k:
            op = 0.55
        s.append(f'<g opacity="{op}">{parcalar[k]}</g>')
    if secili in halolar:
        s.append(halolar[secili] + ' fill="none" stroke="#FF3B30" stroke-width="4" '
                 'stroke-dasharray="8 5"/>')
    for i, k in enumerate(sira, 1):
        x, y = numaralar[k]
        vurgu = secili == k
        s.append(f'<circle cx="{x}" cy="{y}" r="{13 if vurgu else 11}" '
                 f'fill="{"#FF3B30" if vurgu else "#1F3F73"}" stroke="white" stroke-width="2"/>')
        s.append(_yazi(x, y + 4.5, str(i), 12, "white", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Nükleik asitler
# ---------------------------------------------------------------------------
def _besgen(cx, cy, r, dolgu, cizgi="#333"):
    pts = " ".join(f"{cx + r * math.cos(math.radians(-90 + 72 * i)):.1f},"
                   f"{cy + r * math.sin(math.radians(-90 + 72 * i)):.1f}" for i in range(5))
    return f'<polygon points="{pts}" fill="{dolgu}" stroke="{cizgi}" stroke-width="1.5"/>'


def _altigen(cx, cy, r, dolgu, cizgi="#333"):
    pts = " ".join(f"{cx + r * math.cos(math.radians(30 + 60 * i)):.1f},"
                   f"{cy + r * math.sin(math.radians(30 + 60 * i)):.1f}" for i in range(6))
    return f'<polygon points="{pts}" fill="{dolgu}" stroke="{cizgi}" stroke-width="1.5"/>'


def svg_nukleotid():
    W, H = 720, 300
    s = [svg_ac(W, H, 760)]
    s.append(f'<circle cx="110" cy="150" r="40" fill="{SARI}" stroke="#333" stroke-width="1.5"/>')
    s.append(_yazi(110, 157, "P", 24, "#333", kalin=True))
    s.append(_yazi(110, 215, "Fosfat grubu", 14, "#333", kalin=True))
    s.append('<line x1="150" y1="150" x2="222" y2="150" stroke="#333" stroke-width="3"/>')
    s.append(_besgen(285, 150, 62, "#F7D9B5"))
    s.append(_yazi(285, 157, "Şeker", 15, "#333", kalin=True))
    s.append(_yazi(285, 235, "pentoz şeker: deoksiriboz (DNA) / riboz (RNA)", 11, "#333"))
    for etiket, a in (("5′", 214), ("1′", 18), ("3′", 126)):
        x = 285 + 76 * math.cos(math.radians(a))
        y = 150 + 76 * math.sin(math.radians(a))
        s.append(_yazi(x, y + 5, etiket, 13, "#B5651D", kalin=True))
    s.append('<line x1="345" y1="135" x2="430" y2="110" stroke="#333" stroke-width="3"/>')
    s.append(f'<rect x="430" y="70" width="130" height="80" rx="10" fill="#BFE3C8" stroke="#333" '
             f'stroke-width="1.5"/>')
    s.append(_yazi(495, 105, "Azotlu baz", 15, "#333", kalin=True))
    s.append(_yazi(495, 127, "A · G · C · T (U)", 13, "#333"))
    s.append('<path d="M222,240 L222,252 L565,252 L565,240" fill="none" stroke="#3C9A5F" stroke-width="2"/>')
    s.append(_yazi(393, 272, "NÜKLEOZİT = şeker + baz", 14, "#3C9A5F", kalin=True))
    s.append('<path d="M70,40 L70,28 L565,28 L565,40" fill="none" stroke="#3B6FB6" stroke-width="2"/>')
    s.append(_yazi(318, 20, "NÜKLEOTİT = fosfat + şeker + baz", 14, "#3B6FB6", kalin=True))
    s.append(_yazi(186, 140, "ester bağı", 11, "#666"))
    s.append(_yazi(395, 100, "N-glikozit", 11, "#666"))
    s.append(_yazi(395, 112, "bağı", 11, "#666"))
    s.append("</svg>")
    return "".join(s)


def svg_purin_pirimidin():
    W, H = 720, 230
    s = [svg_ac(W, H, 760)]
    s.append(_yazi(180, 24, "PÜRİNLER (çift halka)", 15, "#8E5BB5", kalin=True))
    for i, (b, ad) in enumerate((("A", "Adenin"), ("G", "Guanin"))):
        x = 100 + i * 160
        s.append(_altigen(x, 110, 34, BAZ_RENK[b]))
        s.append(_besgen(x + 50, 110, 28, BAZ_RENK[b]))
        s.append(_yazi(x + 10, 118, b, 22, "#111", kalin=True))
        s.append(_yazi(x + 20, 180, ad, 14, "#333"))
    s.append(_yazi(540, 24, "PİRİMİDİNLER (tek halka)", 15, "#3C9A5F", kalin=True))
    for i, (b, ad) in enumerate((("C", "Sitozin"), ("T", "Timin"), ("U", "Urasil"))):
        x = 430 + i * 110
        s.append(_altigen(x, 110, 34, BAZ_RENK[b]))
        s.append(_yazi(x, 118, b, 22, "#111", kalin=True))
        s.append(_yazi(x, 180, ad, 13, "#333"))
        s.append(_yazi(x, 196, "yalnız DNA" if b == "T" else "yalnız RNA" if b == "U" else "DNA ve RNA",
                       11, "#666"))
    s.append(_yazi(W / 2, 218, "Eşleşme hep bir pürin + bir pirimidin: A═T (2 H bağı), G≡C (3 H bağı)",
                   13, "#1F3F73", kalin=True))
    s.append("</svg>")
    return "".join(s)


TAMAMLAYICI = {"A": "T", "T": "A", "G": "C", "C": "G"}


def svg_dna_merdiven(dizi):
    dizi = dizi[:16]
    n = len(dizi)
    adim = 44
    W = max(360, 120 + n * adim)
    H = 300
    s = [svg_ac(W, H, max(420, W))]
    y1, y2 = 60, 240
    x0 = 70
    s.append(_yazi(x0 - 40, y1 + 5, "5′", 15, "#B5651D", kalin=True))
    s.append(_yazi(x0 + n * adim - 4, y1 + 5, "3′", 15, "#B5651D", kalin=True))
    s.append(_yazi(x0 - 40, y2 + 5, "3′", 15, "#B5651D", kalin=True))
    s.append(_yazi(x0 + n * adim - 4, y2 + 5, "5′", 15, "#B5651D", kalin=True))
    s.append(f'<line x1="{x0 - 20}" y1="{y1}" x2="{x0 + n * adim - 22}" y2="{y1}" stroke="#555" stroke-width="3"/>')
    s.append(f'<line x1="{x0 - 20}" y1="{y2}" x2="{x0 + n * adim - 22}" y2="{y2}" stroke="#555" stroke-width="3"/>')
    for i, b in enumerate(dizi):
        x = x0 + i * adim
        t = TAMAMLAYICI[b]
        orta = (y1 + y2) / 2
        s.append(f'<rect x="{x - 12}" y="{y1 + 10}" width="24" height="{orta - y1 - 14}" rx="3" '
                 f'fill="{BAZ_RENK[b]}" stroke="#333"/>')
        s.append(f'<rect x="{x - 12}" y="{orta + 4}" width="24" height="{y2 - orta - 14}" rx="3" '
                 f'fill="{BAZ_RENK[t]}" stroke="#333"/>')
        hb = 3 if b in "GC" else 2
        for k in range(hb):
            xx = x - 6 + k * (12 / (hb - 1))
            s.append(f'<line x1="{xx:.1f}" y1="{orta - 4}" x2="{xx:.1f}" y2="{orta + 4}" '
                     f'stroke="#D9534F" stroke-width="1.6"/>')
        s.append(_yazi(x, y1 + 32, b, 15, "#111", kalin=True))
        s.append(_yazi(x, y2 - 18, t, 15, "#111", kalin=True))
        s.append(_besgen(x, y1, 9, "#F7D9B5"))
        s.append(_besgen(x, y2, 9, "#F7D9B5"))
        if i < n - 1:
            s.append(f'<circle cx="{x + adim / 2}" cy="{y1}" r="6" fill="{SARI}" stroke="#333"/>')
            s.append(f'<circle cx="{x + adim / 2}" cy="{y2}" r="6" fill="{SARI}" stroke="#333"/>')
    s.append(_yazi(W / 2, 22, "Kalıp olarak verilen iplik (üst) ve tamamlayıcı iplik (alt)", 13, "#333"))
    s.append(_yazi(W / 2, H - 20, "kırmızı çizgiler: hidrojen bağları · sarı: fosfat · turuncu: şeker",
                   12, "#666"))
    s.append("</svg>")
    return "".join(s)


def svg_cift_sarmal():
    W, H = 640, 220
    s = [svg_ac(W, H, 680)]
    xs = np.linspace(30, 610, 200)
    for faz, renk in ((0, "#2B5DA8"), (math.pi, "#C0504D")):
        pts = " ".join(f"{x:.1f},{110 + 70 * math.sin((x - 30) / 46 + faz):.1f}" for x in xs)
        s.append(f'<polyline points="{pts}" fill="none" stroke="{renk}" stroke-width="5"/>')
    for i, x in enumerate(np.arange(40, 610, 14)):
        ya = 110 + 70 * math.sin((x - 30) / 46)
        yb = 110 + 70 * math.sin((x - 30) / 46 + math.pi)
        b = "ATGC"[i % 4]
        s.append(f'<line x1="{x:.1f}" y1="{ya:.1f}" x2="{x:.1f}" y2="{(ya + yb) / 2:.1f}" '
                 f'stroke="{BAZ_RENK[b]}" stroke-width="5"/>')
        s.append(f'<line x1="{x:.1f}" y1="{(ya + yb) / 2:.1f}" x2="{x:.1f}" y2="{yb:.1f}" '
                 f'stroke="{BAZ_RENK[TAMAMLAYICI[b]]}" stroke-width="5"/>')
    s.append(_yazi(W / 2, 212, "Çift sarmal: şeker-fosfat omurga dışta, baz çiftleri içte (Watson &amp; Crick, 1953)",
                   13, "#333"))
    s.append("</svg>")
    return "".join(s)


def svg_replikasyon():
    W, H = 700, 260
    s = [svg_ac(W, H, 740)]
    eski, yeni = "#2B5DA8", "#E8A33B"
    s.append(f'<line x1="30" y1="120" x2="300" y2="120" stroke="{eski}" stroke-width="6"/>')
    s.append(f'<line x1="30" y1="140" x2="300" y2="140" stroke="{eski}" stroke-width="6"/>')
    s.append(f'<path d="M300,120 Q360,110 660,40" fill="none" stroke="{eski}" stroke-width="6"/>')
    s.append(f'<path d="M300,140 Q360,150 660,220" fill="none" stroke="{eski}" stroke-width="6"/>')
    s.append(f'<path d="M340,132 Q400,118 640,62" fill="none" stroke="{yeni}" stroke-width="6" stroke-dasharray="14 4"/>')
    s.append(f'<path d="M340,128 Q400,142 640,198" fill="none" stroke="{yeni}" stroke-width="6" stroke-dasharray="14 4"/>')
    s.append(f'<circle cx="305" cy="130" r="16" fill="#D9534F" opacity="0.8"/>')
    s.append(_yazi(305, 100, "helikaz", 12, "#D9534F", kalin=True))
    s.append(_yazi(110, 105, "ana (eski) DNA", 13, "#333"))
    s.append(_yazi(560, 105, "yeni DNA 1", 13, "#333"))
    s.append(_yazi(560, 170, "yeni DNA 2", 13, "#333"))
    s.append(f'<rect x="40" y="200" width="22" height="8" fill="{eski}"/>')
    s.append(_yazi(70, 208, "eski (kalıp) zincir", 12, "#333", "start"))
    s.append(f'<rect x="210" y="200" width="22" height="8" fill="{yeni}"/>')
    s.append(_yazi(240, 208, "yeni sentezlenen zincir (DNA polimeraz)", 12, "#333", "start"))
    s.append(_yazi(W / 2, 245, "YARI KORUNUMLU: her yeni DNA = 1 eski + 1 yeni zincir", 14, "#1F3F73", kalin=True))
    s.append("</svg>")
    return "".join(s)


def svg_meselson(kusak):
    W = 700
    satir_h = 54
    H = 40 + (kusak + 1) * satir_h
    s = [svg_ac(W, H, 740)]
    agir, hafif = "#1F3F73", "#F2B04B"
    for g in range(kusak + 1):
        y = 30 + g * satir_h
        s.append(_yazi(10, y + 18, f"{g}. kuşak", 13, "#333", "start", True))
        if g == 0:
            molekuller = [("A", "A")]
        else:
            molekuller = [("A", "H"), ("H", "A")] + [("H", "H")] * (2 ** g - 2)
        n = len(molekuller)
        gen = min(36, (W - 110) / n - 4)
        for i, (u, a) in enumerate(molekuller):
            x = 100 + i * (gen + 4)
            s.append(f'<rect x="{x:.1f}" y="{y + 4}" width="{gen:.1f}" height="9" fill="{agir if u == "A" else hafif}"/>')
            s.append(f'<rect x="{x:.1f}" y="{y + 17}" width="{gen:.1f}" height="9" fill="{agir if a == "A" else hafif}"/>')
    s.append("</svg>")
    return "".join(s)


def svg_sentral_dogma():
    W, H = 720, 260
    s = [svg_ac(W, H, 760)]
    s.append('<rect x="10" y="40" width="330" height="200" rx="14" fill="#E3ECF8" stroke="#5A7FB8" stroke-dasharray="6 4"/>')
    s.append(_yazi(175, 62, "ÇEKİRDEK", 13, "#5A7FB8", kalin=True))
    s.append('<rect x="360" y="40" width="350" height="200" rx="14" fill="#FDF1E4" stroke="#C9A27E" stroke-dasharray="6 4"/>')
    s.append(_yazi(535, 62, "SİTOPLAZMA (ribozom)", 13, "#B5651D", kalin=True))
    kutular = [(60, "DNA", "#2B5DA8"), (260, "mRNA", "#76B7B2"), (560, "PROTEİN", "#8E5BB5")]
    for x, ad, renk in kutular:
        s.append(f'<rect x="{x - 50}" y="120" width="{100 if ad != "PROTEİN" else 120}" height="50" '
                 f'rx="10" fill="{renk}"/>')
        s.append(_yazi(x + (10 if ad == "PROTEİN" else 0), 152, ad, 17, "white", kalin=True))
    s.append(_ok(112, 145, 205, 145))
    s.append(_yazi(158, 135, "transkripsiyon", 12, "#333", kalin=True))
    s.append(_ok(312, 145, 505, 145))
    s.append(_yazi(410, 135, "translasyon", 12, "#333", kalin=True))
    s.append('<path d="M40,118 C20,80 100,80 80,118" fill="none" stroke="#2B5DA8" stroke-width="2.4" marker-end="url(#okucu)"/>')
    s.append(_yazi(60, 92, "replikasyon", 12, "#2B5DA8", kalin=True))
    s.append(_yazi(W / 2, 22, "SENTRAL DOGMA: DNA → RNA → Protein", 16, "#1F3F73", kalin=True))
    s.append(_yazi(158, 200, "DNA'daki bilgi mRNA'ya", 12, "#333"))
    s.append(_yazi(158, 216, "kopyalanır", 12, "#333"))
    s.append(_yazi(560, 200, "mRNA'daki kodonlar okunur,", 12, "#333"))
    s.append(_yazi(560, 216, "tRNA'lar amino asit getirir", 12, "#333"))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Gametogenez, döllenme, cinsiyet
# ---------------------------------------------------------------------------
def _sperm(x, y, renk="#2B5DA8"):
    return (f'<ellipse cx="{x}" cy="{y}" rx="8" ry="5.5" fill="{renk}"/>'
            f'<path d="M{x + 8},{y} q6,-5 12,0 t12,0 t12,0" fill="none" stroke="{renk}" stroke-width="1.6"/>')


def svg_gametogenez():
    W, H = 760, 420
    s = [svg_ac(W, H, 800)]
    xs = [70, 210, 360, 520, 680]
    basliklar = ["Ana hücre (2n)", "Birincil (2n)", "Mayoz I → ikincil (n)", "Mayoz II (n)", "Olgun gamet (n)"]
    for x, b in zip(xs, basliklar):
        s.append(_yazi(x, 20, b, 12, "#555", kalin=True))
    # spermatogenez
    y = 115
    s.append(_yazi(10, y - 70, "SPERMATOGENEZ (testis)", 14, "#2B5DA8", "start", True))
    s.append(f'<circle cx="{xs[0]}" cy="{y}" r="22" fill="#CFDDF5" stroke="#2B5DA8" stroke-width="2"/>')
    s.append(_yazi(xs[0], y + 40, "spermatogonyum", 11, "#333"))
    s.append(_ok(xs[0] + 26, y, xs[1] - 30, y))
    s.append(f'<circle cx="{xs[1]}" cy="{y}" r="27" fill="#CFDDF5" stroke="#2B5DA8" stroke-width="2"/>')
    s.append(_yazi(xs[1], y + 44, "birincil spermatosit", 11, "#333"))
    for dy in (-35, 35):
        s.append(_ok(xs[1] + 28, y, xs[2] - 22, y + dy))
        s.append(f'<circle cx="{xs[2]}" cy="{y + dy}" r="19" fill="#CFDDF5" stroke="#2B5DA8" stroke-width="2"/>')
        for dy2 in (-15, 15):
            s.append(_ok(xs[2] + 20, y + dy, xs[3] - 16, y + dy + dy2))
            s.append(f'<circle cx="{xs[3]}" cy="{y + dy + dy2}" r="12" fill="#CFDDF5" stroke="#2B5DA8" stroke-width="2"/>')
            s.append(_ok(xs[3] + 14, y + dy + dy2, xs[4] - 22, y + dy + dy2))
            s.append(_sperm(xs[4] - 12, y + dy + dy2))
    s.append(_yazi(xs[2], y + 70, "ikincil spermatosit", 11, "#333"))
    s.append(_yazi(xs[3], y + 70, "spermatit", 11, "#333"))
    s.append(_yazi(xs[4] + 8, y + 70, "4 sperm", 12, "#2B5DA8", kalin=True))
    # oogenez
    y = 305
    s.append(_yazi(10, y - 70, "OOGENEZ (yumurtalık)", 14, "#C0504D", "start", True))
    s.append(f'<circle cx="{xs[0]}" cy="{y}" r="22" fill="#F8D7DE" stroke="#C0504D" stroke-width="2"/>')
    s.append(_yazi(xs[0], y + 40, "oogonyum", 11, "#333"))
    s.append(_ok(xs[0] + 26, y, xs[1] - 38, y))
    s.append(f'<circle cx="{xs[1]}" cy="{y}" r="34" fill="#F8D7DE" stroke="#C0504D" stroke-width="2"/>')
    s.append(_yazi(xs[1], y + 52, "birincil oosit", 11, "#333"))
    s.append(_ok(xs[1] + 36, y, xs[2] - 34, y + 10))
    s.append(f'<circle cx="{xs[2]}" cy="{y + 10}" r="31" fill="#F8D7DE" stroke="#C0504D" stroke-width="2"/>')
    s.append(_yazi(xs[2], y + 58, "ikincil oosit", 11, "#333"))
    s.append(_ok(xs[1] + 30, y - 18, xs[2] - 8, y - 46))
    s.append(f'<circle cx="{xs[2]}" cy="{y - 50}" r="8" fill="#F8D7DE" stroke="#C0504D" stroke-width="1.5"/>')
    s.append(_yazi(xs[2] + 14, y - 46, "1. polar cisim", 11, "#333", "start"))
    s.append(_ok(xs[2] + 32, y + 10, xs[3] - 30, y + 10))
    s.append(f'<circle cx="{xs[3]}" cy="{y + 10}" r="29" fill="#F8D7DE" stroke="#C0504D" stroke-width="2"/>')
    s.append(_ok(xs[2] + 26, y - 6, xs[3] - 6, y - 42))
    s.append(f'<circle cx="{xs[3]}" cy="{y - 48}" r="8" fill="#F8D7DE" stroke="#C0504D" stroke-width="1.5"/>')
    s.append(_yazi(xs[3] + 14, y - 44, "2. polar cisim", 11, "#333", "start"))
    s.append(_ok(xs[3] + 31, y + 10, xs[4] - 32, y + 10))
    s.append(f'<circle cx="{xs[4]}" cy="{y + 10}" r="30" fill="#F4B3C2" stroke="#C0504D" stroke-width="2.5"/>')
    s.append(_yazi(xs[4], y + 15, "yumurta", 12, "#7A1F33", kalin=True))
    s.append(_yazi(xs[4], y + 62, "1 yumurta + 3 polar cisim", 12, "#C0504D", kalin=True))
    s.append(_yazi(W / 2, H - 6, "Polar cisimler küçüktür ve dejenere olur; sitoplazmanın neredeyse tamamı yumurtada kalır.",
                   12, "#555"))
    s.append("</svg>")
    return "".join(s)


def svg_cinsiyet(sistem="XY"):
    W, H = 640, 300
    s = [svg_ac(W, H, 680)]
    if sistem == "XY":
        d, e = ("X", "X"), ("X", "Y")
        dis, erk = "♀ Dişi: XX", "♂ Erkek: XY"
        not_ = "Memeliler: cinsiyeti BABADAN gelen gamet (X ya da Y) belirler."
    else:
        d, e = ("Z", "W"), ("Z", "Z")
        dis, erk = "♀ Dişi: ZW", "♂ Erkek: ZZ"
        not_ = "Kuşlar: cinsiyeti ANNEDEN gelen gamet (Z ya da W) belirler."
    s.append(_yazi(130, 30, dis, 16, "#C0504D", kalin=True))
    s.append(_yazi(510, 30, erk, 16, "#2B5DA8", kalin=True))
    ox, oy, hc = 230, 80, 90
    s.append(_yazi(ox + hc, oy - 12, "Erkek gametleri", 12, "#2B5DA8"))
    s.append(f'<text x="{ox - 26}" y="{oy + hc + 4}" {YAZI} font-size="12" fill="#C0504D" '
             f'text-anchor="middle" transform="rotate(-90 {ox - 26} {oy + hc})">Dişi gametleri</text>')
    for j, g in enumerate(e):
        s.append(_yazi(ox + hc / 2 + j * hc, oy + 10, g, 18, "#2B5DA8", kalin=True))
    for i, g in enumerate(d):
        s.append(_yazi(ox - 6, oy + 30 + hc / 2 + i * hc, g, 18, "#C0504D", kalin=True))
    for i, gd in enumerate(d):
        for j, ge in enumerate(e):
            x, y = ox + j * hc, oy + 20 + i * hc
            z = "".join(sorted(gd + ge, key=lambda c: "XZWY".index(c)))
            disi = (sistem == "XY" and z == "XX") or (sistem == "ZW" and z == "ZW")
            s.append(f'<rect x="{x}" y="{y}" width="{hc}" height="{hc}" fill="{"#F8D7DE" if disi else "#CFDDF5"}" '
                     f'stroke="#555"/>')
            s.append(_yazi(x + hc / 2, y + hc / 2 + 2, z, 20, "#222", kalin=True))
            s.append(_yazi(x + hc / 2, y + hc / 2 + 22, "dişi" if disi else "erkek", 12, "#555"))
    s.append(_yazi(W / 2, H - 6, not_ + "  Oran: %50 dişi, %50 erkek.", 13, "#1F3F73", kalin=True))
    s.append("</svg>")
    return "".join(s)


def svg_varyasyon_kaynaklari():
    W, H = 760, 250
    s = [svg_ac(W, H, 800)]
    # mutasyon
    s.append(_yazi(125, 24, "1. MUTASYON", 15, "#D9534F", kalin=True))
    for r, (dz, y) in enumerate((("ATGCCTA", 70), ("ATGTCTA", 140))):
        for i, b in enumerate(dz):
            x = 40 + i * 25
            vurgu = r == 1 and i == 3
            s.append(f'<rect x="{x}" y="{y}" width="22" height="26" rx="4" fill="{BAZ_RENK[b]}" '
                     f'stroke="{"#D9534F" if vurgu else "#333"}" stroke-width="{3 if vurgu else 1}"/>')
            s.append(_yazi(x + 11, y + 18, b, 14, "#111", kalin=True))
    s.append(_ok(125, 100, 125, 134, "#D9534F"))
    s.append(_yazi(125, 200, "DNA dizisinde kalıtsal değişim", 12, "#333"))
    # rekombinasyon
    s.append(_yazi(385, 24, "2. REKOMBİNASYON", 15, "#3B6FB6", kalin=True))
    s.append(kromatit(345, 60, 110, 14, K_ANNE_R, (K_BABA_R, 0.4)))
    s.append(kromatit(370, 60, 110, 14, K_ANNE_R))
    s.append(kromatit(400, 60, 110, 14, K_BABA_R, (K_ANNE_R, 0.4)))
    s.append(kromatit(425, 60, 110, 14, K_BABA_R))
    s.append(f'<path d="M352,118 L393,128 M352,128 L393,118" stroke="#D9534F" stroke-width="2"/>')
    s.append(_yazi(385, 200, "krossing-over ile yeni allel", 12, "#333"))
    s.append(_yazi(385, 216, "kombinasyonları", 12, "#333"))
    # seleksiyon
    s.append(_yazi(640, 24, "3. SELEKSİYON", 15, "#3C9A5F", kalin=True))
    rr = np.random.default_rng(3)
    for i in range(18):
        x, y = rr.uniform(545, 640), rr.uniform(55, 165)
        koyu = i % 3 == 0
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="8" fill="{"#3C9A5F" if koyu else "#BFE3C8"}" stroke="#333"/>')
    s.append(_ok(650, 110, 690, 110, "#3C9A5F"))
    for i in range(6):
        s.append(f'<circle cx="{715 + (i % 2) * 18}" cy="{70 + (i // 2) * 30}" r="8" fill="#3C9A5F" stroke="#333"/>')
    s.append(_yazi(640, 200, "uygun genotiplerin", 12, "#333"))
    s.append(_yazi(640, 216, "seçilip çoğalması", 12, "#333"))
    s.append("</svg>")
    return "".join(s)


def svg_hucre_dongusu():
    W, H = 460, 420
    s = [svg_ac(W, H, 500)]
    cx, cy, r1, r2 = 230, 210, 175, 105
    dilimler = [("G1", 0.40, "#8CC8A8"), ("S", 0.30, "#7EA6E0"), ("G2", 0.18, "#F5C77E"),
                ("M", 0.12, "#E8828F")]
    a0 = -90.0
    for ad, oran, renk in dilimler:
        a1 = a0 + 360 * oran
        buyuk = 1 if oran > 0.5 else 0
        p = (f"M{cx + r1 * math.cos(math.radians(a0)):.1f},{cy + r1 * math.sin(math.radians(a0)):.1f} "
             f"A{r1},{r1} 0 {buyuk} 1 {cx + r1 * math.cos(math.radians(a1)):.1f},{cy + r1 * math.sin(math.radians(a1)):.1f} "
             f"L{cx + r2 * math.cos(math.radians(a1)):.1f},{cy + r2 * math.sin(math.radians(a1)):.1f} "
             f"A{r2},{r2} 0 {buyuk} 0 {cx + r2 * math.cos(math.radians(a0)):.1f},{cy + r2 * math.sin(math.radians(a0)):.1f} Z")
        s.append(f'<path d="{p}" fill="{renk}" stroke="white" stroke-width="3"/>')
        am = math.radians((a0 + a1) / 2)
        s.append(_yazi(cx + (r1 + r2) / 2 * math.cos(am), cy + (r1 + r2) / 2 * math.sin(am) + 7,
                       ad, 22, "#1E2A38", kalin=True))
        a0 = a1
    s.append(_yazi(cx, cy - 18, "HÜCRE", 16, "#333", kalin=True))
    s.append(_yazi(cx, cy + 4, "DÖNGÜSÜ", 16, "#333", kalin=True))
    s.append(_yazi(cx, cy + 30, "interfaz = G1 + S + G2", 12, "#555"))
    s.append(f'<circle cx="{cx + 200}" cy="{cy - 150}" r="26" fill="#DDE3EA" stroke="#5F6B7A"/>')
    s.append(_yazi(cx + 200, cy - 144, "G0", 16, "#333", kalin=True))
    s.append(_ok(cx + 105, cy - 118, cx + 178, cy - 140))
    s.append(_yazi(cx + 170, cy - 98, "bölünmeyen", 11, "#555"))
    s.append(_yazi(cx + 170, cy - 85, "hücreler", 11, "#555"))
    s.append("</svg>")
    return "".join(s)


# ===========================================================================
# EK ŞEMALAR: terimler, baskınlık, genom, ekstrakromozomal kalıtım,
#             transkripsiyon ve translasyon
# ===========================================================================
def svg_genotip_fenotip():
    """Bezelye tohum rengi: genotip (kromozom çifti) → fenotip (tohum)."""
    W, H = 760, 330
    s = [svg_ac(W, H, 800)]
    s.append(_yazi(W / 2, 24, "GENOTİP (taşınan alleller)  →  FENOTİP (gözlenen / ölçülen özellik)", 15, "#1F3F73", kalin=True))
    ornek = [("AA", "#F2C94C", "sarı", "homozigot dominant"),
             ("Aa", "#F2C94C", "sarı", "heterozigot (a gizli)"),
             ("aa", "#6FBF4A", "yeşil", "homozigot resesif")]
    for i, (gt, renk, ad, tur) in enumerate(ornek):
        cx = 130 + i * 250
        for j, al in enumerate(gt):
            x = cx - 32 + j * 26
            s.append(kromatit(x, 50, 110, 16, K_GRI))
            s.append(f'<rect x="{x - 8}" y="95" width="16" height="16" '
                     f'fill="{B_A if al == "A" else B_a}" stroke="#222"/>')
            s.append(_yazi(x, 182, al, 18, B_A if al == "A" else "#B37400", kalin=True))
        s.append(_ok(cx + 22, 115, cx + 70, 115))
        s.append(f'<circle cx="{cx + 100}" cy="115" r="30" fill="{renk}" stroke="#555" stroke-width="2"/>')
        s.append(f'<ellipse cx="{cx + 92}" cy="105" rx="8" ry="5" fill="white" opacity="0.5"/>')
        s.append(_yazi(cx + 100, 170, ad, 15, "#333", kalin=True))
        s.append(_yazi(cx + 30, 215, f"Genotip: {gt}", 15, "#222", kalin=True))
        s.append(_yazi(cx + 30, 236, tur, 13, "#555"))
        s.append(_yazi(cx + 30, 257, f"Fenotip: {ad} tohum", 13, "#555"))
    s.append(f'<rect x="20" y="276" width="{W - 40}" height="44" rx="10" fill="#EEF3FA" stroke="#9DB4D8"/>')
    s.append(_yazi(W / 2, 296, "A (sarı) dominant, a (yeşil) resesif. AA ve Aa'nın genotipi farklı, fenotipi AYNI.", 13, "#1F3F73", kalin=True))
    s.append(_yazi(W / 2, 313, "Yeşil fenotip ancak aa genotipinde ortaya çıkar.", 12, "#1F3F73"))
    s.append("</svg>")
    return "".join(s)


def svg_genom():
    W, H = 760, 330
    s = [svg_ac(W, H, 800)]
    s.append(_yazi(W / 2, 24, "GENOM: bir canlının (bir hücresinin) taşıdığı genetik materyalin TAMAMI", 15, "#1F3F73", kalin=True))
    s.append('<rect x="30" y="45" width="460" height="260" rx="40" fill="#E8F5E0" stroke="#5E9E3F" stroke-width="8"/>')
    s.append('<circle cx="170" cy="170" r="85" fill="#CFDDF5" stroke="#5A7FB8" stroke-width="2.5"/>')
    for i, (L, r) in enumerate([(70, K_ANNE_R), (70, K_BABA_R), (48, K_ANNE_R), (48, K_BABA_R), (32, K_ANNE_R), (32, K_BABA_R)]):
        s.append(kromozom_cift(115 + i * 22, 170 - L / 2, L, 6, r))
    s.append(_yazi(170, 280, "çekirdek genomu (kromozomlar)", 13, "#1F3F73", kalin=True))
    # mitokondri
    s.append(_mitokondri(345, 110, rx=48, ry=24, don=0))
    s.append('<circle cx="345" cy="110" r="11" fill="none" stroke="#7A1F33" stroke-width="3"/>')
    s.append(_yazi(345, 152, "mitokondri DNA'sı", 12, "#7A1F33", kalin=True))
    # kloroplast
    s.append(_kloroplast(400, 225, 0))
    s.append('<circle cx="400" cy="225" r="10" fill="none" stroke="#0B5A1C" stroke-width="3"/>')
    s.append(_yazi(400, 262, "kloroplast DNA'sı", 12, "#0B5A1C", kalin=True))
    s.append(_yazi(395, 286, "(yalnız bitkilerde)", 11, "#555"))
    kartlar_x = 515
    satir = [("Çekirdek genomu", "Kromozomlardaki DNA; genlerin çoğu buradadır"),
             ("Organel genomu", "Mitokondri ve kloroplastın küçük, halkasal DNA'sı"),
             ("İnsan genomu", "≈ 3 milyar baz çifti, ≈ 20 bin protein kodlayan gen"),
             ("Genom ≠ genotip", "Genom: tüm DNA; genotip: belirli lokuslardaki alleller")]
    for i, (b, t) in enumerate(satir):
        y = 60 + i * 62
        s.append(f'<rect x="{kartlar_x}" y="{y}" width="230" height="54" rx="8" fill="#F4F6FA" stroke="#B9C6DA"/>')
        s.append(_yazi(kartlar_x + 10, y + 20, b, 13, "#1F3F73", "start", True))
        words = t.split(" ")
        line1, line2 = "", ""
        for w_ in words:
            if len(line1) + len(w_) < 34 and not line2:
                line1 += w_ + " "
            else:
                line2 += w_ + " "
        s.append(_yazi(kartlar_x + 10, y + 36, line1.strip(), 11, "#333", "start"))
        s.append(_yazi(kartlar_x + 10, y + 49, line2.strip(), 11, "#333", "start"))
    s.append("</svg>")
    return "".join(s)


def svg_ekstrakromozomal():
    W, H = 760, 320
    s = [svg_ac(W, H, 800)]
    s.append(_yazi(W / 2, 24, "Ekstrakromozomal (sitoplazmik) kalıtım: organel DNA'sı ANNEDEN gelir", 15, "#1F3F73", kalin=True))
    # yumurta
    s.append('<circle cx="150" cy="150" r="80" fill="#F8D7DE" stroke="#C0504D" stroke-width="2.5"/>')
    s.append(_cekirdek(150, 150, 28))
    s.append(_yazi(150, 156, "n", 14, "#333", kalin=True))
    rr = np.random.default_rng(2)
    for _ in range(9):
        a = rr.uniform(0, 2 * math.pi); d = rr.uniform(40, 62)
        s.append(_mitokondri(150 + d * math.cos(a), 150 + d * math.sin(a), rx=11, ry=6, don=int(rr.uniform(0, 180))))
    s.append(_yazi(150, 250, "Yumurta (♀): bol sitoplazma", 13, "#C0504D", kalin=True))
    s.append(_yazi(150, 267, "ve çok sayıda mitokondri", 13, "#C0504D", kalin=True))
    # sperm
    s.append(_sperm(300, 150, "#2B5DA8"))
    s.append(f'<ellipse cx="300" cy="150" rx="12" ry="8" fill="#2B5DA8"/>')
    s.append(_yazi(310, 190, "Sperm (♂): yalnızca", 13, "#2B5DA8", kalin=True))
    s.append(_yazi(310, 207, "çekirdek DNA'sı aktarır", 13, "#2B5DA8", kalin=True))
    s.append(_ok(360, 150, 440, 150))
    # zigot
    s.append('<circle cx="560" cy="150" r="80" fill="#FFF0D9" stroke="#B9935A" stroke-width="2.5"/>')
    s.append(_cekirdek(560, 150, 30))
    s.append(_yazi(560, 156, "2n", 14, "#333", kalin=True))
    for _ in range(9):
        a = rr.uniform(0, 2 * math.pi); d = rr.uniform(42, 62)
        s.append(_mitokondri(560 + d * math.cos(a), 150 + d * math.sin(a), rx=11, ry=6, don=int(rr.uniform(0, 180))))
    s.append(_yazi(560, 250, "Zigot: çekirdek DNA'sı anne + baba,", 13, "#333", kalin=True))
    s.append(_yazi(560, 267, "mitokondriler (hemen hepsi) ANNEDEN", 13, "#C0504D", kalin=True))
    s.append(_yazi(W / 2, 305, "Bu yüzden organel genleriyle belirlenen özellikler Mendel oranlarına uymaz; yavru annenin özelliğini gösterir.", 12, "#555"))
    s.append("</svg>")
    return "".join(s)


def svg_kavram_haritasi():
    """Kromozom → lokus → gen → allel ilişkisi (adres benzetmesi)."""
    W, H = 760, 280
    s = [svg_ac(W, H, 800)]
    kutular = [("KROMOZOM", ("DNA + protein", "paketi"), "bir sokak", "#5A7FB8"),
               ("LOKUS", ("genin kromozom", "üzerindeki yeri"), "ev numarası (adres)", "#8E5BB5"),
               ("GEN", ("bir özelliği belirleyen", "DNA bölümü"), "o adresteki ev", "#3C9A5F"),
               ("ALLEL", ("aynı genin", "farklı biçimleri"), "evin farklı renkleri", "#E8A33B")]
    for i, (b, t, benz, renk) in enumerate(kutular):
        x = 20 + i * 188
        s.append(f'<rect x="{x}" y="40" width="168" height="120" rx="14" fill="{renk}" opacity="0.15" stroke="{renk}" stroke-width="2"/>')
        s.append(_yazi(x + 84, 72, b, 17, renk, kalin=True))
        s.append(_yazi(x + 84, 98, t[0], 12, "#222"))
        s.append(_yazi(x + 84, 114, t[1], 12, "#222"))
        s.append(_yazi(x + 84, 145, f"≈ {benz}", 12, "#555"))
        if i < 3:
            s.append(_ok(x + 170, 100, x + 186, 100))
    # küçük sokak çizimi
    s.append('<rect x="40" y="190" width="680" height="34" rx="17" fill="#DDE5F2" stroke="#5A7FB8"/>')
    for i, (no, renk) in enumerate([(5, "#9DB4D8"), (12, B_B), (18, "#9DB4D8"), (27, B_A), (33, "#9DB4D8")]):
        x = 90 + i * 140
        s.append(f'<rect x="{x - 20}" y="194" width="40" height="26" rx="4" fill="{renk}" stroke="#333"/>')
        s.append(_yazi(x, 236 + 16, f"lokus {no}", 11, "#333"))
    s.append(_yazi(W / 2, 182, "Kromozom üzerinde genler belirli adreslerde (lokuslarda) sıralanır", 13, "#1F3F73", kalin=True))
    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------------------
# Transkripsiyon ve translasyon (adım adım)
# ---------------------------------------------------------------------------
KOD_GEN = "ATGGCATTCAAAGGCTGA"          # kodlayan zincir (5'→3'): Met-Ala-Phe-Lys-Gly-DUR
PROMOTOR, SONLANDIRICI = "TATA", "AATT"
_TAM_RNA = {"A": "U", "T": "A", "G": "C", "C": "G"}


def _baz_kutu(x, y, b, w=22, h=22, ince=False):
    return (f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w}" height="{h}" rx="4" '
            f'fill="{BAZ_RENK.get(b, "#ddd")}" stroke="#333" stroke-width="{0.8 if ince else 1}"/>'
            + _yazi(x, y + 5, b, 13, "#111", kalin=True))


def svg_transkripsiyon(k):
    """k: RNA polimerazın okuduğu baz sayısı (0 = başlama, len = bitiş)."""
    kod = PROMOTOR + KOD_GEN + SONLANDIRICI
    kalip = "".join(TAMAMLAYICI[b] for b in kod)
    n_p, n_g = len(PROMOTOR), len(KOD_GEN)
    adim = 27
    x0 = 60
    W, H = x0 * 2 + adim * len(kod), 360
    s = [svg_ac(W, H, 820)]
    bitti = k >= n_g
    poz = n_p + min(k, n_g)                       # polimerazın bulunduğu baz indeksi
    acik = set(range(poz - 6, poz + 2)) if not bitti else set()
    if k == 0:
        acik = set(range(n_p - 1, n_p + 3))
    ust_y, alt_y, ust_ac, alt_ac = 120, 150, 88, 206
    # bölge etiketleri
    s.append(f'<rect x="{x0 - adim / 2}" y="58" width="{adim * n_p}" height="14" rx="4" fill="#C9D6EA"/>')
    s.append(_yazi(x0 - adim / 2 + adim * n_p / 2, 69, "promotor", 11, "#1F3F73", kalin=True))
    s.append(f'<rect x="{x0 - adim / 2 + adim * n_p}" y="58" width="{adim * n_g}" height="14" rx="4" fill="#D8EBD8"/>')
    s.append(_yazi(x0 - adim / 2 + adim * (n_p + n_g / 2), 69, "GEN (kodlanan bölge)", 11, "#2E6B3A", kalin=True))
    s.append(f'<rect x="{x0 - adim / 2 + adim * (n_p + n_g)}" y="58" width="{adim * len(SONLANDIRICI)}" height="14" rx="4" fill="#F1D5D5"/>')
    s.append(_yazi(x0 - adim / 2 + adim * (n_p + n_g + len(SONLANDIRICI) / 2), 69, "sonlandırıcı", 11, "#8A2E2E", kalin=True))
    s.append(_yazi(18, ust_y + 5, "5′", 13, "#B5651D", kalin=True))
    s.append(_yazi(18, alt_y + 5, "3′", 13, "#B5651D", kalin=True))
    s.append(_yazi(W - 18, ust_y + 5, "3′", 13, "#B5651D", kalin=True))
    s.append(_yazi(W - 18, alt_y + 5, "5′", 13, "#B5651D", kalin=True))
    for i, (b1, b2) in enumerate(zip(kod, kalip)):
        x = x0 + i * adim
        y1, y2 = (ust_ac, alt_ac) if i in acik else (ust_y, alt_y)
        s.append(_baz_kutu(x, y1, b1, ince=True))
        s.append(_baz_kutu(x, y2, b2, ince=True))
        if i not in acik:
            s.append(f'<line x1="{x}" y1="{y1 + 11}" x2="{x}" y2="{y2 - 11}" stroke="#D9534F" stroke-width="1.2"/>')
    # eşleşen mRNA (kabarcık içinde)
    yapilan = min(k, n_g)
    for j in range(yapilan):
        i = n_p + j
        if i in acik:
            x = x0 + i * adim
            s.append(_baz_kutu(x, alt_ac - 30, _TAM_RNA[kalip[i]].replace("U", "U"), w=20, h=20))
    # polimeraz
    if not bitti:
        px = max(x0 + (poz - 2) * adim, x0 + 3.5 * adim)
        s.append(f'<ellipse cx="{px}" cy="{(ust_ac + alt_ac) / 2}" rx="{adim * 4.4}" ry="78" fill="#8E5BB5" opacity="0.18" stroke="#8E5BB5" stroke-width="2"/>')
        s.append(_yazi(px, 36, "RNA polimeraz", 13, "#6E3C88", kalin=True))
        s.append(_ok(px + adim * 3.2, 36, px + adim * 5, 36, "#6E3C88"))
    else:
        s.append(_yazi(W / 2, 36, "RNA polimeraz DNA'dan ayrıldı, DNA yeniden kapandı", 13, "#6E3C88", kalin=True))
    # oluşan mRNA satırı
    mrna = "".join(_TAM_RNA[b] for b in kalip[n_p:n_p + yapilan])
    s.append(_yazi(x0 - 20, 266, "Oluşan mRNA:", 13, "#333", "start", True))
    s.append(_yazi(x0 - 20, 300, "5′", 13, "#B5651D", kalin=True))
    for j, b in enumerate(mrna):
        s.append(_baz_kutu(x0 + 10 + j * 24, 296, b, w=21, h=21))
    if mrna:
        s.append(_yazi(x0 + 10 + len(mrna) * 24 + 4, 300, "3′", 13, "#B5651D", "start", True))
    s.append(_yazi(W / 2, H - 12, "Kalıp zincir (alt) 3′→5′ okunur, mRNA 5′→3′ yönünde uzar. DNA'daki T'nin yerine RNA'da U gelir.", 12, "#555"))
    s.append("</svg>")
    return "".join(s)


def _trna(x, y_ust, antikodon, aa_kisa, renk="#76B7B2"):
    """tRNA: üstte amino asit, altta antikodon (y_ust: amino asidin y'si)."""
    s = (f'<path d="M{x - 26},{y_ust + 20} L{x + 26},{y_ust + 20} L{x + 18},{y_ust + 70} '
         f'L{x - 18},{y_ust + 70} Z" fill="{renk}" stroke="#2F6F6A" stroke-width="1.5" opacity="0.9"/>')
    for j, b in enumerate(antikodon):
        s += _baz_kutu(x - 20 + j * 20, y_ust + 82, b, w=18, h=18)
    if aa_kisa:
        s += (f'<circle cx="{x}" cy="{y_ust}" r="17" fill="#8E5BB5" stroke="#4B2C63"/>'
              + _yazi(x, y_ust + 5, aa_kisa, 11, "white", kalin=True))
    return s


def svg_translasyon(adim, mrna=None):
    """adim: 0 = başlama; 1..m = uzama (m: DUR kodonu A bölgesinde); m+1 = bitiş."""
    if mrna is None:
        mrna = KOD_GEN.replace("T", "U")
    kod = [mrna[i:i + 3] for i in range(0, len(mrna) - 2, 3)]
    aa = [GENETIK_KOD[c] for c in kod]
    dur = aa.index("*") if "*" in aa else len(aa)
    W, H = 820, 380
    s = [svg_ac(W, H, 860)]
    kw, gap, x0, my = 66, 6, 70, 270
    def kx(i):
        return x0 + i * (kw + gap) + kw / 2
    s.append(_yazi(x0 - 40, my + 5, "5′", 13, "#B5651D", kalin=True))
    s.append(_yazi(kx(len(kod) - 1) + kw / 2 + 18, my + 5, "3′", 13, "#B5651D", kalin=True))
    for i, c in enumerate(kod):
        for j, b in enumerate(c):
            s.append(_baz_kutu(kx(i) - 21 + j * 21, my, b, w=19, h=20, ince=True))
        etiket = "DUR" if aa[i] == "*" else AA_AD[aa[i]][0]
        s.append(_yazi(kx(i), my + 30, etiket, 11, "#666"))
    s.append(_yazi(x0 - 40, my - 22, "mRNA", 12, "#2F6F6A", "start", True))
    if adim > dur:      # bitiş
        zincir = [AA_AD[a][0] for a in aa[:dur]]
        for i, a in enumerate(zincir):
            cx = 200 + i * 40
            s.append(f'<circle cx="{cx}" cy="70" r="17" fill="#8E5BB5" stroke="#4B2C63"/>' + _yazi(cx, 75, a, 11, "white", kalin=True))
            if i:
                s.append(f'<line x1="{cx - 23}" y1="70" x2="{cx - 17}" y2="70" stroke="#4B2C63" stroke-width="3"/>')
        s.append(_yazi(200 + len(zincir) * 20 - 20, 110, "Protein serbest kaldı", 14, "#4B2C63", kalin=True))
        s.append(f'<ellipse cx="{kx(dur)}" cy="{my + 62}" rx="70" ry="22" fill="#E8C9A0" stroke="#A0703C" stroke-width="2"/>')
        s.append(f'<ellipse cx="{kx(dur) + 120}" cy="160" rx="85" ry="38" fill="#E8C9A0" stroke="#A0703C" stroke-width="2"/>')
        s.append(_yazi(kx(dur) + 120, 165, "ribozom alt birimleri ayrıldı", 11, "#5B3A17", kalin=True))
        s.append("</svg>")
        return "".join(s)
    p = max(adim - 1, 0)          # P bölgesindeki kodon indeksi
    a_i = p + 1 if adim > 0 else None
    rx = (kx(p) + kx(p + 1)) / 2 if adim > 0 else kx(0) + 20
    # ribozom
    if adim > 0:
        s.append(f'<ellipse cx="{rx}" cy="{my - 100}" rx="110" ry="70" fill="#E8C9A0" stroke="#A0703C" stroke-width="2" opacity="0.85"/>')
        s.append(_yazi(rx - 45, my - 150, "P", 15, "#5B3A17", kalin=True))
        s.append(_yazi(rx + 45, my - 150, "A", 15, "#5B3A17", kalin=True))
        s.append(_yazi(rx, my - 175, "büyük alt birim", 11, "#5B3A17"))
    s.append(f'<ellipse cx="{rx}" cy="{my + 62}" rx="100" ry="22" fill="#E8C9A0" stroke="#A0703C" stroke-width="2" opacity="0.9"/>')
    s.append(_yazi(rx, my + 67, "küçük alt birim", 11, "#5B3A17"))
    # P bölgesindeki tRNA ve peptit zinciri
    anti = "".join(_TAM_RNA_ANTI[b] for b in kod[p])
    if adim <= 1:
        s.append(_trna(kx(p), my - 120, anti, AA_AD[aa[p]][0]))
    else:
        s.append(_trna(kx(p), my - 120, anti, None))
        zincir = [AA_AD[a][0] for a in aa[:p + 1]]
        for i, a in enumerate(reversed(zincir)):
            cx, cy = kx(p) - i * 30, my - 120 - i * 26
            s.append(f'<circle cx="{cx}" cy="{cy}" r="16" fill="#8E5BB5" stroke="#4B2C63"/>' + _yazi(cx, cy + 5, a, 10, "white", kalin=True))
    # A bölgesi
    if a_i is not None and a_i < len(kod):
        if aa[a_i] == "*":
            s.append(f'<rect x="{kx(a_i) - 34}" y="{my - 120}" width="68" height="82" rx="10" fill="#F1D5D5" stroke="#8A2E2E" stroke-width="2"/>')
            s.append(_yazi(kx(a_i), my - 90, "serbest", 11, "#8A2E2E", kalin=True))
            s.append(_yazi(kx(a_i), my - 76, "bırakma", 11, "#8A2E2E", kalin=True))
            s.append(_yazi(kx(a_i), my - 62, "faktörü", 11, "#8A2E2E", kalin=True))
        else:
            anti2 = "".join(_TAM_RNA_ANTI[b] for b in kod[a_i])
            s.append(_trna(kx(a_i), my - 120, anti2, AA_AD[aa[a_i]][0], renk="#A7D3CF"))
            if adim >= 1:
                s.append(_yazi((kx(p) + kx(a_i)) / 2, my - 168, "peptit bağı", 11, "#D9534F", kalin=True))
                s.append(f'<path d="M{kx(a_i) - 18},{my - 128} Q{(kx(p) + kx(a_i)) / 2},{my - 160} {kx(p) + 14},{my - 132}" fill="none" stroke="#D9534F" stroke-width="2" stroke-dasharray="5 3" marker-end="url(#okucu)"/>')
    s.append("</svg>")
    return "".join(s)


_TAM_RNA_ANTI = {"A": "U", "U": "A", "G": "C", "C": "G"}


# ===========================================================================
# VERİ: tarihçe, kromozom sayıları, genetik kod, terimler
# ===========================================================================
TARIHCE = [
    (1665, "Robert Hooke", "Mantar dokusunda gördüğü boşluklara 'hücre' adını verdi.", "Hücre"),
    (1838, "Matthias Schleiden", "Bitkilerin hücrelerden oluştuğunu ileri sürdü.", "Hücre"),
    (1839, "Theodor Schwann", "Hayvanların da hücrelerden oluştuğunu gösterdi; hücre teorisi kuruldu.", "Hücre"),
    (1859, "Charles Darwin", "'Türlerin Kökeni' kitabını yayımladı (doğal seçilim).", "Evrim"),
    (1865, "Gregor Mendel", "Bezelye deneylerinin sonuçlarını sundu: ayrılma ve bağımsız dağılım "
                            "ilkeleri (yayın 1866).", "Kalıtım"),
    (1869, "Friedrich Miescher", "Hücre çekirdeğinden 'nüklein' adını verdiği maddeyi (DNA) ayırdı.", "Molekül"),
    (1869, "Francis Galton", "'Hereditary Genius' kitabıyla kalıtımın özellikler üzerindeki etkisini "
                             "tartıştı.", "Kalıtım"),
    (1900, "de Vries, Correns, Tschermak", "Mendel'in kurallarını birbirinden bağımsız olarak yeniden "
                                           "keşfettiler.", "Kalıtım"),
    (1902, "Archibald Garrod", "İlk kalıtsal metabolizma hastalığını (alkaptonüri) tanımladı.", "Kalıtım"),
    (1902, "Walter Sutton, Theodor Boveri", "Kromozom kalıtım teorisi: genler kromozomlar "
                                            "üzerindedir.", "Kromozom"),
    (1908, "G. H. Hardy, Wilhelm Weinberg", "Hardy-Weinberg ilkesini formüle ettiler.", "Popülasyon"),
    (1910, "Thomas Hunt Morgan", "Sirke sineğinde X'e bağlı kalıtımı gösterdi; genlerin kromozom "
                                 "üzerinde olduğunu kanıtladı.", "Kromozom"),
    (1913, "Alfred H. Sturtevant", "İlk genetik haritayı yaptı.", "Kromozom"),
    (1927, "Hermann J. Muller", "X ışınlarıyla yapay mutasyon oluşturdu.", "Mutasyon"),
    (1931, "Harriet Creighton, Barbara McClintock", "Krossing-overın fiziksel (kromozomal) "
                                                    "kanıtını gösterdiler.", "Kromozom"),
    (1941, "George Beadle, Edward Tatum", "'Bir gen – bir enzim' hipotezini kurdular.", "Molekül"),
    (1944, "Avery, MacLeod, McCarty", "Kalıtım materyalinin DNA olduğunu gösterdiler.", "Molekül"),
    (1953, "Watson, Crick (Franklin ve Wilkins'in verileriyle)", "DNA'nın çift sarmal yapısını "
                                                               "ortaya koydular.", "Molekül"),
    (1958, "Matthew Meselson, Franklin Stahl", "DNA replikasyonunun yarı korunumlu olduğunu "
                                               "kanıtladılar.", "Molekül"),
    (1961, "Brenner, Jacob, Meselson", "Mesajcı RNA'yı (mRNA) tanımladılar.", "Molekül"),
    (1966, "Marshall Nirenberg, Har Gobind Khorana", "Genetik kodun çözümü tamamlandı.", "Molekül"),
    (1972, "Paul Berg", "Hücre dışında (in vitro) ilk rekombinant DNA'yı oluşturdu.", "Biyoteknoloji"),
    (1973, "Herbert Boyer, Stanley Cohen", "Plazmitleri DNA klonlamada ilk kez kullandılar.", "Biyoteknoloji"),
    (1976, "Genentech", "İlk genetik mühendisliği şirketi kuruldu (Herbert Boyer).", "Biyoteknoloji"),
    (1977, "Frederick Sanger; Maxam ve Gilbert", "DNA dizileme yöntemleri geliştirildi; Sanger ilk "
                                                 "virüs genomunu (φX174) diziledi.", "Molekül"),
    (1977, "Phillip Sharp, Richard Roberts", "Genlerde intronları keşfettiler.", "Molekül"),
    (1978, "Genentech", "İnsan insülin geni bakteride klonlandı / ifade edildi.", "Biyoteknoloji"),
    (1980, "David Botstein ve ark.", "RFLP (restriksiyon parça uzunluğu polimorfizmi) yöntemini "
                                     "genetik haritalamaya önerdiler.", "Biyoteknoloji"),
    (1983, "Kary Mullis", "Polimeraz zincir reaksiyonunu (PZR/PCR) buldu.", "Biyoteknoloji"),
    (1984, "Alec Jeffreys", "Genetik (DNA) parmak izi yöntemini geliştirdi; ilk adli kullanımı "
                            "İngiltere'deki Colin Pitchfork davasıdır.", "Biyoteknoloji"),
    (1990, "İnsan Genom Projesi", "İnsan genomunun tamamını dizilemek için uluslararası proje "
                                  "başladı.", "Genom"),
    (1990, "W. French Anderson ve ark.", "İlk onaylı gen tedavisi (ADA eksikliğine bağlı ağır "
                                         "bağışıklık yetmezliği) uygulandı.", "Biyoteknoloji"),
    (1993, "Huntington Hastalığı Araştırma Grubu", "Huntington hastalığı geni belirlendi.", "Genom"),
    (1995, "Craig Venter ve ark.", "Bir bakterinin (Haemophilus influenzae) tüm genomu ilk kez "
                                   "dizilendi.", "Genom"),
    (1996, "Uluslararası konsorsiyum", "Ekmek mayasının (Saccharomyces cerevisiae) genomu "
                                       "tamamlandı.", "Genom"),
    (1997, "Ian Wilmut ve ark.", "Ergin hücreden klonlanan ilk memeli, koyun Dolly duyuruldu "
                                 "(doğumu 1996).", "Biyoteknoloji"),
    (2001, "İnsan Genom Projesi ve Celera", "İnsan genomunun taslak dizisi yayımlandı.", "Genom"),
    (2003, "İnsan Genom Projesi", "İnsan genomu dizileme projesi tamamlandı.", "Genom"),
    (2007, "Craig Venter", "Kendi diploit genomunun tam dizisini yayımladı.", "Genom"),
]

TURLER = {  # 2n
    "İnsan": 46, "Sığır": 60, "Koyun": 54, "Keçi": 60, "At": 64, "Tavuk": 78,
    "Bal arısı (dişi)": 32, "Asma (Vitis vinifera)": 38, "Zeytin": 46, "Hünnap": 24,
    "Bezelye": 14, "Domates": 24, "Mısır": 20, "Ekmeklik buğday (heksaploit)": 42,
    "Sirke sineği": 8,
}

_AA_DIZI = "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
GENETIK_KOD = {}
_i = 0
for _b1 in "UCAG":
    for _b2 in "UCAG":
        for _b3 in "UCAG":
            GENETIK_KOD[_b1 + _b2 + _b3] = _AA_DIZI[_i]
            _i += 1
AA_AD = {"F": ("Phe", "Fenilalanin"), "L": ("Leu", "Lösin"), "I": ("Ile", "İzolösin"),
         "M": ("Met", "Metiyonin"), "V": ("Val", "Valin"), "S": ("Ser", "Serin"),
         "P": ("Pro", "Prolin"), "T": ("Thr", "Treonin"), "A": ("Ala", "Alanin"),
         "Y": ("Tyr", "Tirozin"), "H": ("His", "Histidin"), "Q": ("Gln", "Glutamin"),
         "N": ("Asn", "Asparajin"), "K": ("Lys", "Lizin"), "D": ("Asp", "Aspartik asit"),
         "E": ("Glu", "Glutamik asit"), "C": ("Cys", "Sistein"), "W": ("Trp", "Triptofan"),
         "R": ("Arg", "Arjinin"), "G": ("Gly", "Glisin"), "*": ("DUR", "Durdurma kodonu")}

TERIMLER = [
    ("Genetik", "Kalıtsal özelliklerin dölden döle nasıl geçtiğini, genlerin yapısını ve işlevini "
                "inceleyen bilim dalı (kalıtım bilimi)."),
    ("Kalıtım", "Canlıların özelliklerinin ebeveynlerden (P) yavrulara (F) gametler aracılığıyla "
                "aktarılması."),
    ("Gen", "Bir özelliğin kalıtımını sağlayan, belirli bir ürünü (protein ya da RNA) kodlayan "
            "DNA bölümü."),
    ("Lokus", "Bir genin kromozom üzerindeki yeri (adresi). Çoğulu: lokuslar."),
    ("Allel", "Aynı genin, homolog kromozomların aynı lokusunda bulunan farklı biçimleri "
              "(ör. A ve a)."),
    ("Genotip", "Bir canlının taşıdığı genlerin (allellerin) bileşimi; sembolle gösterilir "
                "(ör. AA, Aa, aa)."),
    ("Fenotip", "Bir canlının gözlemlenebilir ve ölçülebilir özellikleri: morfolojik, fizyolojik, "
                "biyokimyasal ya da davranışsal olabilir. Genotip ve çevrenin ortak ürünüdür: "
                "Fenotip = Genotip + Çevre."),
    ("Karakter", "Canlıda kalıtım ve çevrenin etkisiyle ortaya çıkan özellik (göz rengi, kan "
                 "grubu, süt verimi...)."),
    ("Dominant (baskın) allel", "Heterozigot durumda da etkisini gösteren allel; büyük harfle "
                                "gösterilir (A)."),
    ("Resesif (çekinik) allel", "Etkisini ancak homozigot (aa) olduğunda gösteren allel; küçük "
                                "harfle gösterilir (a). F1'de saklanır, F2'de yeniden ortaya çıkar."),
    ("Homozigot (arı döl)", "Bir lokustaki iki allelin aynı olması (AA ya da aa)."),
    ("Heterozigot (melez)", "Bir lokustaki iki allelin farklı olması (Aa)."),
    ("Gamet", "Olgunlaşmış eşey hücresi (sperm, yumurta, polen); haploittir (n)."),
    ("Zigot", "Sperm ve yumurtanın birleşmesiyle (döllenme) oluşan diploit (2n) hücre."),
    ("Mutasyon", "Genetik materyalde (DNA dizisinde) meydana gelen kalıtsal değişiklik; değişikliği "
                 "taşıyan bireye mutant denir."),
    ("Modifikasyon", "Çevre etkisiyle oluşan, genlerde değişiklik yapmayan ve kalıtsal OLMAYAN "
                     "değişim."),
    ("Rekombinasyon", "Kalıtım materyalinin yeniden düzenlenmesi; yeni allel kombinasyonlarının "
                      "oluşması (ör. krossing-over ile)."),
    ("Krossing-over", "Mayoz I profazında homolog kromozomların kromatitleri arasında parça "
                      "değişimi."),
    ("Kiazma", "Krossing-over sırasında homolog kromatitlerin çaprazlaştığı (bağlandığı) nokta."),
    ("Sinaps", "Mayoz I profazında homolog kromozomların boylu boyunca eşleşmesi."),
    ("Tetrad (bivalent)", "Eşleşmiş bir homolog çift; toplam 4 kromatit içerir."),
    ("Homolog kromozom", "Biri anneden biri babadan gelen, aynı genleri aynı sırayla taşıyan "
                         "kromozom çifti."),
    ("Kardeş kromatit", "DNA eşlendikten sonra sentromerden birbirine bağlı duran iki özdeş "
                        "kopya."),
    ("Sentromer", "Kardeş kromatitlerin birleştiği, iğ ipliklerinin (kinetokor aracılığıyla) "
                  "bağlandığı boğum bölgesi."),
    ("Telomer", "Kromozomların uçlarındaki, kromozomu koruyan özel tekrar dizileri."),
    ("Diploit (2n)", "Her kromozomdan iki takım (homolog çift) taşıyan hücre ya da canlı."),
    ("Haploit (n)", "Her kromozomdan tek takım taşıyan hücre (ör. gamet)."),
    ("Otozom", "Cinsiyetin belirlenmesinde rol almayan kromozomlar (insanda 22 çift)."),
    ("Gonozom (eşey kromozomu)", "Cinsiyeti belirleyen kromozomlar (memelilerde X ve Y, kuşlarda "
                                 "Z ve W)."),
    ("Karyotip", "Bir türün kromozomlarının sayı, büyüklük ve şekil bakımından düzenli dizilmiş "
                 "görünümü."),
    ("Varyasyon", "Ortak atadan gelen bireyler arasındaki farklılıklar; genotip ve çevreden "
                  "kaynaklanır."),
    ("Seleksiyon", "Belirli genotiplerin daha fazla yavru bırakması (doğal) ya da insan eliyle "
                   "seçilmesi (yapay)."),
    ("Kalitatif karakter", "Kesin sınıflara ayrılabilen, az sayıda genle kontrol edilen, çevreden "
                           "az etkilenen özellik (renk, kan grubu, boynuzluluk)."),
    ("Kantitatif karakter", "Ölçülerek ifade edilen, çok sayıda gen (poligenik) ve çevreden "
                            "etkilenen, sürekli dağılım gösteren özellik (süt, yumurta verimi)."),
    ("Poligenik kalıtım", "Bir özelliğin birçok genin küçük ve toplanabilir etkileriyle "
                          "belirlenmesi."),
    ("Mitoz", "Vücut (somatik) hücrelerinde görülen, genetik olarak özdeş iki hücre oluşturan "
              "bölünme."),
    ("Mayoz", "Eşey ana hücrelerinde görülen, kromozom sayısını yarıya indirerek 4 haploit hücre "
              "oluşturan bölünme."),
    ("Sitokinez", "Sitoplazmanın bölünmesi; hayvanda boğumlanma, bitkide hücre plağı ile olur."),
    ("İnterfaz", "Hücrenin iki bölünme arasındaki büyüme ve hazırlık dönemi (G1, S, G2)."),
    ("Replikasyon", "DNA'nın kendini eşlemesi (yarı korunumlu)."),
    ("Transkripsiyon", "DNA'daki bilginin mRNA'ya kopyalanması (çekirdekte)."),
    ("Translasyon", "mRNA'daki bilgiye göre ribozomda protein sentezlenmesi."),
    ("Kodon", "mRNA üzerinde bir amino asidi (ya da durdurmayı) belirleyen üçlü baz dizisi."),
    ("Antikodon", "tRNA üzerinde, mRNA kodonuna tamamlayıcı üçlü baz dizisi."),
    ("Nükleotit", "Nükleik asitlerin yapı birimi: fosfat + şeker + azotlu baz."),
    ("Nükleozit", "Şeker + azotlu baz (fosfat yok)."),
    ("Pürin", "Çift halkalı azotlu bazlar: adenin (A) ve guanin (G)."),
    ("Pirimidin", "Tek halkalı azotlu bazlar: sitozin (C), timin (T, yalnız DNA), urasil (U, "
                  "yalnız RNA)."),
    ("Sentral dogma", "Genetik bilginin akış yönü: DNA → RNA → Protein."),
    ("Spermatogenez", "Testiste sperm oluşumu; her birincil spermatositten 4 sperm."),
    ("Oogenez", "Yumurtalıkta yumurta oluşumu; her birincil oositten 1 yumurta + polar cisimler."),
    ("Polar cisim", "Oogenezde oluşan, sitoplazması çok az olan ve dejenere olan küçük hücre."),
    ("Fertilizasyon (döllenme)", "Sperm ve yumurta çekirdeklerinin birleşerek zigotu "
                                 "oluşturması."),
    ("Klon", "Genetik olarak birbirinin aynı olan bireyler ya da hücreler."),
    ("Genom", "Bir canlının (ya da bir hücrenin) taşıdığı genetik materyalin tamamı: çekirdek "
              "kromozomlarındaki DNA + mitokondri (bitkilerde ayrıca kloroplast) DNA'sı."),
    ("Ekstrakromozomal (sitoplazmik) kalıtım", "Çekirdek kromozomları dışındaki, mitokondri ve "
     "kloroplast DNA'sıyla olan kalıtım. Organeller yumurtanın sitoplazmasıyla geçtiği için "
     "genellikle anneden kalıtılır ve Mendel oranlarına uymaz."),
    ("Mitokondriyal DNA (mtDNA)", "Mitokondrinin kendi halkasal DNA'sı; genellikle anneden kalıtılır."),
    ("Çevre (Ç)", "Fenotipi etkileyen genetik olmayan bütün etkenler: besleme, bakım, iklim, "
                  "hastalık, sıcaklık…"),
    ("Genotip × çevre etkileşimi", "Çevrenin etkisinin genotipe göre değişmesi; aynı çevre "
                                   "değişikliğine farklı genotiplerin farklı tepki vermesi."),
    ("Promotor", "Genin önünde, RNA polimerazın bağlanıp transkripsiyonu başlattığı DNA bölgesi."),
    ("RNA polimeraz", "Kalıp DNA'yı okuyarak RNA yapan enzim."),
    ("Kalıp zincir", "Transkripsiyonda RNA polimerazın okuduğu DNA zinciri; mRNA bu zincire "
                     "tamamlayıcıdır."),
    ("Kodlayan zincir", "Kalıp olmayan DNA zinciri; dizisi mRNA ile aynıdır (T yerine U)."),
    ("mRNA", "Mesajcı RNA; genin bilgisini çekirdekten ribozoma taşır."),
    ("tRNA", "Taşıyıcı RNA; antikodonuyla kodonu tanır, amino asidi ribozoma getirir."),
    ("Ribozom", "rRNA ve proteinden oluşan, iki alt birimli protein sentez yapısı; P ve A bölgeleri vardır."),
    ("Peptit bağı", "İki amino asit arasında kurulan bağ; ribozomda oluşturulur."),
    ("İntron", "Ökaryot genlerinde, ön-mRNA'dan kesilip çıkarılan kodlamayan parça."),
    ("Ekzon", "Olgun mRNA'da kalan, birleştirilen kodlayan parça."),
    ("Durdurma kodonu", "Translasyonu bitiren kodon: UAA, UAG, UGA. Bunlara uyan tRNA yoktur."),
]

SEMBOLLER = [("P", "Parental (ebeveyn, ata) döl"), ("F1, F2, … Fn", "Filial (yavru, oğul) döller"),
             ("×", "Çaprazlama, tozlaşma, çiftleşme"), ("♀", "Dişi"), ("♂", "Erkek"),
             ("G", "Gametler"), ("2n", "Diploit kromozom sayısı"), ("n", "Haploit kromozom sayısı")]


# ===========================================================================
# SORU ÜRETİCİLERİ (her biri 10 soru)
# ===========================================================================
def _secim(r, metin, dogru, yanlis, cozum):
    temiz = [y for y in dict.fromkeys(yanlis) if y != dogru][:3]
    return soru_secim(r, metin, dogru, temiz, [_md(c) if isinstance(c, str) else c for c in cozum])


def _tamamla(r, sabit, havuz):
    """sabit sorular + havuzdan rastgele seçilenlerle 10'a tamamlar, sırayı karıştırır."""
    gerek = SORU_SAYISI - len(sabit)
    secilen = _kavram_sec(r, havuz, min(gerek, len(havuz)))
    hepsi = sabit + secilen
    sira = r.permutation(len(hepsi))
    return [hepsi[i] for i in sira]


def _tur_sec(r, haric=()):
    adlar = [t for t in TURLER if t not in haric]
    t = adlar[int(r.integers(0, len(adlar)))]
    return t, TURLER[t]


# ---------------------------------------------------------------------------
_FENOTIP_ORNEK = {
    "Morfolojik": ["bezelyede tohum rengi", "sığırda boynuzlu/boynuzsuz olma", "koyunda yapağı rengi",
                   "asmada yaprak biçimi", "tavukta ibik şekli", "bitki boyu"],
    "Fizyolojik": ["ineğin süt verimi", "tavuğun yumurta verimi", "buzağının günlük canlı ağırlık artışı",
                   "bitkinin kuraklığa dayanıklılığı", "soğuğa dayanıklılık", "yemden yararlanma"],
    "Biyokimyasal": ["insanda ABO kan grubu", "sütte kazein tipi (A1/A2)", "üzümde antosiyanin miktarı",
                     "bir enzimin aktivitesi", "zeytinyağında oleik asit oranı", "hemoglobin tipi"],
    "Davranışsal": ["sığırda mizaç (uysallık)", "tavukta kuluçkaya yatma isteği", "koyunda annelik davranışı",
                    "arıda savunma (saldırganlık) davranışı", "köpekte çoban davranışı"],
}


def _fenotip_turu(r):
    tur = list(_FENOTIP_ORNEK)[int(r.integers(0, 4))]
    ornek = _FENOTIP_ORNEK[tur][int(r.integers(0, len(_FENOTIP_ORNEK[tur])))]
    return _secim(r, f"“{ornek.capitalize()}” hangi tür fenotiptir?", tur, [t for t in _FENOTIP_ORNEK if t != tur],
                  [f"{tur}: " + {"Morfolojik": "biçim ve yapı", "Fizyolojik": "vücudun işleyişi, verim",
                                 "Biyokimyasal": "molekül düzeyi, laboratuvarda ölçülür",
                                 "Davranışsal": "davranış ve mizaç"}[tur] + "."])


def gen_giris(r):
    g = int(r.integers(12, 40)) * 250
    c = int(r.choice([i for i in range(-12, 6) if i != 0])) * 250
    k = int(r.integers(2, 8))
    sabit = [
        soru_sayi(f"Bir ineğin genetik potansiyeli (G) {g} kg, çevrenin etkisi (Ç) {c:+d} kg ise "
                  "gözlenen süt verimi (fenotip) kaç kg olur?", g + c,
                  [_tx(rf"F = G + \text{{Ç}} = {g} + ({c}) = {g + c}"),
                   _md("Fenotip, genotip ile çevrenin ortak etkisidir.")],
                  yanlis=[g - c, g, g * 2 + c]),
        soru_sayi(f"Eklemeli etki gösteren, iki allelli {k} gen bir özelliği belirliyor. Kaç farklı "
                  "genotip sınıfı (fenotip değeri) oluşur?", 2 * k + 1,
                  [_md(f"{k} genin toplam {2 * k} alleli vardır. Bireyde 'büyük harf' allel sayısı "
                       f"0'dan {2 * k}'ye kadar olabilir:"),
                   _tx(rf"2k + 1 = 2\times{k} + 1 = {2 * k + 1}")],
                  yanlis=[2 * k, k + 1, 3 ** k]),
    ]
    havuz = [
        _secim(r, "Aşağıdakilerden hangisi KALITSAL bir değişimdir?", "Mutasyon",
               ["Modifikasyon", "İyi beslenen hayvanın iri olması", "Güneşte kalan derinin bronzlaşması"],
               ["Mutasyon DNA dizisinde olur ve yavrulara geçer. Diğerleri çevrenin etkisiyle "
                "oluşan, kalıtsal olmayan değişimlerdir (modifikasyon)."]),
        _secim(r, "Modifikasyon için hangisi doğrudur?", "Çevre etkisiyle oluşur, kalıtsal değildir",
               ["DNA dizisini değiştirir", "Yalnızca gametlerde görülür", "Krossing-over ile oluşur"],
               ["Modifikasyon genleri değiştirmez; yavrulara aktarılmaz."]),
        _secim(r, "Aşağıdakilerden hangisi KANTİTATİF (nicel) bir karakterdir?", "Süt verimi",
               ["Kan grubu", "Boynuzlu/boynuzsuz olma", "Bezelyede tohum rengi"],
               ["Süt verimi ölçülerek ifade edilir, çok gen ve çevreden etkilenir. Diğerleri kesin "
                "sınıflara ayrılan kalitatif karakterlerdir."]),
        _secim(r, "Aşağıdakilerden hangisi KALİTATİF (nitel) bir karakterdir?", "Kan grubu",
               ["Yumurta verimi", "Yapağı verimi", "Canlı ağırlık"],
               ["Kan grubu kesin sınıflara ayrılır ve çevreden etkilenmez."]),
        _secim(r, "Kantitatif karakterler için hangisi YANLIŞTIR?",
               "Çevreden hiç etkilenmezler",
               ["Çok sayıda gen tarafından etkilenirler", "Ölçülerek ifade edilirler",
                "Sürekli bir dağılım gösterirler"],
               ["Kantitatif karakterler hem genlerden hem çevreden etkilenir."]),
        _secim(r, "Fenotipi en doğru tanımlayan ifade hangisidir?",
               "Genotip ve çevrenin etkisiyle oluşan, gözlemlenebilir ve ölçülebilir özellikler",
               ["Yalnızca genlerin toplamı", "Yalnızca çevrenin etkisi", "Yalnızca gözle görülen dış görünüş"],
               ["F = G + Ç (+ G×Ç etkileşimi). Fenotip morfolojik, fizyolojik, biyokimyasal ya da davranışsal olabilir."]),
        _fenotip_turu(r),
        _secim(r, "Varyasyonun genetik kaynakları arasında hangisi YER ALMAZ?", "Modifikasyon",
               ["Mutasyon", "Rekombinasyon", "Seleksiyon"],
               ["Modifikasyon kalıtsal değildir; genetik varyasyon oluşturmaz."]),
        _secim(r, "Krossing-over hangi varyasyon kaynağına örnektir?", "Rekombinasyon",
               ["Mutasyon", "Modifikasyon", "Seleksiyon"],
               ["Homolog kromozomlar arasında parça değişimi yeni allel kombinasyonları "
                "oluşturur: rekombinasyon."]),
        _secim(r, "Genetik problemlerde 'P' ne anlama gelir?", "Ebeveyn (parental) döl",
               ["Yavru döl", "Gamet", "Popülasyon"], ["P: parental (ata) döl; F: filial (yavru) döl."]),
        _secim(r, "Genetik problemlerde 'F1' ne anlama gelir?", "Birinci yavru döl",
               ["Birinci ebeveyn", "Birinci gamet", "Birinci kromozom"], ["F: filial (yavru) döl."]),
        _secim(r, "Kalıtsal özellikler ebeveynden yavruya ne aracılığıyla geçer?", "Gametler",
               ["Kan", "Sinir hücreleri", "Hormonlar"],
               ["Genler gametlerle (sperm ve yumurta; bitkide polen ve yumurta) aktarılır."]),
        _secim(r, "Hayvan yetiştiriciliği için en doğru ifade hangisidir?",
               "Genetik kuralları hayvanları ıslah etmek için uygular",
               ["Yalnızca hayvan hastalıklarını inceler", "Genetikle hiçbir ilişkisi yoktur",
                "Yalnızca yem bitkilerini inceler"],
               ["Hayvan genetiği ve hayvan yetiştiriciliği birbirinin ayrılmaz parçalarıdır."]),
        _secim(r, "Aynı çevre değişikliğine iki ırkın farklı tepki vermesine ne denir?",
               "Genotip × çevre etkileşimi", ["Mutasyon", "Krossing-over", "Seleksiyon"],
               ["Çevrenin etkisinin genotipe göre değişmesi G×Ç etkileşimidir."]),
        _secim(r, "Mendel kalıtım kurallarını hangi canlıyla çalışarak ortaya koydu?", "Bezelye",
               ["Sirke sineği", "Fare", "Mısır"], ["Gregor Mendel, 1865, bezelye deneyleri."]),
    ]
    return _tamamla(r, sabit, havuz + _EK["giris"](r))


# ---------------------------------------------------------------------------
def gen_tarih(r):
    olaylar = list(TARIHCE)
    idx = r.permutation(len(olaylar))
    sorular = []
    for j in idx:
        yil, kisi, olay, _ = olaylar[j]
        if len(sorular) >= SORU_SAYISI:
            break
        if len(sorular) % 2 == 0:
            yanlis_kisi = list(dict.fromkeys(o[1] for o in olaylar if o[1] != kisi))
            secilen = [yanlis_kisi[i] for i in r.permutation(len(yanlis_kisi))[:3]]
            sorular.append(_secim(r, f"“{olay}” Bu çalışma kime aittir?", kisi, secilen,
                                  [f"**{yil}** · **{kisi}**: {olay}"]))
        else:
            yillar = sorted({o[0] for o in olaylar if abs(o[0] - yil) >= 4})
            yakin = sorted(yillar, key=lambda y: abs(y - yil))[:6]
            secilen = [str(yakin[i]) for i in r.permutation(len(yakin))[:3]]
            sorular.append(_secim(r, f"{kisi}: “{olay}” Bu gelişme hangi yılda oldu?", str(yil),
                                  secilen, [f"**{yil}** · {kisi}"]))
    return sorular


# ---------------------------------------------------------------------------
def gen_hucre(r):
    havuz = []
    hepsi = list(ORGANELLER)
    for k, (ad, acik) in ORGANELLER.items():
        yanlis = [ORGANELLER[x][0] for x in hepsi if x != k]
        secilen = [yanlis[i] for i in r.permutation(len(yanlis))[:3]]
        ilk = acik.split(". ")[0].rstrip(".")
        havuz.append(_secim(r, f"“{ilk}.” Bu tanım hangi yapıya aittir?", ad, secilen,
                            [f"**{ad}:** {acik}"]))
    havuz += [
        _secim(r, "Aşağıdakilerden hangisi hayvan hücresinde BULUNMAZ?", "Kloroplast",
               ["Mitokondri", "Ribozom", "Golgi aygıtı"],
               ["Kloroplast yalnız bitki ve alg hücrelerinde bulunur."]),
        _secim(r, "Aşağıdakilerden hangisi bitki hücresinde BULUNMAZ?", "Sentriyol",
               ["Hücre çeperi", "Kloroplast", "Büyük merkezi koful"],
               ["Bitki hücrelerinde sentriyol yoktur; iğ iplikleri başka yollarla düzenlenir."]),
        _secim(r, "Bitki hücresinin depo karbonhidratı hangisidir?", "Nişasta",
               ["Glikojen", "Kitin", "Selüloz"],
               ["Bitkiler nişasta, hayvan ve mantarlar glikojen depolar. Selüloz çeperin yapı "
                "maddesidir."]),
        _secim(r, "Mantar hücresinin çeperi çoğunlukla hangi maddeden yapılmıştır?", "Kitin",
               ["Selüloz", "Nişasta", "Glikojen"], ["Bitki çeperi selüloz, mantar çeperi kitindir."]),
        _secim(r, "Kendine ait DNA'sı olan organel hangisidir?", "Mitokondri",
               ["Golgi aygıtı", "Lizozom", "Ribozom"],
               ["Mitokondri ve kloroplastın kendi DNA'ları vardır."]),
        _secim(r, "'Hücre' terimini ilk kez kim kullandı?", "Robert Hooke",
               ["Theodor Schwann", "Gregor Mendel", "Friedrich Miescher"],
               ["1665'te mantar dokusunda gördüğü boşluklara hücre dedi."]),
        _secim(r, "Hücre teorisine göre hangisi YANLIŞTIR?",
               "Hücreler cansız maddelerden kendiliğinden oluşur",
               ["Bütün canlılar hücrelerden oluşur", "Hücre canlının en küçük birimidir",
                "Hücreler önceki hücrelerin bölünmesiyle oluşur"],
               ["Hücreler yalnızca var olan hücrelerin bölünmesiyle oluşur."]),
        _secim(r, "Hücrenin genetik bilgisini taşıyan ve faaliyetlerini yöneten kısım hangisidir?",
               "Çekirdek", ["Hücre zarı", "Sitoplazma", "Koful"],
               ["Çekirdek DNA'yı taşır ve hücreyi yönetir."]),
    ]
    return _tamamla(r, [], havuz + _EK["hucre"](r))


# ---------------------------------------------------------------------------
def gen_kromozom(r):
    t1, n2 = _tur_sec(r, haric=("Ekmeklik buğday (heksaploit)",))
    t2, m2 = _tur_sec(r, haric=(t1, "Ekmeklik buğday (heksaploit)"))
    k = int(r.integers(2, 7))
    sabit = [
        soru_sayi(f"{t1} için 2n = {n2}. Bu türün gametlerinde kaç kromozom bulunur?", n2 // 2,
                  [_md("Gametler haploittir (n):"), _tx(rf"n = \frac{{2n}}{{2}} = \frac{{{n2}}}{{2}} = {n2 // 2}")],
                  yanlis=[n2, 2 * n2, n2 // 4 if n2 >= 8 else n2 + 2]),
        soru_sayi(f"{t2} gametlerinde n = {m2 // 2} kromozom vardır. Vücut hücrelerinde kaç "
                  "kromozom bulunur?", m2,
                  [_tx(rf"2n = 2\times{m2 // 2} = {m2}")], yanlis=[m2 // 2, 2 * m2, m2 + 1]),
        soru_sayi(f"{t1} (2n = {n2}) vücut hücresinde kaç homolog kromozom çifti vardır?", n2 // 2,
                  [_md("Her çift, biri anneden biri babadan gelen iki homologdan oluşur:"),
                   _tx(rf"\frac{{2n}}{{2}} = {n2 // 2}\ \text{{çift}}")],
                  yanlis=[n2, n2 - 1, n2 // 4 if n2 >= 8 else n2 + 2]),
        soru_sayi(f"2n = {2 * k} olan bir canlı, yalnızca bağımsız dağılımla (krossing-over olmadan) "
                  "kaç farklı gamet oluşturabilir?", 2 ** k,
                  [_tx(rf"2^n = 2^{{{k}}} = {2 ** k}"), _md(f"n = {k} homolog çift vardır.")],
                  yanlis=[2 * k, k ** 2, 2 ** (2 * k)]),
    ]
    havuz = [
        _secim(r, "Kardeş kromatitlerin birbirine bağlandığı bölgeye ne denir?", "Sentromer",
               ["Telomer", "Kiazma", "Lokus"], ["Sentromer: birincil boğum; iğ iplikleri buraya bağlanır."]),
        _secim(r, "Kromozomların uçlarındaki koruyucu bölgeye ne denir?", "Telomer",
               ["Sentromer", "Kinetokor", "Kromatit"], ["Telomer: uçtaki tekrar dizileri."]),
        _secim(r, "Kromozomun kısa koluna ne ad verilir?", "p kolu",
               ["q kolu", "Telomer", "Kinetokor"], ["p: kısa kol, q: uzun kol."]),
        _secim(r, "Sentromeri tam ortada olan kromozom hangisidir?", "Metasentrik",
               ["Akrosentrik", "Telosentrik", "Submetasentrik"],
               ["Metasentrik: kollar eşit; akrosentrik: sentromer uca çok yakın; telosentrik: uçta."]),
        _secim(r, "İnsanda kaç çift otozom vardır?", "22", ["23", "46", "44"],
               ["46 kromozom = 22 çift otozom + 1 çift eşey kromozomu."]),
        _secim(r, "İnsan erkeğinin eşey kromozomları hangisidir?", "XY", ["XX", "ZW", "ZZ"],
               ["Memelilerde dişi XX, erkek XY."]),
        _secim(r, "Homolog kromozomlar için hangisi doğrudur?",
               "Biri anneden biri babadan gelir; aynı genleri aynı sırayla taşır",
               ["İkisi de anneden gelir", "Birbirinin tamamen aynısıdır", "Yalnızca gametlerde bulunur"],
               ["Homologlar aynı lokusları taşır ama allelleri farklı olabilir."]),
        _secim(r, "Kromozomların sayı, büyüklük ve şekil bakımından düzenli dizilmiş görünümüne ne "
                  "denir?", "Karyotip", ["Genotip", "Fenotip", "Tetrad"], ["Karyotip, metafazdaki "
                                                                          "kromozomlardan hazırlanır."]),
        _secim(r, "Kromozom sayısı ile canlının gelişmişliği arasındaki ilişki için hangisi doğrudur?",
               "Bir ilişki yoktur", ["Kromozom sayısı arttıkça canlı gelişmiştir",
                                     "Bitkilerin kromozomu her zaman daha azdır",
                                     "Memeliler en çok kromozoma sahiptir"],
               ["Örnek: tavukta 2n = 78, insanda 2n = 46."]),
        _secim(r, "DNA ve proteinlerden oluşan, bölünmeyen hücrede gevşek hâldeki yapıya ne denir?",
               "Kromatin", ["Kromozom", "Çekirdekçik", "Sentrozom"],
               ["Bölünme sırasında kromatin yoğunlaşarak kromozomları oluşturur."]),
    ]
    return _tamamla(r, sabit, havuz + _EK["kromozom"](r))


# ---------------------------------------------------------------------------
def gen_dongu(r):
    g1 = int(r.integers(6, 13))
    s_ = int(r.integers(6, 9))
    g2 = int(r.integers(3, 5))
    m = 1
    sabit = [
        soru_sayi(f"Bir hücrede G1 = {g1} saat, S = {s_} saat, G2 = {g2} saat, M = {m} saat sürüyor. "
                  "İnterfaz kaç saattir?", g1 + s_ + g2,
                  [_tx(rf"\text{{İnterfaz}} = G1 + S + G2 = {g1} + {s_} + {g2} = {g1 + s_ + g2}"),
                   _md("M evresi interfaza dahil değildir.")],
                  yanlis=[g1 + s_ + g2 + m, g1 + s_, s_ + g2]),
        soru_sayi(f"Aynı hücrede (G1 = {g1}, S = {s_}, G2 = {g2}, M = {m} saat) hücre döngüsünün "
                  "yüzde kaçı interfazda geçer?", round(100 * (g1 + s_ + g2) / (g1 + s_ + g2 + m), 1),
                  [_tx(rf"\frac{{{g1 + s_ + g2}}}{{{g1 + s_ + g2 + m}}}\times 100 = "
                       rf"{100 * (g1 + s_ + g2) / (g1 + s_ + g2 + m):.1f}")],
                  yanlis=[round(100 * m / (g1 + s_ + g2 + m), 1), 50.0, round(100 * s_ / (g1 + s_ + g2 + m), 1)],
                  ondalik=1),
    ]
    havuz = [
        _secim(r, "DNA'nın eşlendiği (replikasyon) evre hangisidir?", "S", ["G1", "G2", "M"],
               ["S: sentez evresi."]),
        _secim(r, "Bölünmeyen hücrelerin döngüden çıkıp beklediği evre hangisidir?", "G0",
               ["G1", "S", "G2"], ["Örneğin sinir ve kas hücrelerinin çoğu G0'dadır."]),
        _secim(r, "Hücrenin büyüdüğü, organellerin çoğaldığı ve S evresine hazırlandığı evre "
                  "hangisidir?", "G1", ["G2", "M", "S"], ["G1: bölünmeden sonraki ilk büyüme evresi."]),
        _secim(r, "Hücre döngüsünün doğru sırası hangisidir?", "G1 → S → G2 → M",
               ["S → G1 → G2 → M", "G1 → G2 → S → M", "M → S → G1 → G2"], ["Interfaz (G1, S, G2) + M."]),
        _secim(r, "Diploit bir hücrede G1 evresinde DNA miktarı 2c ise G2'de kaç c olur?", "4c",
               ["2c", "1c", "8c"], ["S evresinde DNA iki katına çıkar."]),
        _secim(r, "Hücre döngüsünün en uzun dönemi genellikle hangisidir?", "İnterfaz",
               ["Mitoz", "Anafaz", "Sitokinez"], ["Döngünün büyük kısmı (≈ %90'ı) interfazdır."]),
        _secim(r, "Siklin proteinlerinin görevi nedir?", "CDK'ları etkinleştirerek evre geçişlerini sağlamak",
               ["DNA'yı kopyalamak", "Ribozom yapmak", "Hücre çeperi oluşturmak"],
               ["Siklin + CDK kompleksi döngünün ilerlemesini yönetir."]),
        _secim(r, "Hücre döngüsü kontrolü bozulup hücrelerin kontrolsüz çoğalmasıyla ne ortaya çıkar?",
               "Kanser", ["Mutasyon onarımı", "Döllenme", "Modifikasyon"],
               ["Kontrol noktaları ve CDK inhibitörleri kanseri önlemeye yardım eder."]),
        _secim(r, "Kromozomların iğ ipliklerine doğru bağlanıp bağlanmadığı hangi kontrol noktasında "
                  "denetlenir?", "Metafaz kontrol noktası", ["G1/S", "G0", "S evresi"],
               ["Her kromozom iğe bağlanmadan anafaz başlamaz."]),
        _secim(r, "Bölünme sırasında (M evresi) hangi iki olay gerçekleşir?",
               "Mitoz ve sitokinez", ["Replikasyon ve transkripsiyon", "G1 ve G2",
                                     "Krossing-over ve döllenme"],
               ["Çekirdek bölünmesi (mitoz) ve sitoplazma bölünmesi (sitokinez)."]),
    ]
    return _tamamla(r, sabit, havuz + _EK["dongu"](r))


# ---------------------------------------------------------------------------
def gen_mitoz(r):
    t, n2 = _tur_sec(r)
    t2, m2 = _tur_sec(r, haric=(t,))
    k = int(r.integers(2, 9))
    sabit = [
        soru_sayi(f"{t} (2n = {n2}) hücresinde METAFAZ evresinde kaç kromatit bulunur?", 2 * n2,
                  [_md("DNA eşlendiği için her kromozom iki kardeş kromatitlidir:"),
                   _tx(rf"2\times 2n = 2\times{n2} = {2 * n2}")], yanlis=[n2, n2 // 2, 4 * n2]),
        soru_sayi(f"{t} (2n = {n2}) hücresinde METAFAZ evresinde kaç kromozom bulunur?", n2,
                  [_md("Sentromerden bağlı iki kromatit TEK kromozom sayılır: hâlâ 2n.")],
                  yanlis=[2 * n2, n2 // 2, 4 * n2]),
        soru_sayi(f"{t2} (2n = {m2}) hücresinde ANAFAZ evresinde hücrede toplam kaç kromozom bulunur?",
                  2 * m2, [_md("Kardeş kromatitler ayrılınca her biri bir kromozom olur:"),
                           _tx(rf"2\times{m2} = {2 * m2}")], yanlis=[m2, m2 // 2, 4 * m2]),
        soru_sayi(f"{t2} (2n = {m2}) hücresinin mitozu sonunda oluşan her yavru hücrede kaç kromozom "
                  "vardır?", m2, [_md("Mitoz kromozom sayısını değiştirmez: 2n → 2n.")],
                  yanlis=[m2 // 2, 2 * m2, m2 + 2]),
        soru_sayi(f"Bir hücre art arda {k} kez mitoz bölünme geçirirse kaç hücre oluşur?", 2 ** k,
                  [_tx(rf"2^{{{k}}} = {2 ** k}"), _md("Her bölünmede hücre sayısı iki katına çıkar.")],
                  yanlis=[2 * k, k ** 2, 2 ** k - 1]),
    ]
    havuz = [
        _secim(r, "Kromozomların ekvatorda tek sıra hâlinde dizildiği evre hangisidir?", "Metafaz",
               ["Profaz", "Anafaz", "Telofaz"], ["Kromozom sayımı bu evrede yapılır."]),
        _secim(r, "Kardeş kromatitlerin ayrılıp zıt kutuplara çekildiği evre hangisidir?", "Anafaz",
               ["Metafaz", "Profaz", "Telofaz"], ["Anafaz en hızlı evredir."]),
        _secim(r, "Kromozomların kısalıp kalınlaşarak görünür hâle geldiği evre hangisidir?", "Profaz",
               ["Telofaz", "Metafaz", "Anafaz"], ["Profazda çekirdek zarı ve çekirdekçik kaybolmaya başlar."]),
        _secim(r, "Yeni çekirdek zarlarının oluştuğu, kromozomların gevşediği evre hangisidir?",
               "Telofaz", ["Profaz", "Metafaz", "Anafaz"], ["Telofaz, profazın tersi gibidir."]),
        _secim(r, "Bitki hücrelerinde sitokinez nasıl gerçekleşir?", "Ortada hücre plağı oluşur",
               ["Zar dışarıdan boğumlanır", "Hücre çeperi erir", "Sentriyoller ayrılır"],
               ["Sert çeper boğumlanmaya izin vermez; keseciklerden hücre plağı oluşur."]),
        _secim(r, "Hayvan hücrelerinde sitokinez nasıl gerçekleşir?", "Hücre zarı boğumlanır",
               ["Hücre plağı oluşur", "Koful bölünür", "Kloroplastlar ayrılır"],
               ["Zar dıştan içe doğru büzülür."]),
        _secim(r, "Mitozla oluşan yavru hücreler için hangisi doğrudur?",
               "Genetik olarak ana hücreyle aynıdır", ["Haploittir", "Genetik olarak farklıdır",
                                                     "Kromozom sayısı yarıya iner"],
               ["Mitoz kopyalayıcı bölünmedir."]),
        _secim(r, "Aşağıdakilerden hangisi mitozun görevlerinden DEĞİLDİR?", "Gamet oluşumu",
               ["Büyüme", "Yara onarımı", "Asmanın çelikle çoğaltılması"],
               ["Hayvanlarda gametler mayozla oluşur."]),
        _secim(r, "İğ ipliklerinin kromozoma bağlandığı, sentromerdeki protein yapısı hangisidir?",
               "Kinetokor", ["Telomer", "Kiazma", "Nükleozom"], ["Kinetokor, sentromer bölgesindedir."]),
        _secim(r, "Çekirdek zarının kaybolmadan gerçekleştiği basit bölünmeye ne denir?", "Amitoz",
               ["Mayoz", "Mitoz", "Sitokinez"], ["Bazı basit yapılı tek hücrelilerde ve bazı kanser "
                                                "hücrelerinde görülür."]),
    ]
    return _tamamla(r, sabit, havuz + _EK["mitoz"](r))


# ---------------------------------------------------------------------------
def gen_mayoz(r):
    t, n2 = _tur_sec(r)
    h = int(r.integers(2, 6))
    k = int(r.integers(2, 8))
    sabit = [
        soru_sayi(f"{t} (2n = {n2}) hücresinde Profaz I'de kaç tetrad (bivalent) oluşur?", n2 // 2,
                  [_md("Her homolog çift bir tetrad oluşturur:"), _tx(rf"n = {n2 // 2}")],
                  yanlis=[n2, 2 * n2, n2 // 4 if n2 >= 8 else n2 + 2]),
        soru_sayi(f"{t} (2n = {n2}) hücresinde Profaz I'de toplam kaç kromatit vardır?", 2 * n2,
                  [_tx(rf"\text{{tetrad sayısı}}\times 4 = {n2 // 2}\times4 = {2 * n2}")],
                  yanlis=[n2, 4 * n2, n2 // 2]),
        soru_sayi(f"{t} (2n = {n2}) türünün Mayoz I sonunda oluşan her hücresinde kaç kromozom "
                  "vardır?", n2 // 2,
                  [_md("Mayoz I'de homologlar ayrılır; kromozom sayısı yarıya iner (kromozomlar hâlâ "
                       "iki kromatitli).")], yanlis=[n2, 2 * n2, n2 // 4 if n2 >= 8 else n2 + 2]),
        soru_sayi(f"AaBb… şeklinde {h} gen çifti bakımından heterozigot (genler farklı "
                  "kromozomlarda) bir birey kaç çeşit gamet oluşturur?", 2 ** h,
                  [_tx(rf"2^{{{h}}} = {2 ** h}")], yanlis=[2 * h, h ** 2, 4 ** h]),
        soru_sayi(f"{k} birincil spermatosit mayoz geçirirse kaç sperm oluşur?", 4 * k,
                  [_tx(rf"4\times{k} = {4 * k}"), _md("Her birincil spermatositten 4 sperm.")],
                  yanlis=[k, 2 * k, 8 * k]),
    ]
    havuz = [
        _secim(r, "Homolog kromozomların birbirinden ayrıldığı evre hangisidir?", "Anafaz I",
               ["Anafaz II", "Metafaz I", "Telofaz II"], ["Anafaz II'de ise kardeş kromatitler ayrılır."]),
        _secim(r, "Kardeş kromatitlerin ayrıldığı mayoz evresi hangisidir?", "Anafaz II",
               ["Anafaz I", "Profaz I", "Metafaz I"], ["Mayoz II mitoza benzer."]),
        _secim(r, "Krossing-over hangi evrede gerçekleşir?", "Profaz I",
               ["Metafaz I", "Profaz II", "Anafaz II"], ["Profaz I'in pakiten alt evresinde."]),
        _secim(r, "Profaz I'in alt evrelerinin doğru sırası hangisidir?",
               "Leptoten → Zigoten → Pakiten → Diploten → Diakinez",
               ["Zigoten → Leptoten → Pakiten → Diakinez → Diploten",
                "Pakiten → Leptoten → Zigoten → Diploten → Diakinez",
                "Leptoten → Pakiten → Zigoten → Diakinez → Diploten"], ["Le-Zi-Pa-Di-Di"]),
        _secim(r, "Homolog kromozomların eşleşmeye başladığı (sinaps) alt evre hangisidir?",
               "Zigoten", ["Leptoten", "Diakinez", "Diploten"],
               ["Zigotende sinaps başlar, pakitende tamamlanır."]),
        _secim(r, "Mayozun asıl amacı nedir?", "Kromozom sayısını yarıya indirip gamet oluşturmak",
               ["Büyümeyi sağlamak", "Yaraları onarmak", "Hücre sayısını artırmak"],
               ["Döllenmede n + n = 2n olur; kromozom sayısı sabit kalır."]),
        _secim(r, "Mayozda tetrad hangi evrede ekvatorda karşılıklı dizilir?", "Metafaz I",
               ["Metafaz II", "Anafaz I", "Telofaz II"],
               ["Mitozda ve Metafaz II'de ise kromozomlar tek tek dizilir."]),
        _secim(r, "Tek bir krossing-over sonunda tetraddaki 4 kromatitten kaçı rekombinant olur?",
               "2", ["4", "1", "0"], ["Yalnızca parça değiştiren iki kromatit rekombinanttır."]),
        _secim(r, "Rekombinasyon oranı en fazla yüzde kaç olabilir?", "%50",
               ["%100", "%25", "%75"], ["Bağımsız dağılan genlerde rekombinant gamet oranı %50'dir."]),
        _secim(r, "Mayozla oluşan dört hücrenin genetik olarak farklı olmasının nedenleri hangileridir?",
               "Krossing-over ve bağımsız dağılım", ["Replikasyon ve transkripsiyon",
                                                    "Sitokinez ve interfaz", "Mutasyon ve modifikasyon"],
               ["Profaz I'de krossing-over, Metafaz I'de homologların rastgele dizilmesi."]),
        _secim(r, "Mayoz I ile Mayoz II arasında hangisi OLMAZ?", "DNA eşlenmesi",
               ["Kısa bir ara dönem", "Sitokinez", "Kromozomların hafif gevşemesi"],
               ["İki bölünme arasında S evresi yoktur."]),
    ]
    return _tamamla(r, sabit, havuz + _EK["mayoz"](r))


# ---------------------------------------------------------------------------
def gen_gamet(r):
    k = int(r.integers(2, 12))
    m = int(r.integers(2, 6))
    t, n2 = _tur_sec(r)
    sabit = [
        soru_sayi(f"{k} birincil oosit oogenezi tamamlarsa kaç yumurta oluşur?", k,
                  [_md("Her birincil oositten yalnızca 1 yumurta oluşur.")], yanlis=[4 * k, 2 * k, 3 * k]),
        soru_sayi(f"{k} birincil oosit oogenezi tamamlarsa en fazla kaç polar cisim oluşur?", 3 * k,
                  [_md("Her oositten 1 yumurta + 3 polar cisim (1. polar cisim de bölünürse):"),
                   _tx(rf"3\times{k} = {3 * k}")], yanlis=[k, 4 * k, 2 * k]),
        soru_sayi(f"Bir ailenin {m} çocuğunun HEPSİNİN kız olma olasılığı nedir?", 0.5 ** m,
                  [_md("Her doğumda kız olma olasılığı 1/2; doğumlar birbirinden bağımsızdır:"),
                   _tx(rf"\left(\tfrac12\right)^{{{m}}} = \frac{{1}}{{{2 ** m}}} = {0.5 ** m:.4f}")],
                  yanlis=[0.5, 1 / m, 0.5 * m / 10]),
        soru_sayi(f"{t} (2n = {n2}) türünde döllenme sonucu oluşan zigotta kaç kromozom bulunur?",
                  n2, [_tx(rf"n + n = {n2 // 2} + {n2 // 2} = {n2}")], yanlis=[n2 // 2, 2 * n2, n2 + 1]),
    ]
    havuz = [
        _secim(r, "Memelilerde yavrunun cinsiyetini hangi gamet belirler?", "Babadan gelen sperm",
               ["Anneden gelen yumurta", "Her ikisi eşit", "Çevre sıcaklığı"],
               ["Sperm X ya da Y taşır; yumurta her zaman X taşır."]),
        _secim(r, "Kuşlarda yavrunun cinsiyetini hangi gamet belirler?", "Anneden gelen yumurta",
               ["Babadan gelen sperm", "Her ikisi eşit", "Kuluçka süresi"],
               ["Kuşlarda dişi ZW'dir; yumurta Z ya da W taşır."]),
        _secim(r, "Tavukta dişinin eşey kromozomları hangisidir?", "ZW", ["ZZ", "XX", "XY"],
               ["Kuşlarda erkek ZZ, dişi ZW."]),
        _secim(r, "Spermatogenez için hangisi doğrudur?", "Bir birincil spermatositten 4 sperm oluşur",
               ["Fetal dönemde başlar ve durur", "Bir hücreden 1 sperm oluşur", "Yumurtalıkta olur"],
               ["Spermatogenez testiste, ergenlikten itibaren sürekli olur."]),
        _secim(r, "Oogenezde polar cisimlerin oluşmasının nedeni nedir?",
               "Sitoplazmanın büyük kısmının yumurtada kalması",
               ["Kromozom sayısının artması", "Spermin girmesini engellemek", "Krossing-over"],
               ["Eşit olmayan sitokinez: besin depolu büyük bir yumurta oluşur."]),
        _secim(r, "Oogenez hangi evrelerde duraklar?", "Profaz I ve Metafaz II",
               ["Anafaz I ve Telofaz II", "G1 ve S", "Hiç duraklamaz"],
               ["Profaz I'de doğum öncesinden ergenliğe, Metafaz II'de döllenmeye kadar bekler."]),
        _secim(r, "Sperm ve yumurta çekirdeklerinin birleşmesine ne denir?", "Döllenme (fertilizasyon)",
               ["Mayoz", "Sinaps", "Krossing-over"], ["Sonuçta diploit zigot oluşur."]),
        _secim(r, "Gametler için hangisi doğrudur?", "Haploittir (n)",
               ["Diploittir (2n)", "Mitozla oluşur (hayvanlarda)", "İki takım kromozom taşır"],
               ["Hayvanlarda gametler mayozla oluşur ve n kromozomludur."]),
        _secim(r, "XX × XY çaprazında yavruların yüzde kaçı erkek olur?", "%50",
               ["%25", "%75", "%100"], ["XX, XY, XX, XY → 2/4 erkek."]),
        _secim(r, "Spermatogenez nerede gerçekleşir?", "Testislerin seminifer tüplerinde",
               ["Yumurtalıkta", "Böbrekte", "Karaciğerde"], ["Seminifer tüpler sperm üretim yeridir."]),
    ]
    return _tamamla(r, sabit, havuz + _EK["gamet"](r))


# ---------------------------------------------------------------------------
def _bozuk(r, dizi, alfabe, adet=4):
    """Bir harfi değiştirilmiş varyantlar (yedek yanlış seçenekler)."""
    out = []
    for _ in range(adet * 3):
        i = int(r.integers(0, len(dizi)))
        yeni = [c for c in alfabe if c != dizi[i]]
        v = dizi[:i] + yeni[int(r.integers(0, len(yeni)))] + dizi[i + 1:]
        if v != dizi and v not in out:
            out.append(v)
        if len(out) >= adet:
            break
    return out


def _rasgele_dna(r, n):
    return "".join("ATGC"[int(i)] for i in r.integers(0, 4, n))


def gen_nukleik(r):
    a = int(r.integers(10, 41))
    g = int(r.integers(10, 41))
    dizi = _rasgele_dna(r, int(r.integers(8, 13)))
    tam = "".join(TAMAMLAYICI[b] for b in dizi)
    at = dizi.count("A") + dizi.count("T")
    gc = len(dizi) - at
    hb = 2 * at + 3 * gc
    nbc = int(r.integers(5, 40)) * 100
    sabit = [
        soru_sayi(f"Bir DNA molekülündeki bazların %{a}'i adenindir. Guanin yüzde kaçtır?",
                  (100 - 2 * a) / 2,
                  [_md("Chargaff kuralı: A = T, G = C."),
                   _tx(rf"A + T = 2\times{a} = {2 * a}\qquad G = C = \frac{{100 - {2 * a}}}{{2}} = {(100 - 2 * a) / 2:g}")],
                  yanlis=[a, 100 - a, 50 - a / 2 if a % 2 else 100 - 2 * a], ondalik=1),
        soru_sayi(f"Bir DNA molekülündeki bazların %{g}'u sitozindir. Timin yüzde kaçtır?",
                  (100 - 2 * g) / 2,
                  [_tx(rf"G = C = {g}\qquad A = T = \frac{{100 - 2\times{g}}}{{2}} = {(100 - 2 * g) / 2:g}")],
                  yanlis=[g, 100 - g, 100 - 2 * g], ondalik=1),
        _secim(r, f"5′-{dizi}-3′ zincirinin tamamlayıcısı hangisidir (3′→5′ yönünde)?",
               f"3′-{tam}-5′",
               [f"3′-{dizi}-5′", f"3′-{tam.replace('T', 'U')}-5′", f"3′-{tam[::-1]}-5′",
                f"3′-{''.join(TAMAMLAYICI[b] if b in 'AT' else b for b in dizi)}-5′"]
               + [f"3′-{v}-5′" for v in _bozuk(r, tam, "ATGC")],
               [f"A↔T, G↔C eşleşir: **{tam}**. RNA'da T yerine U bulunur; DNA'da U olmaz."]),
        soru_sayi(f"5′-{dizi}-3′ dizisi ve tamamlayıcısından oluşan çift zincirli DNA'da kaç "
                  "hidrojen bağı vardır?", hb,
                  [_md(f"A-T çifti: {at} (2'şer bağ), G-C çifti: {gc} (3'er bağ)"),
                   _tx(rf"2\times{at} + 3\times{gc} = {hb}")],
                  yanlis=[2 * len(dizi), 3 * len(dizi), 3 * at + 2 * gc]),
        soru_sayi(f"{nbc} baz çiftinden oluşan çift zincirli bir DNA'da toplam kaç nükleotit vardır?",
                  2 * nbc, [_md("Her baz çifti iki nükleotitten oluşur:"), _tx(rf"2\times{nbc} = {2 * nbc}")],
                  yanlis=[nbc, nbc // 2, 3 * nbc]),
    ]
    havuz = [
        _secim(r, "Nükleotidin yapısında hangisi BULUNMAZ?", "Amino asit",
               ["Fosfat", "Beş karbonlu şeker", "Azotlu baz"], ["Nükleotit = fosfat + şeker + baz."]),
        _secim(r, "Nükleozit nedir?", "Şeker + azotlu baz", ["Fosfat + şeker + baz", "Fosfat + baz",
                                                             "İki nükleotit"],
               ["Nükleozitte fosfat yoktur."]),
        _secim(r, "Aşağıdakilerden hangisi pürin bazıdır?", "Guanin", ["Sitozin", "Timin", "Urasil"],
               ["Pürinler: A ve G (çift halka)."]),
        _secim(r, "Yalnızca RNA'da bulunan baz hangisidir?", "Urasil", ["Timin", "Adenin", "Guanin"],
               ["RNA'da timin yerine urasil vardır."]),
        _secim(r, "Yalnızca DNA'da bulunan baz hangisidir?", "Timin", ["Urasil", "Sitozin", "Adenin"],
               ["Timin yalnız DNA'da bulunur."]),
        _secim(r, "DNA'da guanin ile sitozin arasında kaç hidrojen bağı vardır?", "3", ["2", "1", "4"],
               ["G≡C: 3 bağ, A=T: 2 bağ."]),
        _secim(r, "DNA'nın şekeri hangisidir?", "Deoksiriboz", ["Riboz", "Glikoz", "Fruktoz"],
               ["RNA'nın şekeri ribozdur."]),
        _secim(r, "Bir DNA zincirindeki nükleotitleri birbirine bağlayan bağ hangisidir?",
               "Fosfodiester bağı", ["Hidrojen bağı", "Peptit bağı", "İyonik bağ"],
               ["Hidrojen bağları iki zinciri birbirine bağlar; zincir içinde fosfodiester bağı vardır."]),
        _secim(r, "DNA'nın iki zinciri birbirine hangi bağlarla bağlıdır?", "Hidrojen bağları",
               ["Peptit bağları", "Fosfodiester bağları", "Disülfit bağları"],
               ["Karşılıklı bazlar arasında hidrojen bağları vardır."]),
        _secim(r, "Amino asitleri ribozoma taşıyan RNA hangisidir?", "tRNA", ["mRNA", "rRNA", "DNA"],
               ["tRNA taşıyıcı RNA'dır; antikodonu ile kodonu tanır."]),
        _secim(r, "DNA'daki bilgiyi kopyalayıp ribozoma ileten RNA hangisidir?", "mRNA",
               ["tRNA", "rRNA", "Hiçbiri"], ["mRNA: mesajcı (ulak) RNA."]),
        _secim(r, "Ribozomun yapısına katılan RNA hangisidir?", "rRNA", ["mRNA", "tRNA", "DNA"],
               ["rRNA proteinlerle ribozomu oluşturur."]),
        _secim(r, "DNA'nın çift sarmal yapısını 1953'te kim(ler) ortaya koydu?",
               "Watson ve Crick", ["Mendel", "Miescher", "Meselson ve Stahl"],
               ["Rosalind Franklin ve Maurice Wilkins'in X ışını verileri kullanıldı."]),
        _secim(r, "Nükleik asitleri ilk kez kim elde etti?", "Friedrich Miescher",
               ["Gregor Mendel", "Robert Hooke", "James Watson"], ["1869, 'nüklein'."]),
    ]
    return _tamamla(r, sabit, havuz + _EK["nukleik"](r))


# ---------------------------------------------------------------------------
def gen_dogma(r):
    kalip = _rasgele_dna(r, 9)
    mrna = "".join({"A": "U", "T": "A", "G": "C", "C": "G"}[b] for b in kalip)
    kodonlar = [k for k in GENETIK_KOD if GENETIK_KOD[k] not in "*"]
    sec = [kodonlar[int(i)] for i in r.integers(0, len(kodonlar), 3)]
    mrna2 = "AUG" + "".join(sec) + "UAA"
    aa2 = [AA_AD["M"][0]] + [AA_AD[GENETIK_KOD[k]][0] for k in sec]
    baz = int(r.integers(5, 40)) * 3
    kus = int(r.integers(2, 6))
    kodon = sec[0]
    antikodon = "".join({"A": "U", "U": "A", "G": "C", "C": "G"}[b] for b in kodon)
    yanlis_protein = [
        "–".join(aa2[:1] + aa2[1:][::-1]),
        "–".join([AA_AD[GENETIK_KOD[k]][0] for k in sec]),
        "–".join(aa2 + ["DUR"]),
    ]
    sabit = [
        _secim(r, f"Kalıp DNA zinciri 3′-{kalip}-5′ ise oluşacak mRNA hangisidir (5′→3′)?",
               f"5′-{mrna}-3′",
               [f"5′-{''.join(TAMAMLAYICI[b] for b in kalip)}-3′", f"5′-{kalip.replace('T', 'U')}-3′",
                f"5′-{mrna[::-1]}-3′", f"5′-{mrna.replace('U', 'T')}-3′"]
               + [f"5′-{v}-3′" for v in _bozuk(r, mrna, "AUGC")],
               ["Kalıp DNA'daki A'nın karşısına U, T'nin karşısına A, G'nin karşısına C, C'nin "
                f"karşısına G gelir: **{mrna}**."]),
        _secim(r, f"5′-{mrna2}-3′ mRNA'sından hangi protein (amino asit dizisi) oluşur?",
               "–".join(aa2), list(dict.fromkeys(y for y in yanlis_protein if y != "–".join(aa2)))
               + ["–".join(aa2[:-1] + [AA_AD[x][0]]) for x in "GAVLSKPT" if AA_AD[x][0] != aa2[-1]],
               ["Kodonlara ayırın: " + " · ".join(f"{mrna2[i:i + 3]}" for i in range(0, len(mrna2), 3)),
                "Genetik kod tablosundan: " + ", ".join(
                    f"{mrna2[i:i + 3]} = {AA_AD[GENETIK_KOD[mrna2[i:i + 3]]][0]}" for i in range(0, len(mrna2), 3)),
                "UAA durdurma kodonudur; amino asit eklenmez."]),
        soru_sayi(f"{baz} nükleotitlik bir mRNA dizisinde (durdurma kodonu dahil) kaç kodon vardır?",
                  baz // 3, [_tx(rf"\frac{{{baz}}}{{3}} = {baz // 3}"), _md("Her kodon 3 bazdır.")],
                  yanlis=[baz, baz // 2, 3 * baz]),
        soru_sayi(f"{baz} nükleotitlik bir mRNA (son kodonu durdurma kodonu) kaç amino asitlik bir "
                  "protein kodlar?", baz // 3 - 1,
                  [_tx(rf"\frac{{{baz}}}{{3}} - 1 = {baz // 3 - 1}"),
                   _md("Durdurma kodonu amino asit belirlemez.")], yanlis=[baz // 3, baz, baz // 3 + 1]),
        soru_sayi(f"Ağır DNA'lı bakteriler hafif ortamda {kus} kuşak çoğaltılıyor. Oluşan DNA "
                  "moleküllerinin kaçta kaçı melez (bir eski + bir yeni zincir) olur?", 2 / 2 ** kus,
                  [_md(f"{kus}. kuşakta {2 ** kus} molekül vardır; eski iki zincir yalnızca 2 molekülde "
                       "kalır (yarı korunumlu):"), _tx(rf"\frac{{2}}{{{2 ** kus}}} = {2 / 2 ** kus:.4f}")],
                  yanlis=[0.5, 1 / 2 ** kus, 1 - 2 / 2 ** kus]),
        _secim(r, f"mRNA kodonu 5′-{kodon}-3′ ise bunu tanıyan tRNA'nın antikodonu hangisidir "
                  "(3′→5′)?", f"3′-{antikodon}-5′",
               [f"3′-{kodon}-5′", f"3′-{antikodon[::-1]}-5′", f"3′-{antikodon.replace('U', 'T')}-5′",
                f"3′-{kodon[::-1]}-5′",
                f"3′-{''.join({'A': 'G', 'G': 'A', 'U': 'C', 'C': 'U'}[b] for b in antikodon)}-5′"]
               + [f"3′-{v}-5′" for v in _bozuk(r, antikodon, "AUGC")],
               [f"Antikodon kodona tamamlayıcıdır ve RNA olduğu için U içerir: **{antikodon}**."]),
    ]
    havuz = [
        _secim(r, "Sentral dogmada bilginin akış yönü hangisidir?", "DNA → RNA → Protein",
               ["Protein → RNA → DNA", "RNA → DNA → Protein", "DNA → Protein → RNA"], ["Sentral dogma."]),
        _secim(r, "DNA'dan mRNA sentezlenmesine ne denir?", "Transkripsiyon",
               ["Translasyon", "Replikasyon", "Mutasyon"], ["Transkripsiyon çekirdekte olur."]),
        _secim(r, "mRNA'daki bilgiye göre protein sentezlenmesine ne denir?", "Translasyon",
               ["Transkripsiyon", "Replikasyon", "Sinaps"], ["Translasyon ribozomda olur."]),
        _secim(r, "DNA replikasyonu için hangisi doğrudur?", "Yarı korunumludur",
               ["Tamamen korunumludur", "Sitoplazmada ribozomda olur", "RNA polimeraz yapar"],
               ["Her yeni DNA = 1 eski + 1 yeni zincir; enzim DNA polimerazdır."]),
        _secim(r, "Başlangıç kodonu hangisidir?", "AUG", ["UAA", "UGA", "GGG"], ["AUG: metiyonin."]),
        _secim(r, "Aşağıdakilerden hangisi durdurma kodonu DEĞİLDİR?", "AUG", ["UAA", "UAG", "UGA"],
               ["Durdurma kodonları: UAA, UAG, UGA."]),
        _secim(r, "Bir kodon kaç bazdan oluşur?", "3", ["2", "1", "4"], ["Üçlü kod."]),
        _secim(r, "Kodonun aynı amino asidi kodlayan başka bir kodona dönüştüğü mutasyon hangisidir?",
               "Sessiz mutasyon", ["Anlamsız mutasyon", "Çerçeve kayması", "Yanlış anlamlı mutasyon"],
               ["Protein değişmez."]),
        _secim(r, "Bir kodonun erken durdurma kodonuna dönüşmesine ne denir?", "Anlamsız (nonsense) mutasyon",
               ["Sessiz mutasyon", "Yanlış anlamlı mutasyon", "Modifikasyon"], ["Protein kısa kalır."]),
        _secim(r, "Gene tek bir baz eklenmesi genellikle hangi sonuca yol açar?", "Çerçeve kayması",
               ["Sessiz mutasyon", "Hiçbir değişiklik", "Yalnız bir amino asit değişimi"],
               ["Okuma çerçevesi kayar; sonraki bütün kodonlar değişir."]),
        _secim(r, "DNA'nın iki zincirini birbirinden ayıran enzim hangisidir?", "Helikaz",
               ["DNA polimeraz", "RNA polimeraz", "Ligaz"], ["Helikaz hidrojen bağlarını açar."]),
        _secim(r, "Transkripsiyonu yapan enzim hangisidir?", "RNA polimeraz",
               ["DNA polimeraz", "Helikaz", "Ribozom"], ["RNA polimeraz kalıp DNA'yı okur."]),
    ]
    return _tamamla(r, sabit, havuz + _EK["dogma"](r))


# ---------------------------------------------------------------------------
def gen_terim(r):
    idx = r.permutation(len(TERIMLER))[:SORU_SAYISI]
    sorular = []
    for j, i in enumerate(idx):
        terim, tanim = TERIMLER[int(i)]
        digerleri = [TERIMLER[int(x)] for x in r.permutation(len(TERIMLER)) if int(x) != int(i)][:3]
        if j % 2 == 0:
            sorular.append(_secim(r, f"“{tanim}” Bu tanım hangi terime aittir?", terim,
                                  [d[0] for d in digerleri], [f"**{terim}:** {tanim}"]))
        else:
            kisa = lambda t: t if len(t) < 120 else t[:117] + "…"
            sorular.append(_secim(r, f"**{terim}** teriminin doğru tanımı hangisidir?", kisa(tanim),
                                  [kisa(d[1]) for d in digerleri], [f"**{terim}:** {tanim}"]))
    return sorular


# ---------------------------------------------------------------------------
_TUM_URETICILER = None


def gen_tekrar(r):
    ureticiler = [gen_giris, gen_tarih, gen_hucre, gen_kromozom, gen_dongu, gen_mitoz, gen_mayoz,
                  gen_gamet, gen_nukleik, gen_trans, gen_dogma, gen_terim]
    secilen = [ureticiler[int(i)] for i in r.permutation(len(ureticiler))[:SORU_SAYISI]]
    return [u(r)[0] for u in secilen]


# ===========================================================================
# EK SORU HAVUZLARI (soru çeşitliliğini artırmak için)
# ===========================================================================
def _ek(r, liste):
    return [_secim(r, m, d, y, c) for m, d, y, c in liste]


def ek_giris(r):
    return _ek(r, [
        ("Genetik biliminin temel ilgi alanı hangisidir?",
         "Kalıtsal özelliklerin dölden döle nasıl aktarıldığı",
         ["Yalnızca hastalıkların tedavisi", "Toprak yapısı", "İklim değişimi"],
         ["Genetik = kalıtım bilimi."]),
        ("Varyasyon (değişkenlik) hangi iki etmenden kaynaklanır?", "Genotip ve çevre",
         ["Yalnızca genotip", "Yalnızca çevre", "Yalnızca mutasyon"],
         ["Fenotipik farklılıklar hem genlerden hem çevreden kaynaklanır."]),
        ("Mutasyon taşıyan bireye ne ad verilir?", "Mutant", ["Klon", "Hibrit", "Homozigot"],
         ["Mutasyon taşıyan birey mutanttır."]),
        ("Seleksiyon için hangisi doğrudur?",
         "Belirli genotiplerin daha çok yavru bırakmasıdır",
         ["DNA'da baz değişimidir", "Kromozomlar arası parça değişimidir",
          "Çevrenin kalıtsal olmayan etkisidir"],
         ["Doğal ya da yapay seçilim, uygun genotiplerin çoğalmasını sağlar."]),
        ("Holştayn boğa × Holştayn inek çiftleşmesinden Holştayn buzağı doğması hangi kavramı örnekler?",
         "Kalıtım", ["Mutasyon", "Modifikasyon", "Rekombinasyon"],
         ["Canlılar kendilerine benzer yavrular oluşturur."]),
        ("Aynı genotipe sahip iki tohumdan biri verimli tarlada, diğeri kurak tarlada farklı boyda "
         "bitki veriyor. Bu farkın nedeni nedir?", "Çevre", ["Genotip", "Mutasyon", "Krossing-over"],
         ["Genotip aynıysa fark çevreden kaynaklanır (modifikasyon)."]),
        ("Poligenik kalıtım için hangisi doğrudur?", "Bir özelliği birçok gen birlikte etkiler",
         ["Bir özelliği tek gen belirler", "Çevrenin etkisi yoktur", "Yalnızca bitkilerde görülür"],
         ["Kantitatif karakterler poligeniktir."]),
        ("Hangi karakter çevreden EN AZ etkilenir?", "Kan grubu",
         ["Süt verimi", "Canlı ağırlık", "Yumurta verimi"],
         ["Kalitatif karakterler çevreden çok az etkilenir."]),
        ("Kantitatif karakterlerin bir popülasyondaki dağılımı genellikle hangi şekildedir?",
         "Çan eğrisi (sürekli dağılım)", ["İki keskin sınıf", "Tek değer", "Rastgele noktalar"],
         ["Çok gen + çevre → sürekli, normal dağılıma benzer dağılım."]),
        ("Genetiğin hangi dalı popülasyonlardaki allel frekanslarını inceler?", "Popülasyon genetiği",
         ["Moleküler genetik", "Mendel genetiği", "Sitogenetik"], ["Örneğin Hardy-Weinberg ilkesi."]),
        ("Genetiğin hangi dalı DNA, RNA ve genlerin moleküler yapısını inceler?", "Moleküler genetik",
         ["Kantitatif genetik", "Popülasyon genetiği", "Mendel genetiği"], ["Moleküler genetik."]),
        ("Süt veriminin kalıtımı genetiğin hangi dalının konusudur?", "Kantitatif genetik",
         ["Mendel genetiği", "Sitogenetik", "Moleküler genetik"],
         ["Ölçülebilen, poligenik özellikler kantitatif genetiğin konusudur."]),
        ("Genom nedir?", "Bir canlının taşıdığı genetik materyalin tamamı",
         ["Tek bir gen", "Bir lokustaki iki allel", "Gözlenen özelliklerin tamamı"],
         ["Çekirdek genomu + organel (mitokondri, kloroplast) genomu."]),
        ("Genotip nedir?", "Bireyin taşıdığı allellerin bileşimi (ör. Aa)",
         ["Gözlenen özellik", "Genomun tamamı", "Çevrenin etkisi"],
         ["Genotip sembolle gösterilir: AA, Aa, aa."]),
        ("Fenotip nedir?", "Canlının gözlemlenebilir ve ölçülebilir özellikleri",
         ["Yalnızca genlerin toplamı", "Kromozom sayısı", "DNA dizisi"],
         ["Morfolojik, fizyolojik, biyokimyasal ya da davranışsal olabilir; F = G + Ç."]),
        ("Hangisi fenotipin gruplarından biri DEĞİLDİR?", "Allelik", ["Morfolojik", "Fizyolojik", "Biyokimyasal"],
         ["Fenotip: morfolojik, fizyolojik, biyokimyasal, davranışsal."]),
        ("Gözle görülmeyen ama laboratuvarda ölçülebilen kan grubu için hangisi doğrudur?", "Biyokimyasal bir fenotiptir",
         ["Fenotip değildir, genotiptir", "Davranışsal bir fenotiptir", "Çevresel bir özelliktir"],
         ["Fenotip yalnızca dış görünüş değildir; ölçülebilen her özellik fenotiptir."]),
        ("Genotipleri AA ve Aa olan iki bezelyenin tohumları sarıdır. Bu durum neyi gösterir?",
         "Farklı genotipler aynı fenotipi verebilir",
         ["Genotip ve fenotip her zaman aynıdır", "Çevre genotipi değiştirir", "A alleli resesiftir"],
         ["A dominant olduğu için heterozigot da sarıdır."]),
        ("Ekstrakromozomal (sitoplazmik) kalıtım hangi DNA ile ilgilidir?",
         "Mitokondri ve kloroplast DNA'sı", ["Çekirdek DNA'sı", "X kromozomu", "Otozomlar"],
         ["Kromozom dışı, organel genomu."]),
        ("Mitokondri ile kalıtılan bir özellik yavruya genellikle kimden geçer?", "Anneden",
         ["Babadan", "İki ebeveynden eşit", "Rastgele"],
         ["Zigotun sitoplazması ve organelleri yumurtadan gelir."]),
        ("Ekstrakromozomal kalıtım için hangisi doğrudur?", "Mendel oranlarına uymaz",
         ["Mendel oranlarına tam uyar", "Yalnızca erkeklerde görülür", "Kromozomlarla aktarılır"],
         ["Yavru annenin özelliğini gösterir."]),
        ("Bitkilerde yapraktaki alacalığın (yeşil-beyaz) anneden kalıtıldığını gösteren bilim insanı kimdir?",
         "Carl Correns", ["Gregor Mendel", "Thomas Morgan", "Robert Hooke"],
         ["Correns, 1909, akşam sefası (Mirabilis jalapa)."]),
        ("Genom ile genotip arasındaki fark nedir?",
         "Genom tüm DNA'dır; genotip belirli lokuslardaki allellerdir",
         ["İkisi aynı şeydir", "Genom yalnızca mitokondridedir", "Genotip gözlenen özelliktir"],
         ["Genom: tüm genetik materyal; genotip: incelenen genlerin allel bileşimi."]),
    ])


def ek_hucre(r):
    return _ek(r, [
        ("Hücre zarının yapısında başlıca hangi maddeler bulunur?", "Yağlar (fosfolipitler) ve proteinler",
         ["Selüloz ve kitin", "Nişasta ve glikojen", "DNA ve RNA"], ["Zar: fosfolipit çift tabaka + proteinler."]),
        ("Çekirdek zarı için hangisi doğrudur?", "Çift katlıdır ve porlar içerir",
         ["Tek katlı ve geçirimsizdir", "Yalnızca bitkilerde bulunur", "Selülozdan yapılmıştır"],
         ["Porlar madde alışverişini sağlar (ör. mRNA'nın çıkışı)."]),
        ("Hücrenin enerji merkezi olarak bilinen organel hangisidir?", "Mitokondri",
         ["Golgi aygıtı", "Lizozom", "Ribozom"], ["Oksijenli solunumla ATP üretir."]),
        ("Protein sentezinin yapıldığı yapı hangisidir?", "Ribozom",
         ["Mitokondri", "Koful", "Sentrozom"], ["Ribozom zarsızdır, rRNA ve proteinden oluşur."]),
        ("Sindirim enzimleri içeren organel hangisidir?", "Lizozom",
         ["Golgi aygıtı", "Kloroplast", "Çekirdekçik"], ["Hücre içi sindirim."]),
        ("Ribozom alt birimlerinin yapıldığı yer hangisidir?", "Çekirdekçik",
         ["Golgi aygıtı", "Hücre zarı", "Lizozom"], ["Çekirdekçikte rRNA sentezlenir."]),
        ("Üzerinde ribozom bulunan endoplazmik retikuluma ne denir?", "Granüllü ER",
         ["Granülsüz ER", "Golgi", "Lizozom"], ["Granüllü (pürüzlü) ER."]),
        ("Bitki hücresine turgor (dolgunluk) basıncı sağlayan yapı hangisidir?", "Merkezi koful",
         ["Mitokondri", "Ribozom", "Sentriyol"], ["Büyük koful su depolar."]),
        ("Fotosentez yapan organel hangisidir?", "Kloroplast",
         ["Mitokondri", "Golgi", "Lizozom"], ["Klorofil içerir."]),
        ("Hücrenin üç temel kısmı hangileridir?", "Hücre zarı, sitoplazma, çekirdek",
         ["Çeper, koful, kloroplast", "Ribozom, lizozom, Golgi", "DNA, RNA, protein"],
         ["Bu üç kısımdan biri olmazsa hücre yaşayamaz."]),
        ("Mitokondri DNA'sı genellikle hangi ebeveynden kalıtılır?", "Anneden",
         ["Babadan", "İki ebeveynden eşit", "Hiçbirinden"],
         ["Yumurtanın sitoplazmasıyla aktarılır."]),
        ("Hücre teorisini kuran bilim insanları kimlerdir?", "Schleiden ve Schwann",
         ["Watson ve Crick", "Hardy ve Weinberg", "Mendel ve Darwin"], ["1838–1839."]),
    ])


def ek_kromozom(r):
    return _ek(r, [
        ("Bölünme sırasında kromozomların en net görüldüğü evre hangisidir?", "Metafaz",
         ["İnterfaz", "Telofaz", "G1"], ["Karyotip metafaz kromozomlarından hazırlanır."]),
        ("Bir kromozom DNA eşlendikten sonra kaç kromatitten oluşur?", "2", ["1", "4", "3"],
         ["İki kardeş kromatit."]),
        ("Sentromeri uca çok yakın olan kromozom tipi hangisidir?", "Akrosentrik",
         ["Metasentrik", "Submetasentrik", "Halka"], ["İnsanda 13, 14, 15, 21, 22 akrosentriktir."]),
        ("İnsan vücut hücresinde toplam kaç kromozom vardır?", "46", ["23", "44", "48"],
         ["2n = 46."]),
        ("İnsan yumurta hücresinde kaç kromozom vardır?", "23", ["46", "22", "24"], ["n = 23."]),
        ("İnsan dişisinin eşey kromozomları hangisidir?", "XX", ["XY", "ZW", "ZZ"], ["Dişi XX."]),
        ("Cinsiyetin belirlenmesinde rol almayan kromozomlara ne denir?", "Otozom",
         ["Gonozom", "Homolog", "Kromatit"], ["İnsanda 22 çift otozom vardır."]),
        ("Kromozomun uzun koluna ne ad verilir?", "q kolu", ["p kolu", "Telomer", "Sentromer"],
         ["q: uzun kol."]),
        ("Ekmeklik buğday için hangisi doğrudur?", "Heksaploittir (2n = 6x = 42)",
         ["Haploittir", "Diploittir (2n = 14)", "Tetraploittir (2n = 28)"],
         ["Üç farklı atadan gelen genomları taşır."]),
        ("Bir türdeki kromozomların bir takımı hangi harfle gösterilir?", "n", ["2n", "c", "x2"],
         ["Diploitte iki takım: 2n."]),
        ("İğ ipliklerinin bağlandığı kinetokor kromozomun neresindedir?", "Sentromer bölgesinde",
         ["Telomerde", "p kolunun ucunda", "Kromatinde"], ["Kinetokor sentromerdeki protein yapıdır."]),
        ("Bir genin kromozom üzerindeki yerine ne denir?", "Lokus", ["Allel", "Genotip", "Sentromer"],
         ["Lokus = adres."]),
        ("Aynı genin farklı biçimlerine ne denir?", "Allel", ["Lokus", "Homolog", "Kromatit"],
         ["Ör. A ve a."]),
        ("Allel genler homolog kromozomların neresinde bulunur?", "Karşılıklı (aynı) lokuslarında",
         ["Farklı lokuslarında", "Yalnızca telomerlerde", "Yalnızca sentromerde"],
         ["Homologlar aynı genleri aynı sırada taşır."]),
        ("Genotipi Aa olan birey bu lokus için nasıldır?", "Heterozigot", ["Homozigot dominant",
                                                                         "Homozigot resesif", "Haploit"],
         ["İki allel farklı → heterozigot."]),
        ("Genotipi aa olan birey bu lokus için nasıldır?", "Homozigot resesif",
         ["Heterozigot", "Homozigot dominant", "Melez"], ["İki allel aynı ve resesif."]),
        ("Heterozigot durumda da etkisini gösteren allele ne denir?", "Dominant (baskın)",
         ["Resesif (çekinik)", "Mutant", "Letal"], ["Büyük harfle gösterilir."]),
        ("Etkisini yalnızca homozigot olduğunda gösteren allele ne denir?", "Resesif (çekinik)",
         ["Dominant", "Kodominant", "Mutant"], ["Küçük harfle gösterilir; F1'de saklanır, F2'de ortaya çıkar."]),
        ("Sarı (A) yeşile (a) baskınsa, Aa genotipli bezelyenin tohum rengi nedir?", "Sarı",
         ["Yeşil", "Sarı-yeşil benekli", "Açık yeşil"], ["Dominant allel fenotipte görünür."]),
        ("Homozigot ve heterozigot terimleri neye göre söylenir?", "Belirli bir lokusa göre",
         ["Bütün genoma göre", "Kromozom sayısına göre", "Hücre tipine göre"],
         ["Aynı birey bir lokusta heterozigot, bir başkasında homozigot olabilir."]),
        ("Aynı lokustaki iki allel DNA düzeyinde çoğu zaman ne kadar farklıdır?",
         "Çoğu zaman tek bir nükleotit kadar (SNP)", ["Tamamen farklı genlerdir",
                                                     "Farklı kromozomlardadır", "Hiç farklı değildir"],
         ["Tek nükleotit polimorfizmi."]),
    ])


def ek_dongu(r):
    return _ek(r, [
        ("İnterfazın alt evreleri hangileridir?", "G1, S, G2", ["Profaz, metafaz, anafaz", "G0, M",
                                                            "S, M, G0"], ["İnterfaz = G1 + S + G2."]),
        ("Sentriyollerin eşlenmesi ve bölünmeye son hazırlık hangi evrede tamamlanır?", "G2",
         ["G1", "G0", "M"], ["G2: ikinci büyüme ve hazırlık evresi."]),
        ("Sinir hücrelerinin çoğu döngünün hangi evresinde bulunur?", "G0", ["S", "M", "G2"],
         ["Bölünmeyen hücreler G0'dadır."]),
        ("Tipik bir memeli hücresinde döngü yaklaşık ne kadar sürer?", "24 saat",
         ["1 saat", "1 hafta", "10 dakika"], ["Hücre tipine göre değişir; yaklaşık 24 saat."]),
        ("Siklinlerin görevini tamamladıktan sonraki durumu nedir?", "Hızla yıkılırlar",
         ["Sürekli birikirler", "DNA'ya dönüşürler", "Ribozom olurlar"],
         ["Siklin düzeyi evreye göre inip çıkar."]),
        ("CDK'nın açılımı nedir?", "Siklin bağımlı kinaz",
         ["Kromozom dağılım kompleksi", "Çekirdek DNA kinazı", "Hücre bölünme kodu"], ["Cyclin-dependent kinase."]),
        ("RB proteini fosforlanınca ne olur?", "E2F serbest kalır, DNA eşlenmesi için genler çalışır",
         ["Hücre ölür", "Mitoz durur", "DNA yıkılır"], ["Döngünün 'başlat' anahtarı."]),
        ("CDK inhibitörleri (Cip/Kip, INK4) nasıl davranır?", "Tümör baskılayıcı gibi",
         ["Kanser yapıcı gibi", "Enerji üretici gibi", "Hormon gibi"], ["Döngüyü frenlerler."]),
        ("DNA'da hasar varsa hücre hangi kontrol noktasında durdurulur (S'ye geçmeden)?", "G1/S",
         ["Metafaz", "Telofaz", "G0"], ["Hasarlı DNA eşlenmeden önce onarılmalıdır."]),
        ("Hücre döngüsünde 'M evresi' ne demektir?", "Bölünme (mitoz + sitokinez)",
         ["Mutasyon evresi", "Metabolizma evresi", "Mayoz evresi"], ["M: mitoz."]),
    ])


def ek_mitoz(r):
    return _ek(r, [
        ("Çekirdek zarının tamamen kaybolduğu, iğ ipliklerinin kinetokorlara bağlandığı evre hangisidir?",
         "Prometafaz", ["Telofaz", "Anafaz", "İnterfaz"], ["Geç profaz da denir."]),
        ("Mitozun en hızlı gerçekleşen evresi hangisidir?", "Anafaz", ["Profaz", "Metafaz", "İnterfaz"],
         ["Kardeş kromatitler hızla kutuplara çekilir."]),
        ("Mitozda sentromerlerin ikiye ayrıldığı evre hangisidir?", "Anafaz",
         ["Metafaz", "Profaz", "Telofaz"], ["Böylece kardeş kromatitler ayrılır."]),
        ("Mitoz hangi hücrelerde görülür?", "Vücut (somatik) hücrelerinde",
         ["Yalnızca gametlerde", "Yalnızca bakterilerde", "Yalnızca sinir hücrelerinde"],
         ["Gamet ana hücrelerinde mayoz olur."]),
        ("Asma çeliğinden gelişen bitki ana bitkiye göre nasıldır?", "Genetik olarak aynıdır",
         ["Haploittir", "Genetik olarak tamamen farklıdır", "Kromozom sayısı yarıdır"],
         ["Eşeysiz üreme mitozla olur; oluşan bitki klondur."]),
        ("Mitotik iğ ipliklerini oluşturan mikrotübüller hangi yapıdan uzanır?", "Sentrozomdan",
         ["Ribozomdan", "Lizozomdan", "Kloroplasttan"], ["Hayvan hücrelerinde sentrozom (sentriyoller)."]),
        ("Telofazda hangisi OLMAZ?", "Kardeş kromatitlerin ayrılması",
         ["Çekirdek zarının yeniden oluşması", "Çekirdekçiğin belirmesi", "Kromozomların gevşemesi"],
         ["Kromatitler anafazda ayrılır."]),
        ("Sitokinez neyin bölünmesidir?", "Sitoplazmanın", ["Çekirdeğin", "DNA'nın", "Kromozomun"],
         ["Çekirdek bölünmesi mitozdur."]),
        ("Mitoz sonunda oluşan yavru hücreler ana hücreye göre büyüklük bakımından nasıldır?",
         "Daha küçüktür; interfazda büyürler", ["Daha büyüktür", "Aynı büyüklüktedir", "İki kat büyüktür"],
         ["Yeni hücreler G1'de büyür."]),
        ("Yara iyileşmesinde hangi bölünme görev alır?", "Mitoz", ["Mayoz", "Döllenme", "Amitoz"],
         ["Yeni vücut hücreleri mitozla oluşur."]),
    ])


def ek_mayoz(r):
    return _ek(r, [
        ("Kiazmaların görünür hâle geldiği Profaz I alt evresi hangisidir?", "Diploten",
         ["Leptoten", "Zigoten", "Pakiten"], ["Diplotende homologlar ayrılmaya başlar."]),
        ("Krossing-overın gerçekleştiği alt evre hangisidir?", "Pakiten",
         ["Leptoten", "Diakinez", "Zigoten"], ["Pakitende tetradlar belirgindir."]),
        ("Çekirdek zarının dağılmasıyla Profaz I'i bitiren alt evre hangisidir?", "Diakinez",
         ["Diploten", "Pakiten", "Leptoten"], ["Kromozomlar en kalın hâlindedir."]),
        ("Homolog kromozomların boylu boyunca eşleşmesine ne denir?", "Sinaps",
         ["Kiazma", "Sitokinez", "Replikasyon"], ["Sinaps zigotende başlar."]),
        ("Mayoz I'e neden 'indirgeme bölünmesi' denir?", "Kromozom sayısı yarıya iner",
         ["DNA miktarı iki katına çıkar", "Hücre sayısı azalır", "Kromozomlar kaybolur"],
         ["2n → n."]),
        ("Mayoz II hangi bölünmeye benzer?", "Mitoza", ["Mayoz I'e", "Amitoza", "İkiye bölünmeye"],
         ["Kardeş kromatitler ayrılır."]),
        ("Mayoz olmasaydı ne olurdu?", "Her kuşakta kromozom sayısı iki katına çıkardı",
         ["Kromozom sayısı yarıya inerdi", "Hiçbir şey değişmezdi", "Mutasyon olmazdı"],
         ["n + n = 2n dengesi bozulurdu."]),
        ("Bitkilerde mayoz nerede gerçekleşir?", "Çiçeğin üreme organlarında (başçık ve tohum taslağı)",
         ["Yapraklarda", "Kökte", "Gövdede"], ["Polen ve yumurta oluşumu için."]),
        ("Mitozda homolog kromozomlar eşleşir mi?", "Hayır, yalnızca mayozda eşleşir",
         ["Evet, her zaman", "Yalnızca bitkilerde", "Yalnızca anafazda"], ["Sinaps mayoza özgüdür."]),
        ("Bir tetrad kaç kromatit içerir?", "4", ["2", "8", "1"], ["İki homolog × iki kardeş kromatit."]),
        ("Homologların Metafaz I'de rastgele dizilmesi hangi Mendel ilkesinin temelidir?",
         "Bağımsız dağılım", ["Baskınlık", "Ayrılma", "Eksik baskınlık"],
         ["Farklı çiftler birbirinden bağımsız dağılır."]),
    ])


def ek_gamet(r):
    return _ek(r, [
        ("Spermatogenez ne zaman başlar?", "Ergenlikten (puberte) hemen önce",
         ["Fetal dönemde", "Doğumdan hemen sonra", "Yaşlılıkta"], ["Ömür boyu sürer."]),
        ("Oogenez ne zaman başlar?", "Doğumdan önce (fetal dönemde)",
         ["Ergenlikte", "Menopozda", "Döllenmede"], ["Oogonyumlar fetal dönemde çoğalır."]),
        ("Oogenezde ikinci mayoz bölünme ne zaman tamamlanır?", "Döllenme gerçekleşirse",
         ["Doğumda", "Ergenlikte", "Hiçbir zaman"], ["İkincil oosit Metafaz II'de bekler."]),
        ("Bir spermatogonyumdan oluşan birincil spermatosit kaç kromozomludur?", "2n",
         ["n", "4n", "3n"], ["Birincil spermatosit henüz mayoza girmemiştir."]),
        ("İkincil spermatosit kaç kromozomludur?", "n", ["2n", "4n", "1"], ["Mayoz I sonucu oluşur."]),
        ("Zigot hangi bölünmeyle gelişerek canlıyı oluşturur?", "Mitoz", ["Mayoz", "Amitoz", "Sitokinez yok"],
         ["Zigot mitozla bölünerek embriyoyu oluşturur."]),
        ("Döllenmeden sonra yumurtaya başka spermlerin girmesi nasıl engellenir?",
         "Yumurta zarında kimyasal değişiklikler olur", ["Sperm ölür", "Kromozomlar kaybolur",
                                                        "Polar cisim spermi yakalar"],
         ["Böylece zigot 2n kalır."]),
        ("Memelilerde erkek bireyin ürettiği spermlerin yüzde kaçı Y kromozomu taşır?", "%50",
         ["%100", "%25", "%0"], ["XY → X ve Y taşıyan spermler eşit oranda."]),
        ("Tavukta dişinin ürettiği yumurtaların yüzde kaçı W kromozomu taşır?", "%50",
         ["%100", "%0", "%25"], ["ZW → Z ve W taşıyan yumurtalar eşit oranda."]),
        ("İki çocuğu kız olan bir ailenin üçüncü çocuğunun kız olma olasılığı nedir?", "1/2",
         ["1/8", "1/4", "0"], ["Her doğum bağımsızdır; önceki doğumlar sonucu etkilemez."]),
        ("Gametogenezde eşey hormonlarını da salgılayan organlara ne denir?", "Gonadlar (testis ve yumurtalık)",
         ["Böbrekler", "Akciğerler", "Lenf düğümleri"], ["Üreme sisteminin iki görevi: gamet ve hormon."]),
    ])


def ek_nukleik(r):
    return _ek(r, [
        ("DNA'nın açılımı nedir?", "Deoksiribonükleik asit", ["Deoksiriboz nitrik asit",
                                                            "Diribonükleik asit", "Dinükleotit asit"],
         ["Şekeri deoksiribozdur."]),
        ("Pirimidin bazları hangileridir?", "Sitozin, timin, urasil",
         ["Adenin, guanin", "Adenin, timin", "Guanin, sitozin"], ["Tek halkalı bazlar."]),
        ("DNA'da adenin hangi bazla eşleşir?", "Timin", ["Guanin", "Sitozin", "Urasil"], ["A = T."]),
        ("RNA'da adenin hangi bazla eşleşir?", "Urasil", ["Timin", "Guanin", "Sitozin"], ["A = U."]),
        ("DNA'nın iki zincirinin zıt yönlü olmasına ne denir?", "Antiparalel",
         ["Paralel", "Yarı korunumlu", "Polimorfik"], ["Biri 5′→3′, diğeri 3′→5′."]),
        ("Genetik bilgi DNA'da nasıl saklanır?", "Bazların diziliş sırasıyla",
         ["Şeker sayısıyla", "Fosfat miktarıyla", "Zincir uzunluğuyla"], ["Değişken olan bazların sırasıdır."]),
        ("Çift zincirli DNA'da pürinlerin oranı pirimidinlere göre nasıldır?", "Eşittir",
         ["İki katıdır", "Yarısıdır", "Türe göre çok farklıdır"], ["Chargaff kuralı: A + G = T + C."]),
        ("RNA kaç zincirlidir?", "Tek", ["Çift", "Üç", "Dört"], ["Genellikle tek zincirlidir."]),
        ("Kendini eşleme (replikasyon) yeteneği olan nükleik asit hangisidir?", "DNA",
         ["mRNA", "tRNA", "rRNA"], ["RNA, DNA'dan kopyalanır."]),
        ("Antikodon hangi RNA çeşidinde bulunur?", "tRNA", ["mRNA", "rRNA", "DNA"],
         ["tRNA antikodonu ile mRNA kodonunu tanır."]),
        ("GC oranı yüksek bir DNA'nın zincirlerini ayırmak için ne gerekir?", "Daha yüksek sıcaklık",
         ["Daha düşük sıcaklık", "Daha az enerji", "Hiçbir şey"], ["G-C çiftinde 3 hidrojen bağı vardır."]),
    ])


def ek_dogma(r):
    return _ek(r, [
        ("Transkripsiyon hücrenin neresinde gerçekleşir (ökaryotlarda)?", "Çekirdekte",
         ["Ribozomda", "Lizozomda", "Hücre zarında"], ["mRNA çekirdekte yapılıp sitoplazmaya geçer."]),
        ("Translasyon nerede gerçekleşir?", "Ribozomda", ["Çekirdekçikte", "Mitokondri zarında", "Golgi'de"],
         ["Protein sentezi ribozomda olur."]),
        ("Genetik bilginin ana ürünü nedir?", "Protein", ["Yağ", "Karbonhidrat", "Su"], ["Sentral dogma."]),
        ("64 kodon kaç farklı amino asidi kodlar?", "20", ["64", "4", "61"], ["Kod 'dejeneredir': bir amino asidi birden çok kodon kodlar."]),
        ("Kaç kodon durdurma kodonudur?", "3", ["1", "4", "64"], ["UAA, UAG, UGA."]),
        ("AUG kodonu hangi amino asidi kodlar?", "Metiyonin", ["Lösin", "Glisin", "Hiçbiri (durdurma)"],
         ["Başlangıç kodonudur."]),
        ("DNA'ya nükleotit ekleyerek yeni zincir yapan enzim hangisidir?", "DNA polimeraz",
         ["Helikaz", "RNA polimeraz", "Ribozom"], ["Replikasyon enzimi."]),
        ("Yarı korunumlu replikasyonu kanıtlayan bilim insanları kimlerdir?", "Meselson ve Stahl",
         ["Watson ve Crick", "Beadle ve Tatum", "Avery ve McCarty"], ["1958."]),
        ("'Bir gen – bir enzim' hipotezini kimler kurdu?", "Beadle ve Tatum",
         ["Meselson ve Stahl", "Nirenberg ve Khorana", "Hardy ve Weinberg"], ["1941."]),
        ("Genetik kodu çözen bilim insanları kimlerdir?", "Nirenberg ve Khorana",
         ["Sanger ve Gilbert", "Mendel ve Morgan", "Berg ve Boyer"], ["1966."]),
        ("Okuma çerçevesini KAYDIRMAYAN mutasyon hangisidir?", "Tek bazın başka bir bazla değişmesi",
         ["Tek baz eklenmesi", "Tek baz silinmesi", "İki baz eklenmesi"],
         ["Yalnızca 3'ün katı olmayan ekleme ve silmeler çerçeveyi kaydırır."]),
    ])


_EK = {"giris": ek_giris, "hucre": ek_hucre, "kromozom": ek_kromozom, "dongu": ek_dongu,
       "mitoz": ek_mitoz, "mayoz": ek_mayoz, "gamet": ek_gamet, "nukleik": ek_nukleik,
       "dogma": ek_dogma}


def gen_trans(r):
    dizi = "ATG" + "".join("ATGC"[int(i)] for i in r.integers(0, 4, 6))
    while any(GENETIK_KOD[dizi.replace("T", "U")[i:i + 3]] == "*" for i in (3, 6)):
        dizi = "ATG" + "".join("ATGC"[int(i)] for i in r.integers(0, 4, 6))
    mrna = dizi.replace("T", "U")
    kalip = "".join(TAMAMLAYICI[b] for b in dizi)
    n_kod = int(r.integers(5, 40))
    sabit = [
        _secim(r, f"Kodlayan DNA zinciri 5′-{dizi}-3′ ise mRNA hangisidir?", f"5′-{mrna}-3′",
               [f"5′-{''.join(_TAM_RNA[b] for b in dizi)}-3′", f"5′-{dizi}-3′", f"5′-{kalip}-3′"]
               + [f"5′-{v}-3′" for v in _bozuk(r, mrna, "AUGC")],
               ["mRNA, kodlayan zincirle aynı dizidedir; yalnızca T yerine U gelir: **" + mrna + "**"]),
        _secim(r, f"Kalıp DNA zinciri 3′-{kalip}-5′ ise mRNA hangisidir (5′→3′)?", f"5′-{mrna}-3′",
               [f"5′-{kalip.replace('T', 'U')}-3′", f"5′-{dizi}-3′", f"5′-{mrna[::-1]}-3′"]
               + [f"5′-{v}-3′" for v in _bozuk(r, mrna, "AUGC")],
               ["Kalıptaki her bazın tamamlayıcısı yazılır: A→U, T→A, G→C, C→G → **" + mrna + "**"]),
        soru_sayi(f"{n_kod} amino asitlik bir proteini kodlayan mRNA'da (durdurma kodonu dahil) en "
                  "az kaç nükleotit bulunur?", 3 * (n_kod + 1),
                  [_tx(rf"(\,{n_kod} + 1\,)\times 3 = {3 * (n_kod + 1)}"),
                   _md("Her amino asit için 3 baz + durdurma kodonu için 3 baz.")],
                  yanlis=[3 * n_kod, n_kod, 3 * n_kod + 1]),
        _secim(r, f"mRNA'daki {mrna[:3]}-{mrna[3:6]}-{mrna[6:9]} kodonlarından oluşan amino asit "
                  "dizisi hangisidir?",
               "–".join(AA_AD[GENETIK_KOD[mrna[i:i + 3]]][0] for i in (0, 3, 6)),
               ["–".join(AA_AD[GENETIK_KOD[mrna[i:i + 3]]][0] for i in (6, 3, 0)),
                "–".join(AA_AD[x][0] for x in "LAG"), "–".join(AA_AD[x][0] for x in "MKS")],
               ["Genetik kod tablosundan: " + ", ".join(
                   f"{mrna[i:i + 3]} = {AA_AD[GENETIK_KOD[mrna[i:i + 3]]][1]}" for i in (0, 3, 6))]),
    ]
    havuz = _ek(r, [
        ("Transkripsiyonu yapan enzim hangisidir?", "RNA polimeraz", ["DNA polimeraz", "Helikaz", "Ribozom"],
         ["RNA polimeraz kalıp DNA'yı okuyup mRNA yapar."]),
        ("RNA polimerazın bağlandığı, genin önündeki bölgeye ne denir?", "Promotor",
         ["Sonlandırıcı", "Kodon", "İntron"], ["Transkripsiyon promotordan başlar."]),
        ("RNA polimeraz DNA'nın hangi zincirini okur?", "Kalıp zinciri", ["Kodlayan zinciri",
                                                                          "Her iki zinciri", "Hiçbirini"],
         ["mRNA, kalıp zincire tamamlayıcıdır."]),
        ("Oluşan mRNA dizisi hangi DNA zincirine benzer?", "Kodlayan zincire (T yerine U ile)",
         ["Kalıp zincire", "Hiçbirine", "Her ikisine tamamen"], ["Bu yüzden kodlayan zincire 'anlamlı zincir' de denir."]),
        ("Kalıp DNA'daki A bazının karşısına mRNA'da hangi baz gelir?", "U", ["T", "A", "G"],
         ["RNA'da timin yoktur, urasil vardır."]),
        ("Ökaryotlarda transkripsiyon nerede gerçekleşir?", "Çekirdekte", ["Ribozomda", "Golgi'de", "Lizozomda"],
         ["mRNA çekirdekte yapılır, porlardan sitoplazmaya geçer."]),
        ("Translasyon nerede gerçekleşir?", "Ribozomda", ["Çekirdekçikte", "Çekirdek zarında", "Kofulda"],
         ["Ribozom protein sentez yeridir."]),
        ("Amino asitleri ribozoma taşıyan molekül hangisidir?", "tRNA", ["mRNA", "rRNA", "DNA"],
         ["Taşıyıcı RNA."]),
        ("tRNA'nın kodonu tanıyan bölgesine ne denir?", "Antikodon", ["Promotor", "Sentromer", "İntron"],
         ["Antikodon kodona tamamlayıcı 3 bazdır."]),
        ("Ribozomda büyüyen amino asit zincirinin bulunduğu bölge hangisidir?", "P bölgesi",
         ["A bölgesi", "Promotor", "Sentromer"], ["P: peptit bölgesi; A: yeni amino asitli tRNA'nın girdiği bölge."]),
        ("Yeni amino asidi taşıyan tRNA ribozomun hangi bölgesine gelir?", "A bölgesi",
         ["P bölgesi", "Çekirdekçik", "Kalıp zincir"], ["A: aminoasil bölgesi."]),
        ("Amino asitler birbirine hangi bağla bağlanır?", "Peptit bağı", ["Hidrojen bağı", "Fosfodiester bağı",
                                                                       "Glikozit bağı"],
         ["Protein = polipeptit zinciri."]),
        ("Translasyon hangi kodonla başlar?", "AUG", ["UAA", "UGA", "GGG"], ["AUG = metiyonin."]),
        ("A bölgesine durdurma kodonu gelince ne olur?", "Serbest bırakma faktörü bağlanır, protein ayrılır",
         ["Yeni bir tRNA gelir", "DNA kopyalanır", "Ribozom geri döner"],
         ["Durdurma kodonuna uyan tRNA yoktur."]),
        ("Ribozom her adımda mRNA üzerinde ne kadar ilerler?", "Bir kodon (3 baz)",
         ["Bir baz", "Bir gen", "İki kodon"], ["Kodonlar 3'er bazlık okunur."]),
        ("Ökaryotlarda mRNA'dan kesilip çıkarılan kodlamayan parçalara ne denir?", "İntron",
         ["Ekzon", "Kodon", "Promotor"], ["Ekzonlar birleştirilir, intronlar çıkarılır."]),
        ("Ribozom kaç alt birimden oluşur?", "2 (büyük ve küçük)", ["1", "3", "4"],
         ["Translasyon bitince alt birimler ayrılır."]),
        ("Transkripsiyonun ürünü nedir?", "RNA (ör. mRNA)", ["Protein", "DNA", "Amino asit"],
         ["DNA → RNA."]),
        ("Translasyonun ürünü nedir?", "Protein (polipeptit)", ["mRNA", "DNA", "tRNA"], ["mRNA → protein."]),
    ])
    return _tamamla(r, sabit, havuz)


# ===========================================================================
# SAYFALAR
# ===========================================================================
def sayfa_giris():
    st.title("🧬 Genetik Laboratuvarı")
    st.markdown("""
Genetiğin temel kavramlarını **şemalarla, etkileşimli çizimlerle ve bol alıştırmayla** öğrenmek
için hazırlanmış bir ders uygulaması. Bölümleri sırayla izlemeniz önerilir; her bölümün
sonunda **10, 20 ya da 30 soruluk alıştırma** ve **adım adım çözümler** var.""")
    kartlar([
        ("1 · Genetiğe giriş", "Genetik nedir, kalıtım, genom, genotip, fenotip, "
                               "ekstrakromozomal kalıtım, F = G + Ç, karakter tipleri"),
        ("2 · Tarihçe", "Hooke'tan İnsan Genom Projesi'ne etkileşimli zaman çizelgesi"),
        ("3 · Hücre", "Hayvan ve bitki hücresi, organeller ve görevleri"),
        ("4 · Kromozom", "Kromozomun yapısı, lokus, allel, homolog, dominant / resesif, homozigot / heterozigot, 2n / n, karyotip"),
        ("5 · Hücre döngüsü", "İnterfaz (G1, S, G2), G0, döngünün kontrolü"),
        ("6 · Mitoz", "Evre evre mitoz, kromozom ve kromatit sayıları, sitokinez"),
        ("7 · Mayoz", "Mayoz I ve II, krossing-over, bağımsız dağılım, gamet çeşitliliği"),
        ("8 · Gametler", "Spermatogenez, oogenez, döllenme, cinsiyetin belirlenmesi"),
        ("9 · Nükleik asitler", "Nükleotit, DNA ve RNA'nın yapısı, baz eşleşmesi"),
        ("10 · Transkripsiyon ve translasyon", "Adım adım animasyonla DNA → mRNA → protein"),
        ("11 · Replikasyon, genetik kod, mutasyon", "DNA'nın eşlenmesi, gen çevirici, mutasyon laboratuvarı"),
        ("12 · Terimler", "Sözlük, semboller ve hafıza kartları"),
        ("13 · Genel tekrar", "Tüm konulardan karışık sorular"),
    ])
    st.markdown("**Hazırlayanlar:** Emine Dilşat Yeğenoğlu & Tevfik Hasan Can")
    ipucu("Telefonda bölümleri sayfanın en üstündeki <b>Bölüm</b> kutusundan ya da sayfa "
          "sonundaki <b>Önceki / Sonraki</b> bağlantılarından seçebilirsiniz.")


# ---------------------------------------------------------------------------
def sayfa_genetige_giris():
    st.title("1 · Genetiğe giriş")
    st.header("Genetik nedir?")
    st.markdown("""
**Genetik**, kalıtım bilimidir: **genlerin yapısını ve işlevini**, kalıtsal özelliklerin
**bir dölden diğerine nasıl aktarıldığını** inceler. Canlılar arasındaki farklılıklar, büyük
ölçüde taşıdıkları **genlerdeki farklılıklardan** kaynaklanır.

Genetik bilimi üç temel soruyla ilgilenir:
1. Canlının özellikleri (karakterleri) nasıl **belirlenir**?
2. Bu özellikler bir dölden diğerine nasıl **aktarılır**?
3. Genetik materyal bugünkü hâline nasıl bir **değişimle** gelmiştir?""")

    st.header("Kalıtım")
    st.markdown("""
**Kalıtım**, canlıların kendilerine benzer yavrular oluşturması ve ortak atadan gelen
bireylerin birbirine benzemesidir. Kromozomlar üzerindeki genler **ebeveyn (P, parental)**
dölden **yavru (F, filial)** döle **gametler** (sperm ve yumurta; bitkilerde polen ve yumurta)
aracılığıyla geçer.""")
    kartlar([("🐑 Merinos koç × Merinos koyun", "→ Merinos kuzu"),
             ("🐄 Holştayn boğa × Holştayn inek", "→ Holştayn buzağı"),
             ("🍇 Asma çeliği", "Çelikle (eşeysiz) çoğaltılan asma, ana bitkinin genetik kopyasıdır")])
    st.caption("Aktarılan özelliklere örnekler: vücut yapısı, renk, boynuz ve yapağı özellikleri, "
               "yemden yararlanma yeteneği…")

    st.header("Farklılıkların (varyasyonun) kaynakları")
    svg_goster(svg_varyasyon_kaynaklari())
    st.markdown("""
- **Mutasyon:** Genetik materyalde (DNA dizisinde) meydana gelen **kalıtsal** değişim. Bu
  değişikliği taşıyan bireye **mutant** denir.
- **Rekombinasyon:** Mayoz bölünmede homolog kromozomlar arasında parça değişimi
  (**krossing-over**) ve kromozomların bağımsız dağılımıyla **yeni allel kombinasyonları**
  oluşması.
- **Seleksiyon:** Popülasyonda belirli genotiplerin seçilip daha çok yavru bırakması
  (doğada **doğal seçilim**, ıslahta **yapay seçilim**).""")
    uyari("<b>Mutasyon ≠ Modifikasyon.</b> Modifikasyon, çevrenin etkisiyle ortaya çıkan ve "
          "genleri değiştirmeyen, <b>kalıtsal olmayan</b> değişimdir. Örnek: iyi beslenen bir "
          "koyunun daha iri olması yavrularına geçmez.")

    st.header("Karakter tipleri: kalitatif ve kantitatif")
    c1, c2 = st.columns(2)
    with c1:
        kutu("<b>Kalitatif (niteleyici) karakterler</b><br>"
             "• Kesin sınıflara ayrılır, <b>sayılarak</b> sınıflandırılır: siyah / beyaz, "
             "boynuzlu / boynuzsuz, kan grubu<br>"
             "• Bir ya da birkaç gen tarafından kontrol edilir<br>"
             "• Çevreden çok az etkilenir ya da hiç etkilenmez")
    with c2:
        kutu("<b>Kantitatif (nicel) karakterler</b><br>"
             "• <b>Ölçülerek</b> ifade edilir: süt, yumurta, yapağı verimi, canlı ağırlık<br>"
             "• Kesin sınıflara ayrılamaz, sürekli dağılım gösterir<br>"
             "• Çok sayıda gen (<b>poligenik</b>) ve çevre tarafından etkilenir")
    st.subheader("🔬 Deney: gen sayısı ve çevre arttıkça dağılım nasıl değişir?")
    st.caption("Her gen iki allelli ve eklemeli kabul edilmiştir: her 'büyük harf' allel "
               "özelliğe 1 birim katkı yapar. 4000 bireylik kurgusal bir popülasyon.")
    c1, c2 = st.columns(2)
    k = c1.slider("Özelliği etkileyen gen sayısı", 1, 10, 1)
    sigma = c2.slider("Çevrenin etkisi (dağılımı bulandırma)", 0.0, 2.0, 0.0, 0.1)
    rr = np.random.default_rng(42)
    deger = rr.binomial(2 * k, 0.5, 4000) + rr.normal(0, sigma, 4000)
    fig = go.Figure(go.Histogram(x=deger, nbinsx=max(12, 4 * k + 6), marker_color=MAVI))
    fig.update_layout(title=f"{k} gen, çevre etkisi {sigma}: {2 * k + 1} genotip sınıfı",
                      xaxis_title="Özelliğin değeri (birim)", yaxis_title="Birey sayısı",
                      bargap=0.05)
    ciz(fig, 340)
    kutu("Tek gen ve çevre etkisi yokken birbirinden ayrı <b>3 sınıf</b> görülür (kalitatif). "
         "Gen sayısı ve çevre etkisi arttıkça sınıflar birbirine karışır ve <b>çan eğrisi</b> "
         "şeklinde sürekli bir dağılım oluşur (kantitatif). Gen sayısı k ise genotip sınıfı "
         "sayısı <b>2k + 1</b>'dir.")

    st.header("Temel terimler: genom, gen, genotip, fenotip")
    svg_goster(svg_genom())
    st.markdown("""
- **Genom:** Bir canlının taşıdığı **genetik materyalin tamamı**. Ökaryotlarda çekirdekteki
  kromozomların DNA'sı (**çekirdek genomu**) ile mitokondri ve bitkilerde kloroplastın küçük
  halkasal DNA'sından (**organel genomu**) oluşur. Örnek: İnsan genomu yaklaşık **3 milyar baz
  çifti** ve yaklaşık **20 000** protein kodlayan gen içerir.
- **Gen:** Genomun, bir özelliğin (bir proteinin ya da işlevsel bir RNA'nın) yapım bilgisini
  taşıyan parçası. Kalıtımın birimidir.
- **Karakter (özellik):** Canlıda incelenen herhangi bir özellik: tohum rengi, boy, süt verimi,
  kan grubu…""")
    svg_goster(svg_genotip_fenotip())
    st.markdown("""
- **Genotip:** Bireyin incelenen gen(ler) için taşıdığı **allellerin bileşimi**. Sembollerle
  yazılır: **AA, Aa, aa**. Gözle görülmez.
- **Fenotip:** Bir canlının **gözlemlenebilir ve ölçülebilir** bütün özellikleridir. Genotip ile
  çevrenin ortak ürünüdür. Fenotip yalnızca gözle görülen dış görünüş değildir; dört grupta
  incelenir:""")
    kartlar([("🌿 Morfolojik", "Biçim ve yapı: tohum rengi ve şekli, boy, yaprak biçimi, tüy rengi, boynuz"),
             ("⚙️ Fizyolojik", "Vücudun işleyişi: süt verimi, büyüme hızı, yumurta verimi, kuraklığa ve "
                              "soğuğa dayanıklılık"),
             ("🧪 Biyokimyasal", "Moleküler düzey: kan grubu, enzim aktivitesi, süt proteini tipi, "
                                "antosiyanin ve yağ asidi içeriği"),
             ("🐄 Davranışsal", "Davranış: mizaç (uysallık), annelik davranışı, kuluçkaya yatma, sürü içi davranış")])
    st.caption("Kan grubu ya da bir enzimin aktivitesi gözle görülmez ama laboratuvarda ölçülebilir; bu yüzden "
               "bunlar da fenotiptir.")
    kartlar([("🧬 Genotip", "Aa · içerik, 'tarif'"),
             ("👀 Fenotip", "Sarı tohum · görünen sonuç, 'yemek'"),
             ("🌦️ Çevre", "Besleme, bakım, iklim · 'aşçının mutfağı'")])
    st.caption("Benzetme: genotip bir yemek tarifiyse fenotip ortaya çıkan yemektir; aynı tarif "
               "farklı mutfaklarda biraz farklı sonuç verebilir.")

    st.subheader("Ekstrakromozomal (sitoplazmik) kalıtım")
    svg_goster(svg_ekstrakromozomal())
    st.markdown("""
Kalıtımın büyük kısmı çekirdekteki kromozomlarla olur. Ama mitokondri ve kloroplastın kendi
DNA'sı olduğu için bazı özellikler **kromozom dışı** yolla kalıtılır: buna **ekstrakromozomal
(sitoplazmik) kalıtım** denir.
- Zigotun sitoplazması ve organelleri büyük ölçüde **yumurtadan** gelir; sperm hemen hiç
  sitoplazma getirmez. Bu yüzden bu özellikler genellikle **anneden** kalıtılır (**maternal
  kalıtım**).
- Yavrular annenin özelliğini gösterir; **Mendel oranlarına uymaz** ve resiprokal
  (karşılıklı) çaprazlamalarda farklı sonuç verir.
- İlk örnek: **Carl Correns (1909)**, akşam sefası (*Mirabilis jalapa*) bitkisinde yaprak
  alacalığının (yeşil / beyaz) yalnızca **ana bitkiye** göre kalıtıldığını gösterdi. Nedeni
  kloroplast DNA'sıdır.
- İnsanda bazı kalıtsal hastalıklar mitokondriyal DNA'daki mutasyonlardan kaynaklanır ve
  anneden çocuklarına geçer.""")

    st.header("Fenotip = Genotip + Çevre")
    st.markdown("""
**Fenotip**, bir canlının gözlemlenebilir ve ölçülebilir (morfolojik, fizyolojik, biyokimyasal,
davranışsal) özelliklerinin tamamıdır ve **genotip ile çevrenin ortak etkisiyle** oluşur. Genotip özelliğin **sınırlarını (potansiyelini)** belirler; çevre (besleme,
bakım, iklim, hastalık) bu potansiyelin ne kadarının ortaya çıkacağını etkiler.""")
    st.latex(r"F = G + \text{Ç}")
    st.latex(r"F = G + \text{Ç} + (G \times \text{Ç})")
    kartlar([("F (fenotip)", "Gözlenen / ölçülen değer: ör. ineğin bir laktasyondaki süt verimi"),
             ("G (genotip değeri)", "Genlerin fenotipe katkısı; hayvanın kalıtsal potansiyeli"),
             ("Ç (çevre etkisi)", "Besleme, bakım, iklim, hastalık… Olumlu ya da olumsuz olabilir; "
                                  "kalıtsal değildir"),
             ("G × Ç (etkileşim)", "Çevrenin etkisinin genotipe göre değişmesi")])
    c1, c2 = st.columns([1, 1.2])
    with c1:
        g = st.slider("İneğin genetik potansiyeli (G, kg süt / laktasyon)", 3000, 11000, 8000, 250)
        c = st.slider("Çevrenin etkisi (Ç: besleme ve bakım, kg)", -3000, 1500, -1000, 250)
        st.metric("Gözlenen süt verimi (fenotip)", f"{g + c:,} kg".replace(",", "."))
        st.caption("Sayılar öğretim amaçlı kurgusaldır.")
    with c2:
        fig = go.Figure()
        fig.add_bar(x=["Genotip (G)", "Çevre (Ç)", "Fenotip (F)"], y=[g, c, g + c],
                    marker_color=[MAVI, YESIL if c >= 0 else PEMBE, MOR],
                    text=[g, c, g + c], textposition="outside")
        fig.update_layout(title="F = G + Ç", yaxis_title="kg")
        ciz(fig, 320)
    st.subheader("Genotip × çevre etkileşimi (G×Ç)")
    fig = go.Figure()
    fig.add_scatter(x=["Kötü bakım", "İyi bakım"], y=[3800, 9500], name="Holştayn (kültür ırkı)",
                    mode="lines+markers+text", text=["3800", "9500"], textposition="top center",
                    line=dict(color=MAVI, width=4))
    fig.add_scatter(x=["Kötü bakım", "İyi bakım"], y=[3000, 3600], name="Yerli ırk",
                    mode="lines+markers+text", text=["3000", "3600"], textposition="bottom center",
                    line=dict(color=TURUNCU, width=4))
    fig.update_layout(title="Aynı çevre değişikliğine iki genotip farklı tepki veriyor (kurgusal)",
                      yaxis_title="Süt verimi (kg)")
    ciz(fig, 330)
    kutu("İyi bakım kültür ırkının verimini çok artırırken yerli ırkta etki küçük kalıyor. "
         "Çevrenin etkisinin genotipe göre değişmesine <b>genotip × çevre etkileşimi</b> denir. "
         "Bu yüzden 'en iyi ırk / çeşit' her çevrede aynı olmayabilir.")

    st.header("Genetiğin uygulama alanları")
    kartlar([("Mendel genetiği", "Özelliklerin dölden döle geçiş kuralları (1865, Gregor Mendel, "
                                 "bezelye deneyleri)"),
             ("Popülasyon genetiği", "Popülasyonlardaki allel ve genotip frekansları, Hardy-Weinberg"),
             ("Kantitatif genetik", "Verim gibi ölçülebilen, poligenik özelliklerin kalıtımı"),
             ("Moleküler genetik", "DNA, RNA, genlerin yapısı ve ifadesi, biyoteknoloji")])
    st.markdown("""
**Hayvan genetiği**, hayvanlarda kalıtım kurallarını inceler. **Hayvan yetiştiriciliği** ise bu
kuralları hayvanları **ıslah etmek** (daha verimli hâle getirmek) için uygular. Bitkilerde de
aynı ilişki **bitki genetiği** ile **bitki ıslahı** arasında vardır. Bu alanlar birbirinin
ayrılmaz parçalarıdır.""")
    alistirma_blogu("giris", "Genetiğe giriş", gen_giris)


# ---------------------------------------------------------------------------
def sayfa_tarihce():
    st.title("2 · Genetiğin tarihçesi")
    st.markdown("Zaman çizelgesindeki noktaların üzerine gelerek (telefonda dokunarak) olayları "
                "okuyabilirsiniz.")
    df = pd.DataFrame(TARIHCE, columns=["Yıl", "Kişi", "Olay", "Alan"])
    alanlar = sorted(df["Alan"].unique())
    secili = st.multiselect("Alan seçin", alanlar, default=alanlar)
    d = df[df["Alan"].isin(secili)].reset_index(drop=True)
    renkler = {a: c for a, c in zip(alanlar, [MAVI, PEMBE, YESIL, TURUNCU, MOR, GRI_K, "#17BECF",
                                              "#BCBD22", "#8C564B", "#E377C2"])}
    fig = go.Figure()
    for a in secili:
        dd = d[d["Alan"] == a]
        y = [((i % 4) - 1.5) for i in dd.index]
        fig.add_scatter(x=dd["Yıl"], y=y, mode="markers", name=a,
                        marker=dict(size=14, color=renkler[a], line=dict(color="white", width=1)),
                        text=[f"<b>{r.Yıl}</b> · {r.Kişi}<br>{r.Olay}" for r in dd.itertuples()],
                        hovertemplate="%{text}<extra></extra>")
    fig.update_layout(title="Genetik biliminde zaman çizelgesi", yaxis=dict(visible=False),
                      xaxis_title="Yıl", hoverlabel=dict(align="left"))
    ciz(fig, 360)
    donem = st.select_slider("Dönem", ["Tümü", "1665–1899", "1900–1949", "1950–1979", "1980–2007"],
                             value="Tümü")
    sinir = {"1665–1899": (1600, 1899), "1900–1949": (1900, 1949), "1950–1979": (1950, 1979),
             "1980–2007": (1980, 2100), "Tümü": (0, 3000)}[donem]
    for r in d.itertuples():
        if sinir[0] <= r.Yıl <= sinir[1]:
            st.markdown(f'<div class="zaman"><b class="yil">{r.Yıl}</b> · <b>{r.Kişi}</b><br>'
                        f'{r.Olay}</div>', unsafe_allow_html=True)
    ipucu("Mendel çalışmalarını 1865'te sundu ama değeri ancak <b>1900</b>'de üç bilim insanı "
          "tarafından yeniden keşfedilince anlaşıldı. Bu yüzden 1900 yılı modern genetiğin "
          "başlangıcı kabul edilir.")
    alistirma_blogu("tarih", "Tarihçe", gen_tarih)


# ---------------------------------------------------------------------------
def sayfa_hucre():
    st.title("3 · Hücre")
    st.markdown("""
1665'te **Robert Hooke** mantar dokusunu incelerken gördüğü küçük boşluklara **hücre** dedi.
Hücre biliminin temeli ise **Schleiden** (1838, bitkiler) ve **Schwann**'ın (1839, hayvanlar)
**hücre teorisine** dayanır. Bugünkü anlamıyla hücre teorisi:""")
    kartlar([("1", "Bütün canlılar bir ya da daha çok hücreden oluşur."),
             ("2", "Hücre, canlının en küçük yapısal ve işlevsel birimidir."),
             ("3", "Hücreler, kendilerinden önceki hücrelerin bölünmesiyle oluşur."),
             ("4", "Canlıların kalıtım materyali (DNA) hücrelerde bulunur.")])
    st.header("Hayvan ve bitki hücresi")
    tur = st.radio("Hücre tipi", ["Hayvan", "Bitki"], horizontal=True)
    liste = HAYVAN_ORGANEL if tur == "Hayvan" else BITKI_ORGANEL
    adlar = ["— Tümünü göster —"] + [f"{i}. {ORGANELLER[k][0]}" for i, k in enumerate(liste, 1)]
    sec = st.selectbox("Bir yapı seçin, şemada vurgulansın", adlar)
    secili = None if sec.startswith("—") else liste[int(sec.split(".")[0]) - 1]
    c1, c2 = st.columns([1.35, 1])
    with c1:
        svg_goster(svg_hucre(tur, secili))
    with c2:
        if secili:
            ad, acik = ORGANELLER[secili]
            st.subheader(ad)
            st.markdown(acik)
        else:
            for i, k in enumerate(liste, 1):
                st.markdown(f"**{i}. {ORGANELLER[k][0]}:** {ORGANELLER[k][1]}")
    st.caption("Şemalar ölçeksizdir; yapıların büyüklükleri ve sayıları temsilîdir.")
    st.header("Hücrenin üç temel kısmı")
    kartlar([("Hücre zarı", "Hücreyi dış ortamdan ayıran, seçici geçirgen, esnek zar"),
             ("Sitoplazma", "Organellerin bulunduğu, hücre zarı ile çekirdek arasındaki sıvı ortam"),
             ("Çekirdek", "Çekirdek zarı, çekirdek sıvısı (nükleoplazma), çekirdekçik ve kromatin")])
    st.header("Bitki, mantar ve hayvan hücreleri arasındaki farklar")
    tablo(pd.DataFrame({
        "Özellik": ["Hücre çeperi", "Büyük merkezi koful", "Plastit (kloroplast)",
                    "Depo karbonhidratı", "Sentriyol"],
        "Bitki hücresi": ["Var (selüloz)", "Var", "Var", "Nişasta", "Yok"],
        "Mantar hücresi": ["Var (çoğunlukla kitin)", "Var", "Yok", "Glikojen", "Genellikle yok"],
        "Hayvan hücresi": ["Yok", "Yok (küçük kofullar olabilir)", "Yok", "Glikojen", "Var"]}))
    ipucu("<b>Genetik bağlantı:</b> DNA yalnızca çekirdekte değildir. Mitokondri ve kloroplastın "
          "da kendi küçük DNA'ları vardır. Bunlar çoğunlukla <b>anneden</b> (yumurtanın "
          "sitoplazmasıyla) kalıtılır.")
    alistirma_blogu("hucre", "Hücre", gen_hucre)


# ---------------------------------------------------------------------------
def sayfa_kromozom():
    st.title("4 · Kromozom")
    st.markdown("""
Çekirdekteki DNA, proteinlerle birlikte **kromatin** hâlinde bulunur. Hücre bölünürken kromatin
kısalıp kalınlaşır ve mikroskopta görülebilen **kromozomları** oluşturur. DNA eşlendikten sonra
her kromozom, **sentromerden** birbirine bağlı iki özdeş **kardeş kromatitten** oluşur.""")
    svg_goster(svg_kromozom_yapisi())
    kartlar([("Sentromer", "Kardeş kromatitlerin birleştiği boğum; iğ iplikleri buraya "
                           "(kinetokor) bağlanır"),
             ("p ve q kolları", "Sentromerin iki yanındaki kısa (p) ve uzun (q) kollar"),
             ("Telomer", "Kromozom uçlarındaki koruyucu tekrar dizileri"),
             ("Kardeş kromatit", "Replikasyonla oluşan iki özdeş DNA kopyası")])
    st.header("Gen, lokus, allel: kromozom üzerindeki adresler")
    svg_goster(svg_kavram_haritasi())
    st.markdown("""
- **Gen:** Bir özelliğin (ör. tohum rengi) yapım bilgisini taşıyan DNA parçası.
- **Lokus:** Genin kromozom üzerindeki **yeri, adresi**. Homolog kromozomlarda aynı gen
  **aynı lokusta** bulunur.
- **Allel:** Aynı genin **farklı biçimleri** (ör. sarı tohum alleli **A**, yeşil tohum
  alleli **a**). Allel genler homologların **karşılıklı lokuslarında** bulunur.""")
    st.subheader("Homolog kromozomlar ve lokuslar")
    svg_goster(svg_homolog_lokus())
    st.markdown("""
**Homolog kromozomlar**, biri anneden biri babadan gelen; **aynı boyda, aynı sentromer
konumunda ve aynı genleri aynı sırayla** taşıyan kromozom çiftidir. Genler aynıdır ama
**alleller farklı olabilir**: yukarıda A lokusunda anneden **A**, babadan **a** gelmiştir.""")
    st.subheader("Homozigot ve heterozigot")
    svg_goster(svg_genotipler())
    kartlar([("AA · homozigot dominant", "İki allel aynı ve dominant (arı döl)"),
             ("Aa · heterozigot", "İki allel farklı (melez)"),
             ("aa · homozigot resesif", "İki allel aynı ve resesif (arı döl)")])
    uyari("Homozigot / heterozigot <b>bir lokusa göre</b> söylenir. Aynı birey A lokusunda "
          "heterozigot (Aa), B lokusunda homozigot (BB) olabilir.")
    st.subheader("Dominant ve resesif")
    svg_goster(svg_genotip_fenotip())
    st.markdown("""
- **Dominant (baskın) allel:** Heterozigot durumda da etkisini gösterir; **büyük harfle**
  yazılır (A).
- **Resesif (çekinik) allel:** Etkisini yalnızca **homozigot** olduğunda (aa) gösterir; **küçük
  harfle** yazılır (a).
- Bu yüzden **AA** ve **Aa** aynı fenotipi (sarı) verir: **genotip farklı, fenotip aynı**.""")
    with st.expander("🔬 Alleller DNA düzeyinde nasıl farklıdır? Baskınlık nasıl oluşur?"):
        st.markdown(html_snp(), unsafe_allow_html=True)
        st.markdown(html_baskinlik_mekanizma(), unsafe_allow_html=True)

    st.header("Homolog kromozomlar, diploit ve haploit")
    st.markdown("""
- Bir türdeki farklı kromozomların bir takımına **n** denir. Vücut hücrelerinde her kromozomdan
  **iki** tane bulunur: **2n (diploit)**. Biri anneden, biri babadan gelir; bu çiftlere
  **homolog kromozomlar** denir.
- Gametler (sperm, yumurta, polen) her kromozomdan **tek** taşır: **n (haploit)**.
- Döllenmede n + n = **2n** olur; böylece kromozom sayısı kuşaklar boyunca sabit kalır.""")
    c1, c2 = st.columns([1, 1.3])
    with c1:
        tur = st.selectbox("Bir tür seçin", list(TURLER), index=7)
        n2 = TURLER[tur]
        st.metric("Vücut hücresi (2n)", n2)
        st.metric("Gamet (n)", n2 // 2)
        st.metric("Homolog çift sayısı", n2 // 2)
    with c2:
        st.markdown("**Bir canlı kaç farklı gamet yapabilir?**")
        st.markdown("Mayozda her homolog çiftin hangi üyesinin hangi gamete gideceği rastgeledir. "
                    "Krossing-over hiç hesaba katılmasa bile:")
        st.latex(rf"2^{{n}} = 2^{{{n2 // 2}}} = {2 ** (n2 // 2):,}"
                 .replace(",", r"\,"))
        st.caption("Krossing-over bu sayıyı çok daha da artırır.")
    tablo(pd.DataFrame({"Tür": list(TURLER), "2n": list(TURLER.values()),
                        "n": [v // 2 for v in TURLER.values()]}))
    st.caption("Bal arısında erkekler (erkek arılar) döllenmemiş yumurtadan gelişir ve haploittir "
               "(n = 16). Ekmeklik buğday heksaploittir (2n = 6x = 42). Kromozom sayısı ile "
               "canlının gelişmişliği arasında bir ilişki yoktur.")
    st.header("İnsan karyotipi: otozomlar ve eşey kromozomları")
    cins = st.radio("Karyotip", ["Erkek (XY)", "Dişi (XX)"], horizontal=True)
    svg_goster(svg_karyotip(cins))
    st.caption("Şematik çizim; kromozom boyları ve sentromer yerleri yaklaşıktır. Mavi: anneden, "
               "pembe: babadan.")
    st.markdown("""
İnsan vücut hücresinde **46 kromozom (2n = 46)** vardır: **23 anneden, 23 babadan**.
- **22 çift otozom:** Cinsiyetin belirlenmesinde rol almayan kromozomlar.
- **1 çift gonozom (eşey kromozomu):** Dişi **XX**, erkek **XY**.""")
    alistirma_blogu("kromozom", "Kromozom", gen_kromozom)


# ---------------------------------------------------------------------------
def sayfa_dongu():
    st.title("5 · Hücre döngüsü")
    st.markdown("""
Bütün hücreler önceki hücrelerin bölünmesiyle oluşur. Bölünen bir hücrenin yaşamı iki ana
dönemden oluşur: **interfaz** (büyüme ve hazırlık) ve **bölünme (M evresi)**. Bölünen tipik bir
memeli hücresinde döngü yaklaşık **24 saat** sürer.""")
    c1, c2 = st.columns([1, 1.1])
    with c1:
        svg_goster(svg_hucre_dongusu())
    with c2:
        tablo(pd.DataFrame({
            "Evre": ["G1", "S", "G2", "M", "G0"],
            "Ne olur?": ["Hücre büyür, organeller ve proteinler çoğalır; S evresine hazırlanır",
                         "DNA eşlenir (replikasyon): her kromozom iki kromatitli olur",
                         "Bölünmeye son hazırlık; gerekli proteinler sentezlenir",
                         "Mitoz (çekirdek bölünmesi) + sitokinez (sitoplazma bölünmesi)",
                         "Bölünmeyen hücrelerin döngüden çıkıp beklediği evre (ör. sinir, kas "
                         "hücreleri)"],
            "Yaklaşık süre": ["6–12 saat", "6–8 saat", "3–4 saat", "≈1 saat", "değişken"]}))
    st.subheader("Döngü boyunca hücredeki DNA miktarı")
    t = [0, 10, 17, 21, 22, 22.01, 24]
    c = [2, 2, 4, 4, 4, 2, 2]
    fig = go.Figure(go.Scatter(x=t, y=c, mode="lines", line=dict(color=MAVI, width=4),
                               fill="tozeroy", fillcolor="rgba(59,111,182,0.12)"))
    for x0, x1, ad, renk in ((0, 10, "G1", "#8CC8A8"), (10, 17, "S", "#7EA6E0"),
                             (17, 21, "G2", "#F5C77E"), (21, 22, "M", "#E8828F")):
        fig.add_vrect(x0=x0, x1=x1, fillcolor=renk, opacity=0.25, line_width=0,
                      annotation_text=ad, annotation_position="top left")
    fig.update_layout(xaxis_title="Saat", yaxis_title="DNA miktarı (c)",
                      yaxis=dict(tickvals=[2, 4], ticktext=["2c", "4c"], range=[0, 4.8]),
                      title="S evresinde DNA iki katına çıkar, bölünmeyle yarıya iner")
    ciz(fig, 320)
    st.caption("c: haploit bir hücredeki DNA miktarı. Diploit hücrede G1'de 2c, G2'de 4c DNA vardır.")
    st.header("Döngü nasıl kontrol edilir?")
    st.markdown("""
Hücre bir sonraki evreye geçmeden önce **kontrol noktalarında** her şeyin yolunda olup
olmadığını denetler:
- **G1/S kontrol noktası:** Hücre yeterince büyüdü mü, DNA'da hasar var mı?
- **G2/M kontrol noktası:** DNA tam ve hatasız eşlendi mi?
- **Metafaz kontrol noktası:** Bütün kromozomlar iğ ipliklerine doğru bağlandı mı?

Bu geçişleri **siklin** adı verilen proteinler ile onların etkinleştirdiği **siklin bağımlı
kinazlar (CDK)** yönetir. Siklinleri anahtara, CDK'ları motora benzetebiliriz: anahtar
takılınca motor çalışır, hücre bir sonraki evreye geçer.""")
    with st.expander("📚 İleri bilgi: siklin–CDK çiftleri ve RB proteini"):
        tablo(pd.DataFrame({
            "Siklin – CDK": ["Siklin D – CDK4/6", "Siklin E – CDK2", "Siklin A – CDK2",
                             "Siklin B – CDK1"],
            "Görev": ["G1 ilerlemesi; RB proteinini fosforlar", "G1/S geçişi",
                      "S evresi ilerlemesi, G2/M'ye hazırlık", "G2/M geçişi (mitoza giriş)"]}))
        st.markdown("""
- Siklinler döngünün belirli evrelerinde sentezlenir (sırasıyla D, E, A, B) ve görevleri
  bitince hızla yıkılır.
- **RB proteini** fosforlanınca E2F adlı proteini serbest bırakır; E2F, DNA eşlenmesi için
  gerekli genleri (DNA polimeraz, timidin kinaz vb.) çalıştırır. Bu adım döngünün
  moleküler "başlat" anahtarıdır.
- **CDK inhibitörleri** (Cip/Kip ve INK4 aileleri) döngüyü frenler; **tümör baskılayıcı** gibi
  davranırlar.""")
    uyari("Bu kontrol sistemi bozulursa hücreler kontrolsüz çoğalabilir: <b>kanser</b> böyle "
          "ortaya çıkar. DNA eşlenmesindeki (S evresi) hatalar da hücre ölümüne ya da kansere "
          "yol açabilir.")
    alistirma_blogu("dongu", "Hücre döngüsü", gen_dongu)


# ---------------------------------------------------------------------------
_MITOZ_ACIKLAMA = {
    "İnterfaz": "Bölünme öncesi hazırlık. DNA S evresinde eşlenir; kromatin gevşek olduğu için "
                "kromozomlar tek tek görülmez. Sentrozom da eşlenir.",
    "Profaz": "Kromatin kısalıp kalınlaşır, kromozomlar görünür hâle gelir (her biri iki kardeş "
              "kromatitli). Sentrozomlar zıt kutuplara gider, iğ iplikleri oluşmaya başlar. "
              "Çekirdekçik kaybolur.",
    "Prometafaz": "Çekirdek zarı tamamen dağılır. İğ iplikleri kromozomların sentromer "
                  "bölgesindeki kinetokorlara bağlanır.",
    "Metafaz": "Kromozomlar hücrenin ekvatorunda (metafaz plağı) tek sıra hâlinde dizilir. "
               "Kromozomların en net görüldüğü evredir; kromozom sayımı ve karyotip bu evrede "
               "yapılır.",
    "Anafaz": "En hızlı evredir. Sentromerler ayrılır; kardeş kromatitler iğ iplikleriyle zıt "
              "kutuplara çekilir. Ayrılan her kromatit artık bir kromozomdur.",
    "Telofaz": "Kutuplara ulaşan kromozomların etrafında yeni çekirdek zarları oluşur, "
               "çekirdekçik yeniden belirir, kromozomlar gevşeyerek kromatine dönüşür. İğ "
               "iplikleri kaybolur.",
    "Sitokinez": "Sitoplazma bölünür ve genetik olarak birbirinin aynı (ana hücreyle de aynı) "
                 "iki yavru hücre oluşur.",
}


def _mitoz_sayilari(n2):
    return pd.DataFrame({
        "Evre": ["G1", "G2 / Profaz / Metafaz", "Anafaz (hücrenin tamamı)", "Telofaz sonrası "
                 "(her yavru hücre)"],
        "Kromozom": [n2, n2, 2 * n2, n2],
        "Kromatit": [n2, 2 * n2, 2 * n2, n2],
        "DNA": ["2c", "4c", "4c", "2c"]})


def sayfa_mitoz():
    st.title("6 · Mitoz")
    st.markdown("""
**Mitoz**, vücut (somatik) hücrelerinin bölünmesidir. Bir hücreden **genetik olarak birbirinin
aynı iki hücre** oluşur; kromozom sayısı değişmez (**2n → 2n**). Büyüme, yaralanan dokuların
onarımı ve eşeysiz üreme (ör. **asmanın çelikle çoğaltılması**) mitozla gerçekleşir.""")
    st.subheader("Evre evre mitoz")
    st.caption("Örnek hücre: 2n = 4 (uzun ve kısa iki homolog çift). Mavi: anneden, pembe: "
               "babadan gelen kromozom.")
    evre = st.select_slider("Evreyi seçin (kaydırın)", MITOZ_EVRELERI, value="Metafaz")
    c1, c2 = st.columns([1.4, 1])
    with c1:
        svg_goster(svg_mitoz(evre))
    with c2:
        st.subheader(evre)
        st.markdown(_MITOZ_ACIKLAMA[evre])
    st.subheader("Kromozom ve kromatit sayıları")
    tur = st.selectbox("Tür", list(TURLER), index=0, key="mitoz_tur")
    tablo(_mitoz_sayilari(TURLER[tur]))
    kutu("Kardeş kromatitler sentromerden bağlıyken <b>tek kromozom</b> sayılır. Anafazda "
         "ayrıldıkları an her biri ayrı bir kromozom olur; bu yüzden anafazda hücredeki kromozom "
         "sayısı geçici olarak <b>iki katına</b> çıkar.")
    st.header("Sitokinez: hayvan ve bitki hücresinde")
    svg_goster(svg_sitokinez_karsilastir())
    st.markdown("""
**Hatırlatma:** Bazı basit yapılı tek hücrelilerde ve bazı kanser hücrelerinde görülen, çekirdek
zarının kaybolmadığı doğrudan bölünmeye **amitoz** denir. Bakteriler gibi çekirdeksiz canlılar
ise **ikiye bölünme** ile çoğalır.""")
    alistirma_blogu("mitoz", "Mitoz", gen_mitoz)


# ---------------------------------------------------------------------------
_MAYOZ_ACIKLAMA = {
    "Profaz I": "Homolog kromozomlar boylu boyunca eşleşir (sinaps) ve 4 kromatitli tetradları "
                "oluşturur. Homolog kromatitler arasında parça değişimi (krossing-over) olur; "
                "değişim noktalarına kiazma denir.",
    "Metafaz I": "Tetradlar (homolog çiftler) ekvatorda karşılıklı dizilir. Her çiftin hangi "
                 "üyesinin hangi kutba bakacağı rastgeledir (bağımsız dağılım).",
    "Anafaz I": "HOMOLOG kromozomlar birbirinden ayrılıp zıt kutuplara gider. Kardeş "
                "kromatitler hâlâ sentromerden bağlıdır.",
    "Telofaz I": "İki hücre oluşur. Her hücrede kromozom sayısı yarıya inmiştir (n), ama "
                 "kromozomlar hâlâ iki kromatitlidir. Mayoz I 'indirgeme bölünmesidir'.",
    "Profaz II": "İki bölünme arasında DNA eşlenmez. Her hücrede yeni iğ iplikleri oluşur.",
    "Metafaz II": "Kromozomlar her hücrenin ekvatorunda tek sıra dizilir (mitozdaki gibi).",
    "Anafaz II": "Sentromerler ayrılır; kardeş kromatitler zıt kutuplara gider.",
    "Telofaz II": "Sonuçta 4 haploit (n) hücre oluşur. Krossing-over ve bağımsız dağılım "
                  "nedeniyle bu hücreler genetik olarak birbirinden farklıdır.",
}


def _mayoz_dizilim_karistir():
    st.session_state.mayoz_dizilim = (int(rng().integers(0, 2)), int(rng().integers(0, 2)))


def sayfa_mayoz():
    st.title("7 · Mayoz")
    st.markdown("""
**Mayoz**, eşey ana hücrelerinde (hayvanlarda testis ve yumurtalıkta, bitkilerde çiçeğin
üreme organlarında) gamet oluşturmak için görülen bölünmedir.
- Arka arkaya **iki bölünme** olur: **Mayoz I** ve **Mayoz II**.
- Bir diploit (2n) hücreden **dört haploit (n)** hücre oluşur.
- Kromozom sayısını yarıya indirir; böylece döllenmede (n + n = 2n) türün kromozom sayısı
  **sabit** kalır. Mayoz olmasaydı her kuşakta kromozom sayısı iki katına çıkardı!""")
    st.subheader("Evre evre mayoz")
    if "mayoz_dizilim" not in st.session_state:
        st.session_state.mayoz_dizilim = (0, 1)
    c1, c2 = st.columns(2)
    krossing = c1.toggle("Krossing-over göster", value=True)
    c2.button("🔀 Bağımsız dağılım: kromozomları yeniden diz", on_click=_mayoz_dizilim_karistir)
    evre = st.select_slider("Evreyi seçin (kaydırın)", MAYOZ_EVRELERI, value="Metafaz I")
    c1, c2 = st.columns([1.4, 1])
    with c1:
        svg_goster(svg_mayoz(evre, st.session_state.mayoz_dizilim, krossing))
    with c2:
        st.subheader(evre)
        st.markdown(_MAYOZ_ACIKLAMA[evre])
    st.caption("Örnek hücre: 2n = 4. 'Yeniden diz' düğmesine basıp Telofaz II'ye bakın: gametlerin "
               "kromozom bileşimi değişir.")
    st.subheader("Profaz I'in alt evreleri")
    tablo(pd.DataFrame({
        "Alt evre": ["1. Leptoten", "2. Zigoten", "3. Pakiten", "4. Diploten", "5. Diakinez"],
        "Olaylar": ["Kromozomlar ince iplikler hâlinde görünmeye başlar",
                    "Homolog kromozomlar eşleşmeye başlar (sinaps)",
                    "Eşleşme tamamlanır, tetradlar belirgindir; krossing-over bu evrede olur",
                    "Homologlar ayrılmaya başlar; kiazmalar görünür hâle gelir",
                    "Kromozomlar en kısa ve kalın hâlini alır; çekirdekçik ve çekirdek zarı "
                    "kaybolur"]}))
    st.caption("Sırayı hatırlamak için: Le-Zi-Pa-Di-Di")
    st.header("Krossing-over: yeni allel kombinasyonları")
    st.markdown("Bir homolog çiftte anneden gelen kromozom **A B C D E F**, babadan gelen "
                "**a b c d e f** allellerini taşısın. Kırılma noktasını değiştirin:")
    nokta = st.slider("Kırılma noktası (soldan kaçıncı genden sonra?)", 1, 5, 3)
    svg_goster(svg_krossing(nokta))
    kutu("Tek bir krossing-overda tetraddaki 4 kromatitten <b>2'si rekombinant</b>, 2'si ata "
         "tipidir. İki gen birbirinden ne kadar uzaksa aralarında kırılma olma olasılığı o kadar "
         "artar. Rekombinasyon oranı en fazla <b>%50</b> olabilir (bağımsız dağılan genlerdeki "
         "oran).")
    st.header("Bağımsız dağılım ve gamet çeşitliliği")
    n = st.slider("Heterozigot gen çifti sayısı (farklı kromozomlarda)", 1, 5, 2)
    harfler = "ABCDE"[:n]
    genotip = "".join(h + h.lower() for h in harfler)
    import itertools
    gametler = ["".join(c) for c in itertools.product(*[(h, h.lower()) for h in harfler])]
    st.markdown(f"**Genotip:** {genotip}")
    st.latex(rf"\text{{gamet çeşidi}} = 2^{{{n}}} = {2 ** n}")
    st.markdown(" ".join(f"`{g}`" for g in gametler))
    st.markdown("İnsanda n = 23 olduğu için yalnızca bağımsız dağılımla bir kişi "
                "**2²³ = 8.388.608** farklı gamet yapabilir. İki ebeveynden gelen gametlerin "
                "birleşmesiyle 2⁴⁶ ≈ **70 trilyon** farklı kombinasyon mümkündür.")
    st.header("Mitoz ile mayozun karşılaştırılması")
    tablo(pd.DataFrame({
        "Özellik": ["Bölünme sayısı", "Oluşan hücre sayısı", "Kromozom sayısı",
                    "Yavru hücreler genetik olarak", "Homologların eşleşmesi / krossing-over",
                    "Nerede?", "Görevi"],
        "Mitoz": ["1", "2", "Ana hücreyle aynı (2n → 2n)", "Ana hücreyle aynı", "Yok",
                  "Vücut (somatik) hücreleri", "Büyüme, onarım, eşeysiz üreme"],
        "Mayoz": ["2", "4", "Yarıya iner (2n → n)", "Farklı", "Var (Profaz I)",
                  "Eşey ana hücreleri", "Gamet oluşumu, eşeyli üreme, çeşitlilik"]}))
    st.subheader("Mayoz sırasında kromozom ve kromatit sayıları")
    tur = st.selectbox("Tür", list(TURLER), index=0, key="mayoz_tur")
    n2 = TURLER[tur]
    tablo(pd.DataFrame({
        "Evre": ["G1 (başlangıç)", "Profaz I / Metafaz I", "Telofaz I sonrası (her hücre)",
                 "Metafaz II (her hücre)", "Anafaz II (her hücre)", "Gamet (her biri)"],
        "Kromozom": [n2, n2, n2 // 2, n2 // 2, n2, n2 // 2],
        "Kromatit": [n2, 2 * n2, n2, n2, n2, n2 // 2],
        "DNA": ["2c", "4c", "2c", "2c", "2c", "1c"]}))
    alistirma_blogu("mayoz", "Mayoz", gen_mayoz)


# ---------------------------------------------------------------------------
def sayfa_gamet():
    st.title("8 · Gametler, döllenme ve cinsiyet")
    st.markdown("""
Üreme sistemi iki temel işi yapar: **gametleri üretmek** (sperm, yumurta) ve **eşey
hormonlarını salgılamak**. Gametlerin oluşmasına **gametogenez** denir; hayvanlarda testiste
**spermatogenez**, yumurtalıkta **oogenez** olarak gerçekleşir.""")
    svg_goster(svg_gametogenez())
    tablo(pd.DataFrame({
        "Özellik": ["Nerede?", "Ne zaman başlar?", "Duraklama", "Bir birincil hücreden",
                    "Ne kadar sürer?"],
        "Spermatogenez": ["Testislerin seminifer tüplerinde", "Ergenlikten (puberte) hemen önce",
                          "Bir kez başlayınca duraklamaz", "4 olgun sperm",
                          "Ömür boyu (yaşlılıkta azalır)"],
        "Oogenez": ["Yumurtalıklarda", "Doğumdan önce (fetal dönemde)",
                    "İki kez duraklar (Profaz I ve Metafaz II'de)", "1 yumurta (+ polar cisimler)",
                    "Menopozla sona erer"]}))
    st.caption("Tabloda insan örnek alınmıştır; diğer memelilerde de genel düzen benzerdir.")
    with st.expander("📚 Oogenezin ayrıntıları"):
        st.markdown("""
- Oogonyumlar fetal dönemde çoğalır; mayoz I başlar ve **Profaz I'de durur**.
- Ergenlikten sonra her döngüde bir oositte mayoz I tamamlanır: **ikincil oosit** + **1. polar
  cisim** oluşur. İkincil oosit mayoz II'ye başlar ve **Metafaz II'de durur**.
- Ovulasyonla ikincil oosit atılır. **Döllenme olursa** mayoz II tamamlanır (2. polar cisim
  oluşur) ve sperm ile yumurta çekirdekleri birleşerek **diploit zigotu** oluşturur.
- Döllenmeden hemen sonra yumurtanın zarında oluşan değişiklikler başka spermlerin girişini
  engeller.""")
    st.header("Döllenme (fertilizasyon)")
    st.latex(r"\underbrace{n}_{\text{sperm}} + \underbrace{n}_{\text{yumurta}} = "
             r"\underbrace{2n}_{\text{zigot}}")
    st.latex(r"\text{insanda: } 23 + 23 = 46")
    st.header("Cinsiyetin belirlenmesi")
    sistem = st.radio("Sistem", ["XY (memeliler)", "ZW (kuşlar)"], horizontal=True)
    svg_goster(svg_cinsiyet("XY" if sistem.startswith("XY") else "ZW"))
    st.subheader("🎲 Deney: kaç yavruda oranlar %50'ye yaklaşır?")
    c1, c2 = st.columns([1, 1.6])
    with c1:
        N = st.select_slider("Yavru sayısı", [4, 10, 20, 50, 100, 500, 1000, 5000], value=10)
        if st.button("Yeniden doğur 🐣"):
            st.session_state.cins_tohum = int(rng().integers(0, 10 ** 6))
        tohum = st.session_state.get("cins_tohum", 1)
        disi = int(np.random.default_rng(tohum + N).binomial(N, 0.5))
        st.metric("Dişi", f"{disi} (%{100 * disi / N:.0f})")
        st.metric("Erkek", f"{N - disi} (%{100 * (N - disi) / N:.0f})")
    with c2:
        fig = go.Figure(go.Bar(x=["Dişi", "Erkek"], y=[disi, N - disi],
                               marker_color=[PEMBE, MAVI], text=[disi, N - disi],
                               textposition="outside"))
        fig.add_hline(y=N / 2, line_dash="dash", annotation_text="beklenen (%50)")
        fig.update_layout(yaxis_range=[0, N * 0.85], title=f"{N} yavruda dağılım")
        ciz(fig, 300)
    kutu("Her doğumda dişi olma olasılığı 1/2'dir; önceki doğumlar sonucu etkilemez. Az sayıda "
         "yavruda oranlar %50'den sapabilir, yavru sayısı arttıkça %50'ye yaklaşır. "
         "Örnek: 3 çocuğun hepsinin kız olma olasılığı (1/2)³ = 1/8'dir.")
    alistirma_blogu("gamet", "Gametler ve cinsiyet", gen_gamet)


# ---------------------------------------------------------------------------
def _baz_html(dizi):
    return "".join(f'<span class="baz" style="background:{BAZ_RENK.get(b, "#ddd")}">{b}</span>'
                   for b in dizi)


def sayfa_nukleik():
    st.title("9 · Nükleik asitler: DNA ve RNA")
    st.markdown("""
Kalıtımın temel materyali **nükleik asitlerdir**. İki çeşit nükleik asit vardır:
**DNA (deoksiribonükleik asit)** ve **RNA (ribonükleik asit)**. İlk kez 1869'da
**Friedrich Miescher** tarafından hücre çekirdeğinden elde edilmiştir. Nükleik asitler,
**nükleotit** adı verilen yapı birimlerinin uzun zincirler oluşturmasıyla meydana gelir.""")
    st.header("Nükleotit ve nükleozit")
    svg_goster(svg_nukleotid())
    st.header("Azotlu bazlar: pürinler ve pirimidinler")
    svg_goster(svg_purin_pirimidin())
    st.header("DNA'nın yapısı")
    svg_goster(svg_cift_sarmal())
    st.markdown("""
- DNA **iki zincirlidir**; zincirler birbirinin etrafında dönerek **çift sarmal** (bükülmüş
  merdiven) oluşturur.
- Merdivenin **kenarlarını** şeker ve fosfatlar (şeker-fosfat omurga), **basamaklarını** baz
  çiftleri oluşturur. Bir zincirdeki nükleotitler birbirine **fosfodiester bağlarıyla**
  bağlanır.
- Karşılıklı bazlar **hidrojen bağlarıyla** eşleşir: **A = T (2 H bağı)**, **G ≡ C (3 H bağı)**.
- İki zincir **zıt yönlüdür (antiparalel)**: biri 5′→3′, diğeri 3′→5′ yönündedir.
- Genetik bilgi, **bazların diziliş sırasında** saklıdır. Şeker ve fosfat her yerde aynıdır;
  değişken olan bazların sırasıdır.""")
    st.subheader("🔬 Kendi DNA dizinizi yazın")
    dizi = st.text_input("Bir DNA zinciri (5′→3′), yalnız A, T, G, C", "ATGCGTTACGGA")
    dizi = "".join(b for b in dizi.upper() if b in "ATGC")
    if not dizi:
        st.warning("En az bir baz (A, T, G, C) yazın.")
    else:
        tam = "".join(TAMAMLAYICI[b] for b in dizi)
        st.markdown(f'<div class="dizi">5′ {_baz_html(dizi)} 3′<br>3′ {_baz_html(tam)} 5′</div>',
                    unsafe_allow_html=True)
        if len(dizi) <= 16:
            svg_goster(svg_dna_merdiven(dizi))
        else:
            st.caption("Şema ilk 16 bazı gösterir.")
            svg_goster(svg_dna_merdiven(dizi[:16]))
        at = dizi.count("A") + dizi.count("T")
        gc = dizi.count("G") + dizi.count("C")
        c = st.columns(4)
        c[0].metric("Baz çifti", len(dizi))
        c[1].metric("Toplam nükleotit", 2 * len(dizi))
        c[2].metric("Hidrojen bağı", 2 * at + 3 * gc)
        c[3].metric("GC oranı", f"%{100 * gc / len(dizi):.0f}")
        st.latex(r"\text{H bağı} = 2\times(\text{A-T}) + 3\times(\text{G-C})")
        st.latex(rf"= "
                 rf"2\times{at} + 3\times{gc} = {2 * at + 3 * gc}")
        ipucu("GC oranı yüksek DNA'nın iki zinciri daha sıkı bağlıdır (daha çok H bağı); "
              "ayrılması için daha yüksek sıcaklık gerekir.")
    st.subheader("Chargaff kuralı")
    st.markdown("Çift zincirli DNA'da **A = T** ve **G = C**'dir; bu yüzden **pürinler = "
                "pirimidinler** (A + G = T + C).")
    a = st.slider("Bir DNA molekülünde adenin (A) yüzdesi", 0, 50, 30)
    st.latex(rf"A = T = \%{a}")
    st.latex(rf"G = C = \frac{{100 - 2\times{a}}}{{2}} = \%{(100 - 2 * a) / 2:g}")
    fig = go.Figure(go.Bar(x=["A", "T", "G", "C"], y=[a, a, (100 - 2 * a) / 2, (100 - 2 * a) / 2],
                           marker_color=[BAZ_RENK[b] for b in "ATGC"],
                           text=[f"%{v:g}" for v in (a, a, (100 - 2 * a) / 2, (100 - 2 * a) / 2)],
                           textposition="outside"))
    fig.update_layout(yaxis_range=[0, 60], yaxis_title="%")
    ciz(fig, 280)
    st.header("DNA ile RNA'nın karşılaştırılması")
    tablo(pd.DataFrame({
        "Özellik": ["Zincir sayısı", "Şeker", "Bazlar", "Kendini eşleme (replikasyon)",
                    "Çeşit", "Görevi"],
        "DNA": ["Çift zincir", "Deoksiriboz", "A, G, C, T", "Var", "Tek tip",
                "Kalıtsal bilgiyi saklar ve aktarır"],
        "RNA": ["Tek zincir", "Riboz", "A, G, C, U", "Yok (DNA'dan kopyalanır)",
                "Başlıca 3 çeşit: mRNA, tRNA, rRNA", "Protein sentezinde görev alır"]}))
    kartlar([("mRNA (mesajcı / ulak RNA)", "DNA'daki bilgiyi kopyalayıp sitoplazmadaki "
                                          "ribozomlara taşır. Kodonları taşır."),
             ("tRNA (taşıyıcı RNA)", "Amino asitleri ribozoma taşır. Antikodonu ile mRNA'daki "
                                     "kodonu tanır."),
             ("rRNA (ribozomal RNA)", "Proteinlerle birlikte ribozomun yapısını oluşturur; "
                                      "amino asitleri birbirine bağlar.")])
    alistirma_blogu("nukleik", "Nükleik asitler", gen_nukleik)


# ---------------------------------------------------------------------------
def _cevir(mrna, aug_baslat=True):
    bas = mrna.find("AUG") if aug_baslat else 0
    if bas < 0:
        bas = 0
    kodonlar, aa = [], []
    for i in range(bas, len(mrna) - 2, 3):
        k = mrna[i:i + 3]
        kodonlar.append(k)
        aa.append(GENETIK_KOD[k])
        if GENETIK_KOD[k] == "*":
            break
    return bas, kodonlar, aa


def _kodon_html(kodonlar, aa):
    return "".join(f'<span class="kodon">{k}<small>{AA_AD[a][0]}</small></span>'
                   for k, a in zip(kodonlar, aa))


def sayfa_dogma():
    st.title("11 · Replikasyon, genetik kod ve mutasyon")
    st.markdown("""
Önceki bölümde bir genin nasıl okunup proteine çevrildiğini gördük. Bu bölümde DNA'nın
kendini nasıl **eşlediğini**, **genetik kodu** ve DNA'daki küçük bir değişikliğin
(**mutasyon**) proteini nasıl etkilediğini inceleyeceğiz.""")
    st.header("1. Replikasyon: DNA kendini eşler")
    svg_goster(svg_replikasyon())
    st.markdown("""
Hücre bölünmeden önce (S evresinde) DNA'nın iki zinciri hidrojen bağlarından ayrılır
(**helikaz** enzimi). Her eski zincir kalıp olur, **DNA polimeraz** karşısına tamamlayıcı
nükleotitleri ekler. Sonuçta her yeni DNA'da **bir eski, bir yeni zincir** bulunur:
**yarı korunumlu replikasyon** (Meselson ve Stahl, 1958).""")
    st.subheader("🔬 Meselson–Stahl deneyi: kuşaklar boyunca eski zincirler")
    kus = st.slider("Kuşak sayısı", 0, 4, 2)
    svg_goster(svg_meselson(kus))
    if kus == 0:
        st.markdown("Başlangıç: tek bir DNA molekülü, iki zinciri de 'ağır' (eski).")
    else:
        st.markdown(f"**{kus}. kuşak:** toplam **{2 ** kus}** DNA molekülü. Bunların yalnızca "
                    f"**2**'si eski bir zincir taşır (melez), **{2 ** kus - 2}** tanesi tamamen "
                    f"yenidir. Melez oranı = 2 / {2 ** kus} = **%{100 * 2 / 2 ** kus:g}**.")
    st.header("2. Genetik kod")
    st.markdown("""
mRNA üzerindeki her **üçlü baz (kodon)** bir amino asidi belirler (ayrıntılı anlatım:
**10 · Transkripsiyon ve translasyon**).
- Başlangıç kodonu: **AUG** (Metiyonin)
- Durdurma kodonları: **UAA, UAG, UGA**
- 4 × 4 × 4 = **64 kodon**, **20 amino asidi** kodlar: bir amino asidi birden çok kodon
  belirleyebilir (kodun **dejenere** olması). Ama bir kodon her zaman tek bir amino asidi belirler.
- Kod **evrenseldir**: bakteriden insana hemen bütün canlılarda aynıdır.""")
    st.subheader("🔬 Gen çevirici: DNA → mRNA → protein")
    c1, c2 = st.columns([1.2, 1])
    zincir = c1.radio("Yazdığınız DNA zinciri hangisi?",
                      ["Kodlayan zincir (5′→3′, mRNA ile aynı, T yerine U)",
                       "Kalıp zincir (3′→5′ yönünde yazın)"])
    aug = c2.toggle("İlk AUG'den başlat", value=True)
    girdi = st.text_input("DNA dizisi", "ATGGAACTTTGGAAATAA" if zincir.startswith("Kodlayan")
                          else "TACCTTGAAACCTTTATT")
    dna = "".join(b for b in girdi.upper() if b in "ATGC")
    if len(dna) < 3:
        st.warning("En az 3 baz yazın.")
    else:
        if zincir.startswith("Kodlayan"):
            mrna = dna.replace("T", "U")
            st.markdown(f'<div class="dizi">DNA (kodlayan) 5′ {_baz_html(dna)} 3′</div>',
                        unsafe_allow_html=True)
        else:
            mrna = "".join({"A": "U", "T": "A", "G": "C", "C": "G"}[b] for b in dna)
            st.markdown(f'<div class="dizi">DNA (kalıp) 3′ {_baz_html(dna)} 5′</div>',
                        unsafe_allow_html=True)
        st.markdown(f'<div class="dizi">mRNA 5′ {_baz_html(mrna)} 3′</div>', unsafe_allow_html=True)
        bas, kodonlar, aa = _cevir(mrna, aug)
        if aug and "AUG" not in mrna:
            st.info("Dizide AUG yok; baştan okundu.")
        st.markdown(_kodon_html(kodonlar, aa), unsafe_allow_html=True)
        protein = "–".join(AA_AD[a][0] for a in aa if a != "*")
        st.markdown(f"**Protein:** {protein if protein else '(amino asit yok)'}"
                    + (" · *durdurma kodonunda bitti*" if aa and aa[-1] == "*" else
                       " · *durdurma kodonu bulunamadı*"))
    with st.expander("📖 Genetik kod tablosu (mRNA kodonları)"):
        satir = []
        for b1 in "UCAG":
            for b3 in "UCAG":
                satir.append({"1. baz": b1, **{f"2. baz {b2}": f"{b1}{b2}{b3} {AA_AD[GENETIK_KOD[b1 + b2 + b3]][0]}"
                                               for b2 in "UCAG"}, "3. baz": b3})
        tablo(pd.DataFrame(satir))
    st.header("3. Mutasyonlar: bir harf neyi değiştirir?")
    st.markdown("Aşağıdaki gen (kodlayan zincir) üzerinde bir mutasyon yapın ve sonucu görün.")
    orijinal = "ATGGAACTTTGGAAATACTAA"
    c1, c2, c3 = st.columns(3)
    tip = c1.selectbox("Mutasyon tipi", ["Baz değişimi", "Baz eklenmesi", "Baz silinmesi"])
    poz = c2.slider("Konum (kaçıncı baz?)", 1, len(orijinal), 6)
    yeni = c3.selectbox("Yeni baz", list("ATGC"), index=1) if tip != "Baz silinmesi" else None
    if tip == "Baz değişimi":
        mut = orijinal[:poz - 1] + yeni + orijinal[poz:]
    elif tip == "Baz eklenmesi":
        mut = orijinal[:poz] + yeni + orijinal[poz:]
    else:
        mut = orijinal[:poz - 1] + orijinal[poz:]
    _, k1, a1 = _cevir(orijinal.replace("T", "U"), False)
    _, k2, a2 = _cevir(mut.replace("T", "U"), False)
    st.markdown("**Normal gen**")
    st.markdown(_kodon_html(k1, a1), unsafe_allow_html=True)
    st.markdown("**Mutant gen**")
    st.markdown(_kodon_html(k2, a2), unsafe_allow_html=True)
    if tip != "Baz değişimi":
        uyari("<b>Çerçeve kayması mutasyonu:</b> 3'ün katı olmayan ekleme ya da silme, okuma "
              "çerçevesini kaydırır; mutasyondan sonraki bütün kodonlar değişir. Genellikle "
              "proteinin işlevi tamamen bozulur.")
    elif mut == orijinal:
        st.info("Aynı bazı seçtiniz; değişiklik yok.")
    elif a1 == a2:
        st.success("**Sessiz mutasyon:** Kodon değişti ama aynı amino asidi kodluyor; protein "
                   "değişmedi.")
    elif "*" in a2 and a2.index("*") < len(a1) - 1:
        st.error("**Anlamsız (nonsense) mutasyon:** Kodon erken bir durdurma kodonuna dönüştü; "
                 "protein kısa kaldı.")
    else:
        st.warning("**Yanlış anlamlı (missense) mutasyon:** Bir amino asit başka bir amino asitle "
                   "değişti. Etkisi, değişimin proteinin neresinde olduğuna bağlıdır.")
    alistirma_blogu("dogma", "Replikasyon, genetik kod ve mutasyon", gen_dogma)


# ---------------------------------------------------------------------------
def _kart_yeni():
    st.session_state.kart_i = int(rng().integers(0, len(TERIMLER)))
    st.session_state.kart_acik = False


def sayfa_terimler():
    st.title("12 · Temel terimler ve semboller")
    st.header("Genetik problemlerde kullanılan semboller")
    tablo(pd.DataFrame(SEMBOLLER, columns=["Sembol", "Anlamı"]))
    st.header("🃏 Hafıza kartları")
    if "kart_i" not in st.session_state:
        _kart_yeni()
    terim, tanim = TERIMLER[st.session_state.kart_i]
    st.markdown(f'<div class="flash">{terim}' +
                (f'<div class="flash-cevap">{tanim}</div>' if st.session_state.kart_acik else "") +
                '</div>', unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 2])
    if c1.button("👀 Tanımı göster"):
        st.session_state.kart_acik = True
        st.rerun()
    c2.button("➡️ Sonraki kart", on_click=_kart_yeni)
    st.header("📖 Sözlük")
    ara = st.text_input("Terim ara", "")
    for t, d in TERIMLER:
        if ara.lower() in (t + d).lower():
            st.markdown(f"**{t}:** {d}")
    alistirma_blogu("terim", "Terimler", gen_terim)


# ---------------------------------------------------------------------------
def sayfa_tekrar():
    st.title("13 · Genel tekrar")
    st.markdown("Bütün konulardan karışık sorular (10, 20 ya da 30). **🎲 Yeni sorular** ile istediğiniz kadar "
                "tekrar edebilirsiniz.")
    alistirma_blogu("tekrar", "Karışık sorular", gen_tekrar)


# ---------------------------------------------------------------------------
_TR_ADIM = {
    "baslama": "**Başlama:** RNA polimeraz enzimi genin önündeki **promotor** bölgesine bağlanır ve "
               "DNA'nın iki zincirini birbirinden ayırarak küçük bir 'kabarcık' açar.",
    "uzama": "**Uzama:** RNA polimeraz **kalıp zinciri** 3′→5′ yönünde okur ve karşısına tamamlayıcı "
             "RNA nükleotitlerini ekler (A↔U, T↔A, G↔C, C↔G). mRNA 5′→3′ yönünde uzar. Arkada kalan "
             "DNA yeniden kapanır.",
    "bitis": "**Bitiş:** RNA polimeraz **sonlandırıcı** diziye ulaşınca DNA'dan ayrılır; mRNA serbest "
             "kalır. Oluşan mRNA, DNA'nın **kodlayan zinciriyle aynı diziye** sahiptir (yalnızca T yerine U).",
}


def sayfa_trans():
    st.title("10 · Transkripsiyon ve translasyon")
    svg_goster(svg_sentral_dogma())
    st.markdown("""
DNA çekirdekte saklıdır, proteinler ise sitoplazmadaki **ribozomlarda** yapılır. Bu yüzden genin
bilgisi önce bir **kopya**ya, yani **mRNA**'ya aktarılır (**transkripsiyon** = yazılım). Sonra
ribozom bu kopyayı okuyarak proteini yapar (**translasyon** = çeviri).""")
    kartlar([("📝 Transkripsiyon", "DNA → mRNA · çekirdekte · enzim: RNA polimeraz"),
             ("🔤 Translasyon", "mRNA → protein · ribozomda · tRNA'lar amino asit taşır"),
             ("🧩 Kodon", "mRNA'da 3 bazlık 'kelime'; her biri bir amino asidi belirler")])
    st.caption(f"Örnek gen (kodlayan zincir): 5′-{KOD_GEN}-3′ → Met–Ala–Phe–Lys–Gly–DUR")

    st.header("1. Transkripsiyon: DNA'dan mRNA'ya")
    k = st.slider("RNA polimerazı ilerletin (okunan baz sayısı)", 0, len(KOD_GEN), 0, key="tr_k")
    svg_goster(svg_transkripsiyon(k))
    if k == 0:
        st.markdown(_TR_ADIM["baslama"])
    elif k < len(KOD_GEN):
        st.markdown(_TR_ADIM["uzama"])
        st.caption(f"Şu ana kadar {k} nükleotitlik mRNA oluştu.")
    else:
        st.markdown(_TR_ADIM["bitis"])
    tablo(pd.DataFrame({"Kalıp DNA bazı": ["A", "T", "G", "C"],
                        "mRNA'ya eklenen baz": ["U", "A", "C", "G"]}))
    ipucu("Kısa yol: mRNA dizisini bulmak için <b>kodlayan zinciri</b> alıp T'leri U yapmanız "
          "yeterlidir. Kalıp zincir verilmişse her bazın tamamlayıcısını yazın (A→U, T→A, G→C, C→G).")
    with st.expander("📚 Ökaryotlarda mRNA'nın olgunlaşması"):
        st.markdown("""
Bitki ve hayvan hücrelerinde ilk oluşan RNA (ön-mRNA) çekirdekten çıkmadan önce işlenir:
- Genin içindeki kodlamayan parçalar (**intronlar**) kesilip çıkarılır, kodlayan parçalar
  (**ekzonlar**) birleştirilir.
- 5′ ucuna koruyucu bir **başlık**, 3′ ucuna **poli-A kuyruğu** eklenir.
- Olgun mRNA çekirdek porlarından sitoplazmaya geçer.

Bakterilerde çekirdek olmadığı için transkripsiyon ve translasyon aynı anda olabilir.""")

    st.header("2. Translasyon: mRNA'dan proteine")
    st.markdown("""
**Oyuncular:**
- **mRNA:** okunan şerit; her 3 baz bir **kodon**.
- **Ribozom:** büyük ve küçük iki alt birimden oluşur; üzerinde **P** (peptit) ve **A**
  (amino asit) bölgeleri vardır.
- **tRNA:** bir ucunda **antikodon** (kodona tamamlayıcı 3 baz), diğer ucunda taşıdığı **amino
  asit** bulunur.""")
    kod = [KOD_GEN.replace("T", "U")[i:i + 3] for i in range(0, len(KOD_GEN), 3)]
    son = len(kod)
    adim = st.slider("Ribozomu ilerletin (adım)", 0, son, 0, key="tl_adim")
    svg_goster(svg_translasyon(adim))
    dur = [GENETIK_KOD[c] for c in kod].index("*")
    if adim == 0:
        st.markdown("**Başlama:** Küçük alt birim mRNA'ya bağlanır ve **AUG** başlangıç kodonunu bulur. "
                    "Antikodonu **UAC** olan tRNA, **metiyonin (Met)** getirir. Sonra büyük alt birim "
                    "katılır.")
    elif adim < dur:
        st.markdown(f"**Uzama:** A bölgesine kodona uyan yeni bir tRNA gelir. P bölgesindeki amino asit "
                    f"zinciri yeni amino aside **peptit bağıyla** bağlanır. Ribozom bir kodon (3 baz) "
                    f"ilerler. Şu an zincirde **{adim}** amino asit var, sıradaki kodon "
                    f"**{kod[adim]}**.")
    elif adim == dur:
        st.markdown("**Bitiş:** A bölgesine **durdurma kodonu** (UAA, UAG ya da UGA) gelir. Bu kodona "
                    "uyan tRNA yoktur; onun yerine **serbest bırakma faktörü** bağlanır.")
    else:
        st.markdown("**Bitiş:** Protein zinciri serbest kalır, ribozomun alt birimleri birbirinden "
                    "ayrılır. Oluşan protein: **Met–Ala–Phe–Lys–Gly**.")
    tablo(pd.DataFrame({"mRNA kodonu": kod,
                        "tRNA antikodonu": ["—" if GENETIK_KOD[c] == "*" else
                                            "".join(_TAM_RNA_ANTI[b] for b in c) for c in kod],
                        "Amino asit": [AA_AD[GENETIK_KOD[c]][1] for c in kod]}))

    st.header("3. Üç süreci karşılaştıralım")
    tablo(pd.DataFrame({
        "": ["Ne olur?", "Nerede? (ökaryot)", "Kalıp", "Ürün", "Görevli yapı / enzim", "Bazlar"],
        "Replikasyon": ["DNA kopyalanır", "Çekirdek", "DNA'nın iki zinciri", "İki DNA molekülü",
                        "DNA polimeraz, helikaz", "A, T, G, C"],
        "Transkripsiyon": ["DNA'dan mRNA yapılır", "Çekirdek", "DNA'nın kalıp zinciri", "mRNA",
                           "RNA polimeraz", "A, U, G, C (RNA)"],
        "Translasyon": ["mRNA'dan protein yapılır", "Sitoplazma (ribozom)", "mRNA",
                        "Protein (amino asit zinciri)", "Ribozom, tRNA", "—"]}))
    alistirma_blogu("trans", "Transkripsiyon ve translasyon", gen_trans)


# ===========================================================================
# Gezinme
# ===========================================================================
SAYFALAR = [
    st.Page(sayfa_giris, title="Giriş", icon="🏠", url_path="giris", default=True),
    st.Page(sayfa_genetige_giris, title="1 · Genetiğe giriş", url_path="genetige-giris"),
    st.Page(sayfa_tarihce, title="2 · Tarihçe", url_path="tarihce"),
    st.Page(sayfa_hucre, title="3 · Hücre", url_path="hucre"),
    st.Page(sayfa_kromozom, title="4 · Kromozom", url_path="kromozom"),
    st.Page(sayfa_dongu, title="5 · Hücre döngüsü", url_path="hucre-dongusu"),
    st.Page(sayfa_mitoz, title="6 · Mitoz", url_path="mitoz"),
    st.Page(sayfa_mayoz, title="7 · Mayoz", url_path="mayoz"),
    st.Page(sayfa_gamet, title="8 · Gametler ve cinsiyet", url_path="gametler"),
    st.Page(sayfa_nukleik, title="9 · Nükleik asitler", url_path="nukleik-asitler"),
    st.Page(sayfa_trans, title="10 · Transkripsiyon ve translasyon", url_path="transkripsiyon-translasyon"),
    st.Page(sayfa_dogma, title="11 · Replikasyon, genetik kod, mutasyon", url_path="replikasyon-genetik-kod"),
    st.Page(sayfa_terimler, title="12 · Terimler", url_path="terimler"),
    st.Page(sayfa_tekrar, title="13 · Genel tekrar", url_path="genel-tekrar"),
]
gezinme = st.navigation(SAYFALAR)

with st.sidebar:
    tohum = st.number_input("Rastgele tohum (0 = rastgele)", 0, 999999, 0,
                            help="Sınıfta herkes aynı sayıyı girerse aynı soruları görür.")
    if st.session_state.get("tohum") != tohum:
        st.session_state.tohum = tohum
        st.session_state.rng = (np.random.default_rng(tohum) if tohum
                                else np.random.default_rng())
    st.divider()
    st.caption(TELIF)

basliklar = [p.title for p in SAYFALAR]
simdiki = basliklar.index(gezinme.title) if gezinme.title in basliklar else 0
secilen = st.selectbox("📚 Bölüm", basliklar, index=simdiki)
if secilen != gezinme.title:
    st.switch_page(SAYFALAR[basliklar.index(secilen)])

gezinme.run()

st.divider()
c1, _, c3 = st.columns([1, 0.2, 1])
if simdiki > 0:
    c1.page_link(SAYFALAR[simdiki - 1], label=f"◀ {basliklar[simdiki - 1]}")
if simdiki < len(SAYFALAR) - 1:
    c3.page_link(SAYFALAR[simdiki + 1], label=f"{basliklar[simdiki + 1]} ▶")

st.markdown(f'<div style="text-align:center;color:gray;font-size:0.85rem;'
            f'margin-top:24px">{TELIF}</div>', unsafe_allow_html=True)
