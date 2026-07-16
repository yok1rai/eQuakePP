# Deprem Analiz Modülü v3.0

Masaüstü deprem takip uygulaması. Kandilli canlı deprem verisini periyodik
olarak çeker, tablo ve harita üzerinde gösterir, eşik değeri aşan
depremlerde sesli/görsel alarm verir, ve tüm kayıtları CSV arşivine yazar.

## Kurulum

```bash
pip install -r requirements.txt
python src/main.py
```

Uyarı sesi için proje kök dizinine bir `alert.wav` dosyası koyun (WAV en
uyumlu formattır; QSoundEffect platforma göre başka formatları
desteklemeyebilir). Dosya yoksa uygulama terminal zili ile geri düşer.

## Proje yapısı

```
src/
  main.py                 - giriş noktası, logging kurulumu
  config.py               - renk paleti ve sabitler (tek kaynak)
  core/
    models.py             - Earthquake veri modeli + tarih/alan normalizasyonu
    api.py                 - arka plan thread'inde API polling
    data_manager.py        - CSV arşivi, yeniden başlatmalarda tekrar kayıt yok
    sound_manager.py       - Qt native ses (harici ffplay bağımlılığı yok)
    settings_manager.py    - QSettings ile kalıcı kullanıcı ayarları
  ui/
    main_window.py         - ana pencere, tüm bileşenleri birbirine bağlar
    map_template.py        - Leaflet haritası, JSON ile güvenli veri aktarımı
    styles.py              - QSS tema (palet'ten üretilir)
```

## v2.2'den değişenler

- **Güvenli JS veri aktarımı**: harita artık tek bir `renderMarkers(json)`
  çağrısıyla güncelleniyor; eskiden her marker için elle string
  birleştirilerek JS kodu üretiliyordu (bir yer adında tırnak/backslash
  olması haritayı bozabiliyordu).
- **Kaçırılan alarmlar düzeltildi**: eskiden sadece "en son" deprem kontrol
  ediliyordu; aynı 60 saniyelik pencerede birden fazla eşik-üstü deprem
  gelirse biri sessizce atlanıyordu. Şimdi yeni kaydedilen *her* deprem
  kontrol ediliyor.
- **Harici `ffplay` bağımlılığı kaldırıldı**: ses artık Qt'nin kendi
  multimedia altyapısıyla (`QSoundEffect`) çalınıyor.
- **Kalıcı ayarlar**: yenileme aralığı, alarm eşiği, sessize alma ve
  minimum büyüklük filtresi artık `QSettings` ile saklanıyor ve yeniden
  başlatmada korunuyor.
- **Yeni özellikler**: yer adına göre arama, minimum büyüklük filtresi
  (tablo + harita), istatistik paneli (toplam / en güçlü / ortalama),
  arşiv klasörünü açma butonu, sessize alma butonu, harita üzerinde
  büyüklük lejantı, pencere boyutu/konumunun hatırlanması.
- **Tip güvenliği ve hata yönetimi**: ham `dict` yerine `Earthquake`
  dataclass'ı; her ağ hatası türü ayrı ayrı ele alınıyor; boş `except:`
  blokları kaldırıldı; `print()` yerine `logging` kullanılıyor.
