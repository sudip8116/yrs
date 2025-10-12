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
    this.song_title = document.querySelector("#song-title");
    this.play_btn = document.querySelector("#play-btn");
    this.album_art = document.querySelector("#player-album");
    this.album_background = document.querySelector("#album-background");
    this.time_slider = document.querySelector("#time-slider");

    this.playing = false;
    this.song_loaded = false;
    this.song_index = 0;

    this.barAnim = new BarAnimation();
    this.backgroundChanger = new BackgroundChanger();

    this.init();
  }

  init() {
    this.audioPlayer.volume = 1;
    this.play_btn.addEventListener("click", () => this.togglePlayPause());
    this.audioPlayer.addEventListener("timeupdate", () =>
      this.handleTimeUpdate()
    );
    this.barAnim.stop();
    this.getSong();
  }

  togglePlayPause() {
    if (!this.song_loaded) return;

    if (!this.playing) {
      this.sync();
      this.audioPlayer.play().catch(console.error);
      this.play_btn.textContent = "❚❚";
      this.barAnim.start();
      this.album_art.classList.add("rot");
    } else {
      this.audioPlayer.pause();
      this.play_btn.textContent = "▶";
      this.barAnim.stop();
      this.album_art.classList.remove("rot");
    }
    this.playing = !this.playing;
  }

  getSong() {
    this.song_loaded = false;

    fetch("/get-song")
      .then((res) => res.json())
      .then((data) => {
        if (data.error) return console.error("❌ Song load failed!");

        this.song_title.textContent = data.title;
        this.audioPlayer.src = `data:audio/mp3;base64,${data.audio}`;
        this.album_background.style.backgroundImage = `url("data:image/png;base64,${data.image}")`;

        this.audioPlayer.onloadedmetadata = () => {
          this.song_loaded = true;
          console.log("✅ Song loaded");

          if (this.playing) {
            this.playing = false;
            this.togglePlayPause();
          }
        };
      });
  }

  sync() {
    fetch("/get-song-position")
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          this.audioPlayer.currentTime = 0;
          return;
        }
        this.audioPlayer.currentTime =
          ((Date.now() / 1000) % data.mod) - data.t;
      });
  }

  handleTimeUpdate() {
    if (!this.audioPlayer.duration) return;
    this.time_slider.value =
      (this.audioPlayer.currentTime / this.audioPlayer.duration) * 100;
  }

  check_song_index(index) {
    if (this.song_index !== index) {
      this.song_index = index;
      this.getSong();
    }
  }

  update() {
    fetch("/get-bisi")
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        if ("error" in data) return console.log("bisi failed!");
        this.backgroundChanger.changeBackground(data.bi);
        this.check_song_index(data.si);
      });
  }
}

// 🎧 Initialize and start updating
const liveRadio = new LiveRadio();
liveRadio.update();
setInterval(() => liveRadio.update(), 2000);
window.addEventListener("resize", () => liveRadio.barAnim.init());

console.log("🎵 Live Radio Debug: Ready!");
