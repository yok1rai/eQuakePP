# core/sound_manager.py
import os
import threading

class SoundManager:
    def __init__(self, sound_file="alert.mp3"):
        self.sound_file = sound_file

    def play_alert(self):
        """Kütüphane gerektirmeyen Linux yöntemi"""
        if os.path.exists(self.sound_file):
            # Arayüzü dondurmamak için thread içinde çalıştır
            threading.Thread(target=self._run_sys_player, daemon=True).start()
        else:
            print("\a") # Dosya yoksa terminal bip sesi

    def _run_sys_player(self):
        # mp3 için 'ffplay' veya 'cvlc' (vlc) genelde yüklüdür.
        # Eğer wav kullanırsan 'aplay' en garantisidir.
        # En yaygın olan ffplay (ffmpeg ile gelir):
        os.system(f"ffplay -nodisp -autoexit {self.sound_file} > /dev/null 2>&1")
