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

    def get_song_list(self):
        try:
            path = PathManager.get_path(self.audio_path)
            return [
                f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))
            ]
        except Exception as e:
            print(f"[AudioManager] Failed to load song list: {e}")
            return []

    def get_song(self, file_name):
        path = PathManager.get_path(f"{self.audio_path}/{file_name}")
        if os.path.exists(path):
            return True, path
        return False, None

    def save_song(self, file_name, song_json):
        with open(
            PathManager.get_path(f"{AudioManager.audio_path}/{file_name}"), "w"
        ) as f:
            f.write(json.dumps(song_json, indent=4))

    def delete_song(self, file):
        f_path = PathManager.get_path(f"{AudioManager.audio_path}/{file}")
        try:
            os.remove(f_path)
            return True
        except:
            return False


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
        self.current_time = 0

    def _update_start_data(self):
        self.song_id = randint(1111, 9999)
        self.background.pick_random()
        VarManager.set("song-path", {"path": str(self.current_song.path)})
        VarManager.set(
            "song-start-data", {"t": time() % LiveRadio.mod, "mod": LiveRadio.mod}
        )
        VarManager.set(
            "bi-si", {"bi": self.background.current_index, "si": self.song_id}
        )

    def _load_song(self, next_song=False):
        songs = self.audio.get_song_list()
        if not songs:
            print("[LiveRadio] ⚠️ No songs available.")
            self.current_song = None
            return

        if next_song:
            self.play_index = (self.play_index + 1) % len(songs)
        else:
            # start from first if not playing yet
            self.play_index = 0

        suc, song_path = self.audio.get_song(songs[self.play_index])
        if suc:
            self.current_song = Song(song_path)
            self._update_start_data()
            print(f"[LiveRadio] ▶ Now playing: {songs[self.play_index]}")
        else:
            print(f"[LiveRadio] ⚠️ Failed to load: {songs[self.play_index]}")
            self._load_song(next_song=True)

    def start(self):
        if self.thread and self.thread.is_alive():
            print("[LiveRadio] Already running.")
            return
        self.running = True
        self.thread = Thread(target=self._thread_loop, daemon=False, name="LiveRadioThread")
        self.thread.start()
        print("[LiveRadio] 🟢 Radio started.")

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        print("[LiveRadio] 🔴 Radio stopped.")

    def restart(self):
        self.stop()
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
                    self._load_song(next_song=True)
                    self.current_time = 0

                self.current_time += 1
            sleep(1)
