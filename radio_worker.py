from scripts.live_radio import LiveRadio

if __name__ == "__main__":
    radio = LiveRadio()
    radio.start()
    print("🎵 Radio worker running...")
    while True:
        pass  # keep worker alive forever
