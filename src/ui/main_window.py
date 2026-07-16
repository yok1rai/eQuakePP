"""Main application window.

Wires together the background API worker, CSV archive, sound alerts, and
the two views (table + map) that display the live earthquake feed.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QColor, QDesktopServices
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from config import (
    APP_NAME,
    APP_VERSION,
    ARCHIVE_CSV_PATH,
    ALERT_SOUND_PATH,
    MAP_MARKER_LIMIT,
    MAX_REFRESH_SECONDS,
    MIN_REFRESH_SECONDS,
    TABLE_ROW_LIMIT,
)
from core.api import EarthquakeWorker
from core.data_manager import DataManager
from core.models import Earthquake
from core.settings_manager import SettingsManager
from core.sound_manager import SoundManager
from ui.map_template import get_map_html
from ui.styles import get_stylesheet

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.settings = SettingsManager()
        self.data_manager = DataManager(ARCHIVE_CSV_PATH)
        self.sound_manager = SoundManager(ALERT_SOUND_PATH)
        self.sound_manager.set_muted(self.settings.muted)

        self.worker = EarthquakeWorker(self)
        self.worker.data_fetched.connect(self._on_data_received)
        self.worker.error_occurred.connect(self._on_error)

        self._all_quakes: list[Earthquake] = []
        self._is_map_ready = False
        self._known_alarm_ids: set[str] = set()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(1320, 820)
        self.setStyleSheet(get_stylesheet())

        self._build_ui()
        self._restore_geometry()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.fetch_data)
        self.refresh_timer.start(self.settings.refresh_seconds * 1000)

        self.fetch_data()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_left_panel())

        self.map_view = QWebEngineView()
        self.map_view.setHtml(get_map_html())
        self.map_view.loadFinished.connect(self._on_map_loaded)
        root_layout.addWidget(self.map_view, stretch=1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Başlatılıyor…")

    def _build_left_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("leftPanel")
        panel.setFixedWidth(460)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel(APP_NAME)
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        self.status_label = QLabel("Sistem başlatılıyor…")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        layout.addWidget(self._build_stats_row())
        layout.addWidget(self._build_filter_row())

        self.table = self._build_table()
        layout.addWidget(self.table, stretch=1)

        layout.addWidget(self._build_action_row())

        return panel

    def _build_stats_row(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("statsPanel")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)

        self.stat_total = self._make_stat_block(layout, "0", "TOPLAM")
        self.stat_strongest = self._make_stat_block(layout, "—", "EN GÜÇLÜ")
        self.stat_average = self._make_stat_block(layout, "—", "ORTALAMA")

        return frame

    def _make_stat_block(self, layout: QHBoxLayout, value: str, caption: str) -> QLabel:
        block = QVBoxLayout()
        value_label = QLabel(value)
        value_label.setProperty("class", "statValue")
        value_label.setStyleSheet("font-size: 20px; font-weight: 700; color: #4f8cff;")
        caption_label = QLabel(caption)
        caption_label.setStyleSheet("color: #9a9ba3; font-size: 11px;")
        block.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        block.addWidget(caption_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(block)
        return value_label

    def _build_filter_row(self) -> QFrame:
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Yer ara…")
        self.search_box.textChanged.connect(self._apply_filters)
        layout.addWidget(self.search_box, stretch=2)

        self.min_mag_spin = QDoubleSpinBox()
        self.min_mag_spin.setRange(0.0, 9.0)
        self.min_mag_spin.setSingleStep(0.1)
        self.min_mag_spin.setPrefix("M≥ ")
        self.min_mag_spin.setValue(self.settings.min_magnitude_filter)
        self.min_mag_spin.valueChanged.connect(self._on_min_magnitude_changed)
        layout.addWidget(self.min_mag_spin, stretch=1)

        return frame

    def _build_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["M", "Yer", "Derinlik", "Saat"])
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.cellClicked.connect(self._on_table_row_clicked)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        return table

    def _build_action_row(self) -> QFrame:
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 12)

        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.fetch_data)
        layout.addWidget(refresh_btn)

        archive_btn = QPushButton("Arşivi Aç")
        archive_btn.clicked.connect(self._open_archive_folder)
        layout.addWidget(archive_btn)

        self.mute_btn = QPushButton()
        self.mute_btn.setObjectName("mutedButton")
        self.mute_btn.setCheckable(True)
        self.mute_btn.setChecked(self.settings.muted)
        self._update_mute_button_text()
        self.mute_btn.clicked.connect(self._on_mute_toggled)
        layout.addWidget(self.mute_btn)

        return frame

    def _restore_geometry(self) -> None:
        geometry = self.settings.window_geometry
        if geometry is not None:
            self.restoreGeometry(geometry)

    # ------------------------------------------------------------- fetching

    def fetch_data(self) -> None:
        if self.worker.isRunning():
            return
        self.status_label.setText("Veri çekiliyor…")
        self.status_bar.showMessage("Sunucuya bağlanılıyor…")
        self.worker.start()

    def _on_data_received(self, quakes: list[Earthquake]) -> None:
        if not quakes:
            self.status_label.setText("Veri alınamadı (boş yanıt).")
            return

        self._all_quakes = quakes
        newly_saved = self.data_manager.save_new(quakes)
        self._check_alarms(newly_saved)

        self.status_label.setText(f"Güncel — toplam {len(quakes)} kayıt")
        self.status_bar.showMessage(f"Son güncelleme: {quakes[0].time_str}", 5000)

        self._update_stats(quakes)
        self._apply_filters()

    def _on_error(self, message: str) -> None:
        self.status_label.setText(f"Hata: {message}")
        self.status_bar.showMessage(message, 8000)
        logger.warning("Veri çekme hatası: %s", message)

    # --------------------------------------------------------------- alarms

    def _check_alarms(self, newly_saved: list[Earthquake]) -> None:
        """Alarm on every newly-seen quake above the threshold.

        The original only ever inspected the single most-recent record, so
        if two qualifying quakes arrived in the same 60-second window, the
        older one silently never triggered an alert. Iterating over every
        newly-saved record fixes that.
        """
        threshold = self.settings.alarm_threshold
        for quake in newly_saved:
            if quake.id in self._known_alarm_ids:
                continue
            self._known_alarm_ids.add(quake.id)
            if quake.magnitude >= threshold:
                self.sound_manager.play_alert()
                self._show_alert_popup(quake)

    def _show_alert_popup(self, quake: Earthquake) -> None:
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("DEPREM ALARMI")
        box.setText(
            f"Bölge: {quake.title}\n"
            f"Büyüklük: {quake.magnitude:.1f}\n"
            f"Derinlik: {quake.depth:.1f} km\n"
            f"Zaman: {quake.datetime_str}"
        )
        box.setWindowFlags(box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        box.exec()

    # ---------------------------------------------------------------- stats

    def _update_stats(self, quakes: list[Earthquake]) -> None:
        self.stat_total.setText(str(len(quakes)))
        if not quakes:
            self.stat_strongest.setText("—")
            self.stat_average.setText("—")
            return

        strongest = max(quakes, key=lambda q: q.magnitude)
        average = sum(q.magnitude for q in quakes) / len(quakes)
        self.stat_strongest.setText(f"{strongest.magnitude:.1f}")
        self.stat_average.setText(f"{average:.2f}")

    # -------------------------------------------------------------- filters

    def _on_min_magnitude_changed(self, value: float) -> None:
        self.settings.min_magnitude_filter = value
        if self._is_map_ready:
            self.map_view.page().runJavaScript(f"setMinMagnitude({value});")
        self._apply_filters()

    def _apply_filters(self) -> None:
        min_mag = self.min_mag_spin.value()
        search_text = self.search_box.text()

        filtered = [
            q for q in self._all_quakes
            if q.magnitude >= min_mag and q.matches(search_text)
        ]
        self._render_table(filtered)
        self._render_map(filtered)

    # ---------------------------------------------------------------- table

    def _render_table(self, quakes: list[Earthquake]) -> None:
        self.table.setRowCount(0)
        for quake in quakes[:TABLE_ROW_LIMIT]:
            row = self.table.rowCount()
            self.table.insertRow(row)

            mag_item = QTableWidgetItem(f"{quake.magnitude:.1f}")
            mag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            mag_item.setBackground(QColor(quake.color))
            mag_item.setData(Qt.ItemDataRole.UserRole, quake)

            self.table.setItem(row, 0, mag_item)
            self.table.setItem(row, 1, QTableWidgetItem(quake.title))
            self.table.setItem(row, 2, QTableWidgetItem(f"{quake.depth:.1f} km"))
            self.table.setItem(row, 3, QTableWidgetItem(quake.time_str))

    def _on_table_row_clicked(self, row: int, _column: int) -> None:
        item = self.table.item(row, 0)
        if item is None:
            return
        quake: Earthquake = item.data(Qt.ItemDataRole.UserRole)
        if quake and self._is_map_ready:
            self.map_view.page().runJavaScript(f"flyTo({quake.latitude}, {quake.longitude});")

    # ----------------------------------------------------------------- map

    def _on_map_loaded(self, success: bool) -> None:
        if not success:
            logger.error("Harita motoru yüklenemedi.")
            return
        self._is_map_ready = True
        self.map_view.page().runJavaScript(f"setMinMagnitude({self.min_mag_spin.value()});")
        if self._all_quakes:
            self._apply_filters()

    def _render_map(self, quakes: list[Earthquake]) -> None:
        if not self._is_map_ready:
            return

        payload = [
            {
                "lat": q.latitude,
                "lng": q.longitude,
                "mag": q.magnitude,
                "depth": q.depth,
                "title": q.title,
                "time": q.time_str,
            }
            for q in quakes[:MAP_MARKER_LIMIT]
        ]

        self.map_view.page().runJavaScript(f"renderMarkers({json.dumps(payload)});")

    # -------------------------------------------------------------- actions

    def _on_mute_toggled(self, checked: bool) -> None:
        self.sound_manager.set_muted(checked)
        self.settings.muted = checked
        self._update_mute_button_text()

    def _update_mute_button_text(self) -> None:
        self.mute_btn.setText("🔇 Sessiz" if self.mute_btn.isChecked() else "🔊 Sesli")

    def _open_archive_folder(self) -> None:
        folder = Path(self.data_manager.filepath).resolve().parent
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    # -------------------------------------------------------------- cleanup

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override signature
        self.settings.window_geometry = self.saveGeometry()
        self.refresh_timer.stop()
        if self.worker.isRunning():
            self.worker.wait(3000)
        super().closeEvent(event)
