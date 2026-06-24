import csv
import os

class DataManager:
    def __init__(self, filename="deprem_log.csv"):
        self.filename = filename
        self._initialize_file()

    def _initialize_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Tarih", "Büyüklük", "Derinlik", "Yer", "Enlem", "Boylam"])

    def save_quake(self, quake):
        try:
            coords = quake['geojson']['coordinates']

            tarih = quake.get('date_time', quake.get('date', 'Bilinmiyor'))

            with open(self.filename, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    tarih,
                    quake.get('mag', 0),
                    quake.get('depth', 0),
                    quake.get('title', 'Bilinmiyor'),
                    coords[1],
                    coords[0]
                ])
            print(f"[LOG] Kaydedildi: {quake.get('title')}")
        except Exception as e:
            print(f"[LOG] Kayıt Hatası: {e}")
