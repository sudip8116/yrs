from flask import Flask, render_template, Response, jsonify
from scripts.process_variable import VarManager
from scripts.path_manager import PathManager
import os

app = Flask(__name__, static_url_path="/static")
PathManager.init(__file__)
VarManager.init()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/live-radio")
def live_radio():
    return render_template("live-radio.html")

@app.route("/get-song")
def get_song():
    song_path = VarManager.get("song-path", None)
    if song_path and os.path.exists(PathManager.get_path(song_path)):
        with open(PathManager.get_path(song_path), "r") as f:
            return Response(f.read(), mimetype="application/json")
    return jsonify({"error": True})

@app.route("/get-song-position")
def get_song_position():
    return Response(
        VarManager.get("song_start_data", {"t": 0, "mod": 1}), mimetype="application/json"
    )

@app.route("/get-bisi")
def get_bisi():
    return Response(
        VarManager.get("bisi", {"bi": 0, "si": 0}), mimetype="application/json"
    )

if __name__ == "__main__":
    app.run("0.0.0.0")
