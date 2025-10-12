class Bar {
  constructor(element) {
    this.element = element;
    this.height = 0;
  }

  update(targetHeight, color) {
    this.height = targetHeight;
    this.element.style.height = `${this.height}%`;
    this.element.style.background = `
      linear-gradient(180deg, rgba(255, 255, 255, 0.5), ${color})
    `;
    this.element.style.transition = "height 0.3s ease, background 0.4s ease";
  }
}

class BarAnimation {
  constructor() {
    this.album_background = document.getElementById("album-background");
    this.bars = [];
    this.interval = null;
    this.animationSpeed = 500; // ms
    this.init();
  }

  init() {
    this.album_background.innerHTML = "";
    this.bars = [];

    const width = this.album_background.getBoundingClientRect().width;
    const barWidth = Math.max(10, Math.min(22, width / 40)); // adaptive bar width
    const count = Math.floor(width / (barWidth + 5)); // spacing

    for (let i = 0; i < count; i++) {
      const div = document.createElement("div");
      div.classList.add("bar");
      div.style.width = `${barWidth}px`;
      this.album_background.appendChild(div);
      this.bars.push(new Bar(div));
    }
  }

  start() {
    clearInterval(this.interval);
    this.interval = setInterval(() => {
      const baseColor = this.randomColor();
      this.bars.forEach((bar, i) => {
        const wave = Math.sin((Date.now() / 300 + i) / 2);
        const random = Math.random() * 15;
        const h = 20 + wave * 25 + random;
        bar.update(h, baseColor);
      });
    }, this.animationSpeed);
  }

  stop() {
    clearInterval(this.interval);
    this.bars.forEach((bar) => bar.update(5, "rgba(255,255,255,0.2)"));
  }

  randomColor() {
    const hue = Math.floor(Math.random() * 360);
    return `hsl(${hue}, 80%, 60%)`;
  }
}

class BackgroundChanger {
  constructor() {
    this.cover = document.querySelector("body");
  }

  changeBackground(background_index) {
    this.cover.style.transition = "background-image 1.5s ease-in-out";
    this.cover.style.backgroundImage = `url("/static/images/background/image-${background_index}.jpg")`;
  }
}

class LiveRadio {
  constructor() {
    this.audioPlayer = document.querySelector("audio");
    this.songTitle = document.querySelector("#song-title");
    this.playBtn = document.querySelector("#play-btn");
    this.albumArt = document.querySelector("#player-album");
    this.albumBackground = document.querySelector("#album-background");
    this.timeSlider = document.querySelector("#time-slider");
    this.playing = false;
    this.songLoaded = false;
    this.songPath = "";
    this.songId = 0;

    this.barAnim = new BarAnimation();
    this.backgroundChanger = new BackgroundChanger();

    this.init();
  }

  init() {
    this.audioPlayer.volume = 1;
    this.playBtn.addEventListener("click", () => this.togglePlayPause());
    this.audioPlayer.addEventListener("timeupdate", () =>
      this.updateTimeSlider()
    );
    this.barAnim.stop();
    this.fetchSong();
    setInterval(() => this.fetchBisi(), 2000);
  }

  togglePlayPause() {
    if (!this.songLoaded) return;
    if (!this.playing) {
      this.syncPosition();
      this.audioPlayer.play().catch(console.error);
      this.playBtn.textContent = "❚❚";
      this.barAnim.start();
      this.albumArt.classList.add("rot");
    } else {
      this.audioPlayer.pause();
      this.playBtn.textContent = "▶";
      this.barAnim.stop();
      this.albumArt.classList.remove("rot");
    }
    this.playing = !this.playing;
  }

  fetchSong() {
    fetch("/get-song")
      .then((res) => res.json())
      .then((data) => {
        if (data.error) return console.warn("❌ Song load failed");
        this.audioPlayer.src = "data:audio/mp3;base64," + data.audio;
        this.songTitle.textContent = data.title || "Unknown Song";
        this.albumBackground.style.backgroundImage = `url(data:image/png;base64,${data.image})`;
        this.audioPlayer.onloadedmetadata = () => {
          this.songLoaded = true;
          if (this.playing) this.togglePlayPause(); // sync state
        };
      })
      .catch((err) => console.error("Fetch song error:", err));
  }

  syncPosition() {
    fetch("/get-song-position")
      .then((res) => res.json())
      .then((data) => {
        if (!data || !("t" in data)) return;
        this.audioPlayer.currentTime =
          ((Date.now() / 1000) % data.mod) - data.t;
      })
      .catch((err) => console.error(err));
  }

  fetchBisi() {
    fetch("/get-bisi")
      .then((res) => res.json())
      .then((data) => {
        if (!data || "error" in data) return;
        this.backgroundChanger.changeBackground(data.bi);
        if (this.songId !== data.si) {
          this.songId = data.si;
          this.songLoaded = false;
          this.fetchSong(); // load new song
        }
      })
      .catch((err) => console.error(err));
  }

  updateTimeSlider() {
    if (!this.audioPlayer.duration) return;
    this.timeSlider.value =
      (this.audioPlayer.currentTime / this.audioPlayer.duration) * 100;
  }
}

const liveRadio = new LiveRadio();

liveRadio.update();
setInterval(() => liveRadio.update(), 2000);
window.addEventListener("resize", () => liveRadio.barAnim.init());

console.log("🎵 Live Radio Debug: Ready!");
