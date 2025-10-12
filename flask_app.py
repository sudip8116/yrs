from flask import Flask
from flask import render_template, request, Response, jsonify
from scripts.path_manager import PathManager
from scripts.process_variable import VarManager
from scripts.live_radio import LiveRadio

app = Flask(__name__, static_url_path="/static")
PathManager.init(__file__)
VarManager.init()
VarManager.set("song_start_data", {"t": 0, "mod": 1})
VarManager.set("bisi", {"bi": 0, "si": 0})
liveRadio = LiveRadio()
liveRadio.start()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/live-radio")
def live_radio():
    return render_template("live-radio.html")


@app.route("/custom-music")
def custom_music():
    return render_template("custom-music.html")


#### publc routed #####
@app.route("/get-song")
def get_song():
    if liveRadio.current_song:
        return Response(liveRadio.current_song.json_data, mimetype="application/json")
    return jsonify({"error": True})


@app.route("/get-song-position")
def get_song_position():
    try:
        return Response(
            VarManager.get("song_start_data", {"t": 0, "mod": 1}),
            mimetype="application/json",
        )
    except:
        return jsonify({"error": True})


@app.route("/get-bisi")
def get_bisi():
    try:
        return Response(
            VarManager.get("bisi", {"bi": 0, "si": 0}), mimetype="application/json"
        )
    except:
        return jsonify({"error": True})


# if __name__ == "__main__":
#     app.run("0.0.0.0", debug=True)
