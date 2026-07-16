"""Persists earthquake events to a CSV archive.

Unlike the original implementation, this tracks already-logged IDs (loaded
from disk on startup) so restarting the app never re-logs old events, and
so *every* new quake in a batch gets archived -- not just the single most
recent one.
"""
from __future__ import annotations

import csv
import logging
from pathlib import Path

from core.models import Earthquake

logger = logging.getLogger(__name__)

_HEADER = ["id", "date_time", "magnitude", "depth", "title", "latitude", "longitude"]


class DataManager:
    def __init__(self, filepath: str | Path) -> None:
        self.filepath = Path(filepath)
        self._logged_ids: set[str] = set()
        self._initialize_file()

    def _initialize_file(self) -> None:
        if not self.filepath.exists():
            with self.filepath.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(_HEADER)
            return

        try:
            with self.filepath.open("r", newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    row_id = row.get("id")
                    if row_id:
                        self._logged_ids.add(row_id)
        except OSError as exc:
            logger.error("Arşiv dosyası okunamadı: %s", exc)

    def has_logged(self, earthquake: Earthquake) -> bool:
        return earthquake.id in self._logged_ids

    def save(self, earthquake: Earthquake) -> bool:
        """Append a single new earthquake. Returns False if already logged or on error."""
        if self.has_logged(earthquake):
            return False
        try:
            with self.filepath.open("a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(
                    [
                        earthquake.id,
                        earthquake.datetime_str,
                        earthquake.magnitude,
                        earthquake.depth,
                        earthquake.title,
                        earthquake.latitude,
                        earthquake.longitude,
                    ]
                )
            self._logged_ids.add(earthquake.id)
            return True
        except OSError as exc:
            logger.error("CSV yazma hatası: %s", exc)
            return False

    def save_new(self, earthquakes: list[Earthquake]) -> list[Earthquake]:
        """Save every earthquake not yet logged. Returns the ones actually saved."""
        saved = [eq for eq in earthquakes if self.save(eq)]
        if saved:
            logger.info("%d yeni deprem arşive kaydedildi", len(saved))
        return saved
