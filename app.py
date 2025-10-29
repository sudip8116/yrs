from flask import Flask, request, render_template, Response, jsonify
from scripts.process_variable import VarManager
from scripts.path_manager import PathManager
from scripts.live_radio import LiveRadio
import os

AUTH_KEY = "3f9a7b2c1d8e4f6a0b9c2d7e8f1a3b"
app = Flask(__name__, static_url_path="/static")

PathManager.init(__file__)
VarManager.init()
VarManager.set("bi-si", {"bi": 1, "si": 0})
VarManager.set("song-start-data", {"t": 0, "mod": 1})
VarManager.set(
    "song-path",
    {
        "path": str(
            PathManager.get_path(
                f"audios/{os.listdir(PathManager.get_path('audios'))[0]}"
            )
        )
    },
)

live_radio = LiveRadio()  # no threading now
live_radio.start()
# -----------------------------
# Admin routes
# -----------------------------


@app.route("/upload-song", methods=["POST"])
def upload_song():
    if request.headers.get("auth", "null") != AUTH_KEY:
        return "Authorization Failed"
    json_data = request.get_json()
    save_name = request.headers.get("file-name", None)
    live_radio.audio.save_song(save_name, json_data)
    return "Success"


@app.route("/delete-song")
def delete_song():
    if request.headers.get("auth", "null") != AUTH_KEY:
        return "Authorization Failed"
    file = request.headers.get("file-name")
    res = live_radio.audio.delete_song(file)
    return str(res)


@app.route("/restart-player")
def restart_player():
    if request.headers.get("auth", "null") != AUTH_KEY:
        return "Failed to restart"
    live_radio.restart()
    return "Player restarted"


@app.route("/get-song-list")
def get_song_lists():
    if request.headers.get("auth", "null") != AUTH_KEY:
        return jsonify([])
    live_radio.restart()
    return jsonify(live_radio.audio.get_song_list())


# -----------------------------
# Public routes
# -----------------------------


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/live-radio")
def live_radio_page():
    return render_template("live-radio.html")


@app.route("/get-song")
def get_song():
    song_dir = PathManager.get_path("audios")
    song_files = os.listdir(song_dir)
    if not song_files:
        return jsonify({"error": True, "message": "No songs found"})

    current_song = VarManager.get("song-path", None)
    if not current_song or not os.path.exists(current_song["path"]):
        # pick next available song automatically
        next_song_path = PathManager.get_path(f"audios/{song_files[0]}")
        VarManager.set("song-path", {"path": str(next_song_path)})
        current_song = {"path": str(next_song_path)}

    with open(current_song["path"], "r") as f:
        return Response(f.read(), mimetype="application/json")


@app.route("/get-song-position")
def get_song_position():
    return jsonify(VarManager.get("song-start-data", {"t": 0, "mod": 1}))


@app.route("/get-bisi")
def get_bisi():
    return jsonify(VarManager.get("bi-si", {"bi": 0, "si": 0}))


if __name__ == "__main__":
    app.run("0.0.0.0")
