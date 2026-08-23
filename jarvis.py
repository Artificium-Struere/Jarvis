"""JARVIS - step 1: wake word and greeting.

    python jarvis.py            listen for "Hey Jarvis", greet, go back to sleep
    python jarvis.py --tune     same, but print the live wake score so you can
                                set WAKE_THRESHOLD in config.py

Nothing leaves this machine. The wake word runs locally, the greeting is
played from a file rendered at install time. Later steps hang recording,
transcription and routing off the same loop.
"""

from __future__ import annotations

import argparse
import sys
import time

import config

BANNER = r"""
   _   _   _____   _____  _   _ _____ ____
  | | / \ |  _  \ \  _  /| | | |  ___/ ___|
  | |/ _ \| |_| |  \ V / | | | | |___\___ \
 _| / ___ |  _  /   | |  | |_| |___  |___) |
|__/_/   \_|_| \_\  |_|   \___/|____/|____/
"""


def die(message: str, hint: str = "") -> int:
    """Fail loudly. A silent failure is the worst outcome this thing can have."""
    print()
    print(f"  STOPPED: {message}")
    if hint:
        print(f"  {hint}")
    print()
    return 1


def speak_cached(player, name: str, block: bool = True) -> bool:
    path = config.phrase_path(name)
    if not path.exists():
        return False
    player.play(path, block=block)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="JARVIS voice assistant.")
    parser.add_argument("--tune", action="store_true",
                        help="print the live wake word score for threshold tuning")
    args = parser.parse_args()

    print(BANNER)

    # ---------------------------------------------------------------- assets
    greeting = config.phrase_path("greeting")
    if not greeting.exists():
        return die(
            f"No greeting audio at {greeting}",
            "Run: python setup_assets.py",
        )

    # ---------------------------------------------------------------- output
    import tts

    player = tts.Player()
    try:
        player.start()
    except RuntimeError as exc:
        return die(str(exc), "Run: python check_audio.py")

    # ------------------------------------------------------------- wake word
    print("  Loading wake word model...", end=" ", flush=True)
    import wake

    try:
        listener = wake.WakeListener()
    except wake.WakeUnavailable as exc:
        print()
        return die(str(exc), "Run: python setup_assets.py")
    print(f"'{config.WAKE_MODEL}' ready (threshold {config.WAKE_THRESHOLD})")

    # ------------------------------------------------------------------- mic
    import audio

    mic = audio.MicStream()
    try:
        mic.start()
    except audio.MicUnavailable as exc:
        speak_cached(player, "mic_error")
        return die(str(exc), "Run: python check_audio.py")

    print(f"  Mic open at {config.SAMPLE_RATE} Hz")
    print()
    print('  Listening for "Hey Jarvis".  Ctrl+C to quit.')
    print()

    deaf_since = None
    last_tune_print = 0.0

    try:
        while True:
            frame = mic.read(timeout=1.0)

            if frame is None:
                # Degrade loudly rather than sitting there pretending to listen.
                if deaf_since is None:
                    deaf_since = time.monotonic()
                elif time.monotonic() - deaf_since > 10.0:
                    print("  [!] No audio from the microphone for 10s. "
                          "Device unplugged or blocked?", flush=True)
                    speak_cached(player, "mic_error")
                    deaf_since = time.monotonic()
                continue
            deaf_since = None

            fired = listener.detect(frame)

            if args.tune:
                now = time.monotonic()
                if now - last_tune_print > 0.1:
                    score = listener.last_score
                    bar = "#" * int(score * 40)
                    print(f"\r  score [{bar:<40}] {score:.3f}", end="", flush=True)
                    last_tune_print = now

            if not fired:
                continue

            if args.tune:
                print()
            print(f"  [{time.strftime('%H:%M:%S')}] wake word "
                  f"(score {listener.last_score:.3f}) -> greeting", flush=True)

            # Deaf while speaking. Without this it hears the greeting through
            # the speakers and triggers on itself.
            mic.pause()
            try:
                player.play(greeting, block=True)
            finally:
                mic.resume()
                listener.reset()

    except KeyboardInterrupt:
        print("\n  Shutting down.")
    finally:
        mic.stop()
        player.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
