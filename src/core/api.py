# core/api.py
import requests
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal

class EarthquakeWorker(QThread):
    # Sinyaller: Veri geldiğinde (list) veya hata olduğunda (str) tetiklenir
    data_fetched = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    API_URL = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"

    def run(self):
        """Thread başladığında çalışacak fonksiyon."""
        try:
            # İsteği gönder
            response = requests.get(self.API_URL, timeout=10)

            # HTTP Kontrolü
            if response.status_code == 200:
                data = response.json()

                # API 'status': true ve 'result': [...] yapısında mı?
                if data.get('status') is True and 'result' in data:
                    results = data['result']

                    # Başarılı ise veriyi GUI'ye gönder
                    self.data_fetched.emit(results)

                    # Terminale sadece ufak bir bilgi geç (Console spam'i engellemek için)
                    zaman = datetime.now().strftime("%H:%M:%S")
                    print(f"[SİSTEM {zaman}] Veri güncellendi. ({len(results)} deprem)")

                else:
                    self.error_occurred.emit("API verisi boş veya format hatalı.")
            else:
                self.error_occurred.emit(f"Sunucu Hatası: {response.status_code}")

        except requests.exceptions.Timeout:
            self.error_occurred.emit("Bağlantı Zaman Aşımı (Timeout)")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("İnternet Bağlantısı Yok")
        except Exception as e:
            self.error_occurred.emit(f"Beklenmeyen Hata: {str(e)}")
