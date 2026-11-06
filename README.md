# 🧬 Genetik Laboratuvarı

**Ön lisans Genetik dersi için etkileşimli, Türkçe öğretim uygulaması**

© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır.

---

## Nedir?

Genetiğin temel konularını şemalarla, etkileşimli çizimlerle ve bol alıştırmayla anlatan bir web
uygulamasıdır. Bilgisayardan ve telefondan tarayıcıyla açılır. Bütün şemalar bu uygulama için
özgün olarak çizilmiştir.

## İçerik

| Bölüm | Konu ve etkileşimli öğeler |
|---|---|
| 1 · Genetiğe giriş | Genetik, kalıtım; genom, gen, genotip, fenotip; ekstrakromozomal (sitoplazmik) kalıtım; varyasyon kaynakları; kalitatif/kantitatif karakter (gen sayısı ve çevre deneyi); Fenotip = Genotip + Çevre; G×Ç etkileşimi |
| 2 · Tarihçe | 1665–2007 etkileşimli zaman çizelgesi, alan ve dönem filtresi |
| 3 · Hücre | Hayvan ve bitki hücresi şeması; organel seçince vurgulama; bitki–mantar–hayvan farkları |
| 4 · Kromozom | Kromozom yapısı; gen–lokus–allel kavram haritası; homolog kromozomlar; homozigot/heterozigot; dominant/resesif; sentromer tipleri, 2n/n, türlere göre kromozom sayıları, insan karyotipi (XX/XY) |
| 5 · Hücre döngüsü | G1–S–G2–M ve G0, DNA miktarı grafiği, kontrol noktaları, siklin–CDK (ileri bilgi) |
| 6 · Mitoz | Kaydırıcıyla evre evre mitoz şemaları, türe göre kromozom/kromatit sayıları, sitokinez |
| 7 · Mayoz | Evre evre mayoz, bağımsız dağılımı yeniden dizme, krossing-over simülatörü, gamet çeşitliliği, mitoz–mayoz karşılaştırması |
| 8 · Gametler | Spermatogenez ve oogenez şeması, döllenme, XY/ZW cinsiyet belirlenmesi, yavru simülasyonu |
| 9 · Nükleik asitler | Nükleotit, pürin/pirimidin, çift sarmal; kendi DNA dizinizle tamamlayıcı iplik, H bağı, GC oranı; Chargaff |
| 10 · Transkripsiyon ve translasyon | Kaydırıcıyla adım adım RNA polimeraz ve ribozom animasyonu (promotor, kalıp zincir, kodon–antikodon, P/A bölgeleri, peptit bağı, durdurma kodonu); mRNA olgunlaşması; replikasyon–transkripsiyon–translasyon karşılaştırması |
| 11 · Replikasyon, genetik kod, mutasyon | Replikasyon, Meselson–Stahl simülasyonu; genetik kod tablosu; gen çevirici; mutasyon laboratuvarı |
| 12 · Genetik kod ve kodon atölyesi | Neden üçlü (4¹–4⁴ karşılaştırması), kodun özellikleri, okuma çerçevesi ve çerçeve kayması, tıklanabilir kod tablosu ve dejenerelik grafiği; DNA → tamamlayıcı DNA → mRNA yazma alıştırması (baz baz kontrol, sık yapılan hatalara ipucu) ve mRNA → protein çevirme |
| 13 · Terimler | Semboller, hafıza kartları, aranabilir sözlük |
| 14 · Genel tekrar | Tüm konulardan karışık sorular |

Her bölümün sonunda **10, 20 ya da 30 soruluk seçmeli alıştırma** vardır (öğrenci seçer). Yanıt seçilince kilitlenir, doğru/yanlış ve
adım adım çözüm o zaman açılır. "Yeni sorular" düğmesiyle sınırsız soru üretilir.

## Kurulum ve çalıştırma

```bash
pip install -r requirements.txt
streamlit run genetik_streamlit.py
```

Linux / WSL'de kısaca: `bash baslat.sh`. Ardından tarayıcıda http://localhost:8501

## Yayına alma

GitHub reposuna `genetik_streamlit.py` ve `requirements.txt` yüklenir; share.streamlit.io'da
"Create app" ile ana dosya olarak `genetik_streamlit.py` seçilir.

## Bilinen sınırlamalar

- Şemalar öğretim amaçlı ve ölçeksizdir; karyotipte kromozom boyları yaklaşıktır.
- Süt verimi, G×Ç ve poligenik kalıtım örneklerindeki sayılar kurgusaldır.
- Öğrenci yanıtları kaydedilmez; uygulama öğrenmek için tasarlanmıştır.

## Telif ve kullanım

© 2026 Emine Dilşat Yeğenoğlu & Tevfik Hasan Can. Tüm hakları saklıdır. Ayrıntılar için
`LICENSE` dosyasına bakın.

İletişim ve izin talepleri: dilsat.yegenoglu@cbu.edu.tr
