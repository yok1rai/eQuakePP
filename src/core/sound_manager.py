import os
import threading

class SoundManager:
    def __init__(self, sound_file="alert.mp3"):
        self.sound_file = sound_file

    def play_alert(self):
        if os.path.exists(self.sound_file):
            threading.Thread(target=self._run_sys_player, daemon=True).start()
        else:
            print("\a")

    def _run_sys_player(self):
        os.system(f"ffplay -nodisp -autoexit {self.sound_file} > /dev/null 2>&1")
