import requests
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal

class EarthquakeWorker(QThread):
    data_fetched = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    API_URL = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"

    def run(self):
        try:
            response = requests.get(self.API_URL, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if data.get('status') is True and 'result' in data:
                    results = data['result']

                    self.data_fetched.emit(results)

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
