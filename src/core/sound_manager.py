"""Alert sound playback.

The original app shelled out to the ``ffplay`` binary via ``os.system``,
which silently did nothing if ffmpeg wasn't installed. This uses Qt's own
multimedia stack instead, so there's no external process dependency, and
failures are logged rather than swallowed.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QSoundEffect

logger = logging.getLogger(__name__)


class SoundManager:
    def __init__(self, sound_file: str | Path) -> None:
        self._effect = QSoundEffect()
        self._muted = False
        self._available = False

        path = Path(sound_file)
        if path.exists():
            self._effect.setSource(QUrl.fromLocalFile(str(path.resolve())))
            self._effect.setVolume(0.9)
            self._available = True
        else:
            logger.warning("Uyarı sesi bulunamadı: %s (terminal zili kullanılacak)", path)

    @property
    def muted(self) -> bool:
        return self._muted

    def set_muted(self, muted: bool) -> None:
        self._muted = muted

    def play_alert(self) -> None:
        if self._muted:
            return
        if self._available:
            self._effect.play()
        else:
            print("\a", end="", flush=True)
