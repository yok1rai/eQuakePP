"""Application-wide constants and design tokens.

Centralizing these values means colors, sizes, and thresholds are defined
once instead of scattered as magic literals across the UI code.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    background: str = "#1e1f22"
    surface: str = "#26272b"
    surface_alt: str = "#302f34"
    border: str = "#3d3e43"
    text: str = "#e8e8ea"
    text_dim: str = "#9a9ba3"
    accent: str = "#4f8cff"
    accent_hover: str = "#3d75e6"
    severe: str = "#e63946"
    high: str = "#ff9f1c"
    moderate: str = "#e8c547"
    low: str = "#2ec4b6"


PALETTE = Palette()

APP_NAME = "Deprem Analiz Modülü"
APP_VERSION = "3.0"
APP_ORG = "DepremAnalizModulu"

DEFAULT_CENTER_LAT = 39.0
DEFAULT_CENTER_LNG = 35.0
DEFAULT_ZOOM = 6

DEFAULT_REFRESH_SECONDS = 60
MIN_REFRESH_SECONDS = 15
MAX_REFRESH_SECONDS = 600

DEFAULT_ALARM_THRESHOLD = 4.0

TABLE_ROW_LIMIT = 100
MAP_MARKER_LIMIT = 200

ARCHIVE_CSV_PATH = "deprem_arsiv.csv"
ALERT_SOUND_PATH = "alert.wav"


def severity_color(magnitude: float) -> str:
    """Map a magnitude to its palette color."""
    if magnitude >= 5.0:
        return PALETTE.severe
    if magnitude >= 4.0:
        return PALETTE.high
    if magnitude >= 3.0:
        return PALETTE.moderate
    return PALETTE.low
