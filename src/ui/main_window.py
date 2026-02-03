# ui/main_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QLabel, QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView

from core.api import EarthquakeWorker
from core.data_manager import DataManager
from core.sound_manager import SoundManager
from ui.map_template import get_map_html

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Yapılandırma ---
        self.setWindowTitle("Linux Deprem Analiz Modülü v2.2 (Fixed)")
        self.resize(1280, 800)
        self.refresh_rate = 60 # saniye
        self.alarm_limit = 4.0
        self.last_quake_id = None
        self.is_map_ready = False # Harita yüklendi mi kontrolü
        self.cached_quakes = []   # Harita yüklenene kadar veriyi burada tut

        # --- Modüller ---
        self.data_manager = DataManager("deprem_arsiv.csv")
        self.sound_manager = SoundManager("alert.mp3")
        self.worker = EarthquakeWorker()

        # --- Sinyal Bağlantıları ---
        self.worker.data_fetched.connect(self.on_data_received)
        self.worker.error_occurred.connect(self.on_error)

        # --- Arayüz Kurulumu ---
        self.init_ui()
        self.apply_theme()

        # --- Zamanlayıcı ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_data)
        self.timer.start(self.refresh_rate * 1000)

        # İlk veri çekimi
        self.fetch_data()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. SOL PANEL
        left_panel = QFrame()
        left_panel.setFixedWidth(450)
        left_layout = QVBoxLayout(left_panel)

        self.lbl_status = QLabel("Sistem Beklemede...")
        left_layout.addWidget(self.lbl_status)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["M", "Yer", "Zaman"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.cellClicked.connect(self.on_table_click)
        left_layout.addWidget(self.table)

        btn_refresh = QPushButton("Manuel Yenile")
        btn_refresh.clicked.connect(self.fetch_data)
        left_layout.addWidget(btn_refresh)

        main_layout.addWidget(left_panel)

        # 2. SAĞ PANEL (Harita)
        self.map_view = QWebEngineView()
        self.map_view.setHtml(get_map_html())
        # Harita tam yüklenince bu fonksiyon çalışacak:
        self.map_view.loadFinished.connect(self.on_map_loaded)
        main_layout.addWidget(self.map_view)

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; }
            QLabel { color: #ffffff; padding: 5px; font-weight: bold; }
            QTableWidget { background-color: #333; color: #eee; border: none; }
            QHeaderView::section { background-color: #444; color: #fff; padding: 4px; }
            QPushButton { background-color: #0d6efd; color: white; padding: 10px; border-radius: 4px; }
            QPushButton:hover { background-color: #0b5ed7; }
        """)

    def on_map_loaded(self, success):
        """Harita HTML'i yüklendiğinde tetiklenir."""
        if success:
            self.is_map_ready = True
            print("[SİSTEM] Harita motoru hazır.")
            # Eğer hafızada bekleyen veri varsa şimdi haritaya çiz
            if self.cached_quakes:
                self.update_map(self.cached_quakes)

    def fetch_data(self):
        self.lbl_status.setText("Veri çekiliyor...")
        self.worker.start()

    def on_data_received(self, quakes):
        self.lbl_status.setText(f"Güncel (Toplam: {len(quakes)})")
        if not quakes: return

        self.cached_quakes = quakes # Veriyi hafızaya al

        self.update_table(quakes)
        self.update_map(quakes)
        self.check_alarm(quakes[0])

    def on_error(self, message):
        self.lbl_status.setText(f"Hata: {message}")

    def update_table(self, quakes):
        self.table.setRowCount(0)

        for quake in quakes[:40]:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # --- GÜVENLİ VERİ ÇEKİMİ ---
            mag = float(quake.get('mag', 0))
            title = quake.get('title', 'Bilinmiyor')

            # API ARTIK 'date_time' KULLANIYOR
            full_date = quake.get('date_time', quake.get('date', ''))
            try:
                # "2026-02-03 19:35:44" -> "19:35:44"
                time_str = full_date.split(" ")[1] if " " in full_date else full_date
            except:
                time_str = full_date

            item_mag = QTableWidgetItem(str(mag))
            item_mag.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if mag >= 4.0:
                item_mag.setBackground(QColor("#d32f2f"))
            elif mag >= 3.0:
                item_mag.setBackground(QColor("#f57c00"))

            self.table.setItem(row, 0, item_mag)
            self.table.setItem(row, 1, QTableWidgetItem(title))
            self.table.setItem(row, 2, QTableWidgetItem(time_str))

            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, quake)

    def update_map(self, quakes):
        # Eğer harita henüz yüklenmediyse işlemi iptal et
        if not self.is_map_ready:
            return

        self.map_view.page().runJavaScript("clearMarkers();")

        for q in quakes[:20]:
            try:
                coords = q.get('geojson', {}).get('coordinates', [0,0])
                title = q.get('title', '').replace("'", "")
                mag = q.get('mag', 0)

                # Koordinatlar API'da [Boylam, Enlem] gelir, Leaflet [Enlem, Boylam] ister.
                # q['geojson']['coordinates'] -> [36.416, 40.6392] (Lon, Lat)
                # addMarker(Lat, Lon) olmalı.
                self.map_view.page().runJavaScript(f"addMarker({coords[1]}, {coords[0]}, '{title}', {mag});")
            except Exception as e:
                print(f"Harita marker hatası: {e}")

    def on_table_click(self, row, col):
        if not self.is_map_ready: return

        quake = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        coords = quake.get('geojson', {}).get('coordinates', [0,0])
        self.map_view.page().runJavaScript(f"flyTo({coords[1]}, {coords[0]});")

    def check_alarm(self, latest_quake):
        # Unique ID oluştururken date_time kullan
        date_val = latest_quake.get('date_time', latest_quake.get('date', 'nodate'))
        mag_val = latest_quake.get('mag', 0)

        unique_id = f"{date_val}_{mag_val}"

        if self.last_quake_id != unique_id:
            self.last_quake_id = unique_id

            self.data_manager.save_quake(latest_quake)

            try:
                if float(mag_val) >= self.alarm_limit:
                    self.sound_manager.play_alert()
                    self.show_alert_popup(latest_quake)
            except:
                pass

    def show_alert_popup(self, quake):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("DEPREM ALARMI")
        msg.setText(f"Bölge: {quake.get('title')}\nBüyüklük: {quake.get('mag')}")
        msg.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        msg.exec()
