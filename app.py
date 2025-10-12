from flask import Flask, render_template, Response, jsonify
from scripts.process_variable import VarManager
from scripts.path_manager import PathManager
from scripts.live_radio import LiveRadio
import os

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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/live-radio")
def live_radio():
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


if __name__ == "__main__":
    app.run("0.0.0.0")
