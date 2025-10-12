import json
import os
from random import randint
from threading import Thread, Lock
from time import sleep, time
from .process_variable import VarManager
from .path_manager import PathManager


class Song:
    def __init__(self, path):
        self.path = path
        self.duration = 0
        try:
            with open(self.path, "r") as f:
                self.duration = self._parse_duration(f.read())
        except Exception as e:
            print(f"[Song] Error loading {path}: {e}")

    def _parse_duration(self, song_json: str) -> int:
        try:
            data = json.loads(song_json)
            duration_str = data.get("duration", "0")
            return self._to_seconds(duration_str)
        except Exception as e:
            print(f"[Song] Error parsing duration: {e}")
            return 0

    def _to_seconds(self, duration: str) -> int:
        try:
            parts = list(map(int, duration.strip().split(":")))
            total = 0
            for p in parts:
                total = total * 60 + p
            return total
        except Exception as e:
            print(f"[Song] Duration format error: {duration} ({e})")
            return 0


class AudioManager:
    audio_path = "audios"

    def __init__(self):
        PathManager.create_path(self.audio_path)
        self.song_list = []
        self.load_song_list()

    def get_song(self, index: int):
        if not (0 <= index < len(self.song_list)):
            return False, None
        path = PathManager.get_path(f"{self.audio_path}/{self.song_list[index]}")
        return True, path

    def get_random_index(self) -> int:
        return randint(0, len(self.song_list) - 1) if self.song_list else -1

    def is_empty(self) -> bool:
        return not self.song_list

    def load_song_list(self):
        try:
            path = PathManager.get_path(self.audio_path)
            self.song_list = [
                f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
            ]
            print(f"[AudioManager] Loaded {len(self.song_list)} songs.")
        except Exception as e:
            print(f"[AudioManager] Failed to load song list: {e}")
            self.song_list = []


class BackgroundManager:
    background_path = "static/images/background"

    def __init__(self):
        PathManager.create_path(self.background_path)
        self.max_count = 0
        self.current_index = 0
        self._rename_backgrounds()
        self.pick_random()

    def _rename_backgrounds(self):
        bg_path = PathManager.get_path(self.background_path)
        try:
            files = [
                f
                for f in os.listdir(bg_path)
                if os.path.isfile(os.path.join(bg_path, f))
            ]
            if not files:
                self.max_count = 0
                return

            for i, f in enumerate(files):
                src = os.path.join(bg_path, f)
                temp = os.path.join(bg_path, f"__temp_{i + 1}.jpg")
                if src != temp:
                    if os.path.exists(temp):
                        os.remove(temp)
                    os.rename(src, temp)

            temp_files = sorted(
                f for f in os.listdir(bg_path) if f.startswith("__temp_")
            )
            for i, f in enumerate(temp_files):
                src = os.path.join(bg_path, f)
                dst = os.path.join(bg_path, f"image-{i + 1}.jpg")
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)

            self.max_count = len(temp_files)
            print(f"[BackgroundManager] {self.max_count} backgrounds ready.")
        except Exception as e:
            print(f"[BackgroundManager] Rename error: {e}")

    def pick_random(self):
        if self.max_count == 0:
            self.current_index = 0
        else:
            self.current_index = randint(1, self.max_count)


class LiveRadio:
    mod = 100000

    def __init__(self):
        self.audio = AudioManager()
        self.background = BackgroundManager()
        self.play_index = 0
        self.song_id = 0
        self.current_song: "Song" = None
        self.lock = Lock()

        self.running = False
        self.thread: Thread | None = None

    def _update_start_data(self):
        if not self.song_id:
            self.song_id = randint(1111, 9999)

        self.background.pick_random()
        VarManager.set("song-path", str(self.current_song.path))
        VarManager.set(
            "song_start_data", {"t": time() % LiveRadio.mod, "mod": LiveRadio.mod}
        )
        VarManager.set(
            "bisi", {"bi": self.background.current_index, "si": self.song_id}
        )

    def _load_song(self):
        if self.audio.is_empty():
            print("[LiveRadio] ⚠️ No songs available.")
            return

        suc, song_path = self.audio.get_song(self.play_index)
        if suc:
            self.current_song = Song(song_path)
            self._update_start_data()
            print(f"[LiveRadio] ▶ Now playing index {self.play_index}")
        else:
            self.play_index = self.audio.get_random_index()
            self._load_song()

    def start(self):
        if self.thread and self.thread.is_alive():
            print("[LiveRadio] Already running.")
            return
        self.running = True
        self.thread = Thread(
            target=self._thread_loop, daemon=False, name="LiveRadioThread"
        )
        self.thread.start()
        print("[LiveRadio] 🟢 Radio started.")

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        print("[LiveRadio] 🔴 Radio stopped.")

    def restart(self):
        self.stop()
        self.play_index = 0
        self.start()

    def _thread_loop(self):
        self.current_time = 0
        self._load_song()
        while self.running:
            with self.lock:
                if not self.current_song:
                    sleep(1)
                    continue

                if self.current_time >= self.current_song.duration:
                    self.song_id = 0
                    self.play_index = self.audio.get_random_index()
                    self._load_song()
                    self.current_time = 0

                self.current_time += 1
            sleep(1)
