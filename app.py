from flask import Flask
from flask import request, render_template, Response, jsonify
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
live_radio = LiveRadio()
live_radio.start()


# admin routes
@app.route("/upload-song", methods=["POST"])
def upload_song():
    if request.headers.get("auth", "null") != AUTH_KEY:
        return "Authorizaion Failed"
    json_data = request.get_json()
    save_name = request.headers.get("file-name", None)
    live_radio.audio.save_song(save_name, json_data)
    return "Success"


@app.route("/update-songs-list")
def update_songs_list():
    if request.headers.get("auth", "null") != AUTH_KEY:
        return "Authorizaion Failed"
    live_radio.audio.load_song_list()
    return "Success"


@app.route("/get-songs-list")
def get_song_list():
    if request.headers.get("auth", "null") != AUTH_KEY:
        return jsonify([])
    return jsonify(live_radio.audio.song_list)


@app.route("/delete-song")
def delete_songs():
    if request.headers.get("auth", "null") != AUTH_KEY:
        return "Authenticaoin Failed"
    file = request.headers.get("file-name")
    res = live_radio.audio.delete_song(file)
    return f"{res}"


@app.route("/restart-player")
def restart_player():
    if request.headers.get("auth", "null") != AUTH_KEY:
        return "failed to restart"
    live_radio.restart()
    return f"player restarted"


# public routes


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/live-radio")
def live_radio_page():
    return render_template("live-radio.html")


@app.route("/get-song")
def get_song():
    song_path = VarManager.get(
        "song-path",
        {
            "path": str(
                PathManager.get_path(
                    f"audios/{os.listdir(PathManager.get_path('audios'))[0]}"
                )
            )
        },
    )
    print(song_path)
    if song_path and os.path.exists(song_path["path"]):
        with open(song_path["path"], "r") as f:
            return Response(f.read(), mimetype="application/json")
    return jsonify({"error": True})


@app.route("/get-song-position")
def get_song_position():
    return jsonify(VarManager.get("song-start-data", {"t": 0, "mod": 1}))


@app.route("/get-bisi")
def get_bisi():
    return jsonify(VarManager.get("bi-si", {"bi": 0, "si": 0}))


# if __name__ == "__main__":
#     app.run("0.0.0.0")
