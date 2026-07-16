"""Background polling of the earthquake feed.

Runs on a QThread so a slow or failed network call never blocks the UI
thread. Each error path is handled distinctly rather than caught with a
single bare ``except``, so failures are diagnosable from the status bar.
"""
from __future__ import annotations

import logging
from typing import Final

import requests
from PyQt6.QtCore import QThread, pyqtSignal

from core.models import Earthquake

logger = logging.getLogger(__name__)


class EarthquakeWorker(QThread):
    """Fetches the live Kandilli earthquake feed on a background thread."""

    data_fetched = pyqtSignal(list)   # list[Earthquake]
    error_occurred = pyqtSignal(str)

    API_URL: Final[str] = "https://api.orhanaydogdu.com.tr/deprem/kandilli/live"
    TIMEOUT_SECONDS: Final[int] = 10

    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)
        self._session = requests.Session()

    def run(self) -> None:
        try:
            response = self._session.get(self.API_URL, timeout=self.TIMEOUT_SECONDS)
            response.raise_for_status()
            payload = response.json()
        except requests.exceptions.Timeout:
            self.error_occurred.emit("Bağlantı zaman aşımına uğradı.")
            return
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("İnternet bağlantısı yok.")
            return
        except requests.exceptions.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "?"
            self.error_occurred.emit(f"Sunucu hatası: {status}")
            return
        except ValueError:
            self.error_occurred.emit("Sunucudan geçersiz JSON alındı.")
            return
        except requests.exceptions.RequestException as exc:
            logger.exception("Ağ isteği başarısız")
            self.error_occurred.emit(f"Ağ hatası: {exc}")
            return

        if not payload.get("status") or "result" not in payload:
            self.error_occurred.emit("API verisi boş veya format hatalı.")
            return

        quakes: list[Earthquake] = []
        for item in payload["result"]:
            try:
                quakes.append(Earthquake.from_api(item))
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning("Kayıt ayrıştırılamadı, atlanıyor: %s", exc)

        quakes.sort(key=lambda q: q.date_time, reverse=True)
        self.data_fetched.emit(quakes)
        logger.info("Veri güncellendi: %d deprem alındı", len(quakes))
