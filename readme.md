# eQuake++ | Modern Deprem Takip Sistemi

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyQt6](https://img.shields.io/badge/Framework-PyQt6-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-orange)

**eQuake++**, Türkiye'deki son depremleri Kandilli Rasathanesi verilerini kullanarak anlık takip eden, modern arayüzlü, modüler ve açık kaynaklı bir masaüstü uygulamasıdır.

## 🌟 Özellikler

* **Canlı Veri Akışı:** Orhan Aydoğdu API üzerinden Kandilli Rasathanesi verilerini anlık çeker.
* **İnteraktif Harita:** LeafletJS ve OpenStreetMap tabanlı, PyQt6 WebEngine içine gömülü modern harita.
* **Modüler Mimari:** SOLID prensiplerine uygun; API, GUI, Veri Yönetimi ve Ses modülleri ayrıştırılmıştır.
* **Akıllı Alarm Sistemi:** Belirlenen büyüklükteki (örn: 4.0+) depremlerde sesli ve görsel uyarı verir.
* **Otomatik Loglama:** Kritik depremleri `deprem_arsiv.csv` dosyasına Excel uyumlu formatta kaydeder.
* **Linux Native:** Linux ses sunucuları (PulseAudio/ALSA) ile tam uyumlu çalışır.

## 📂 Proje Yapısı

```text
eQuake++/
├── main.py                 # Başlatıcı (Entry Point)
├── alert.mp3               # Alarm sesi dosyası
├── core/
│   ├── api.py              # API veri çekme işlemleri (Threaded)
│   ├── data_manager.py     # CSV okuma/yazma işlemleri
│   └── sound_manager.py    # Platform bağımsız ses yönetimi
└── ui/
    ├── main_window.py      # Ana GUI ve Logic
    └── map_template.py     # HTML/JS Harita Şablonu
```

## 🚀 Kurulum (Linux)

Projenin çalışması için Python 3 ve gerekli sistem kütüphanelerine ihtiyacınız vardır.

1. Sistem Bağımlılıkları

PyQt6 WebEngine için gerekli kütüphaneleri yükleyin (Debian/Ubuntu/Kali):

```bash
sudo apt update
sudo apt install python3-pip libxcb-cursor0 libnss3
```

2. Python Kütüphaneleri

Gerekli paketleri pip ile kurun:

```bash
pip install PyQt6 PyQt6-WebEngine requests
```

Not: Ses çalma özelliği için sisteminizde ffplay, mpv veya aplay araçlarından birinin yüklü olması önerilir (Genellikle yüklüdür).

3. Çalıştırma

Proje dizinine gidin ve başlatın:
Bash

python3 main.py

## ⚙️ Yapılandırma

Program ayarlarını ui/main_window.py içinden değiştirebilirsiniz:

```python
self.refresh_rate = 60  # Veri yenileme hızı (saniye)
self.alarm_limit = 4.0  # Alarm için eşik büyüklük
```

## 📊 Veri Kaynağı

Bu proje, verileri Orhan Aydoğdu tarafından sağlanan açık kaynaklı Kandilli Rasathanesi API'sinden almaktadır.
🤝 Katkıda Bulunma

1. Forklayın.
2. Yeni bir dal (branch) oluşturun (git checkout -b feature/YeniOzellik).
3. Değişikliklerinizi commit yapın.
4. Dalı (branch) pushlayın.
5. Bir Pull Request oluşturun.

## 📄 Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Detaylar için [LICENSE](license) dosyasına bakın.


---

### 2. `LICENSE`
Bu dosya, kodunu başkalarının kullanmasına izin verdiğini ama sorumluluk kabul etmediğini belirten standart **MIT Lisansı**dır. (Yılı ve İsim kısmını güncelledim).

```text
MIT License

Copyright (c) 2026 yok1rai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
