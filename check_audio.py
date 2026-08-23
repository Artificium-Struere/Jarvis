"""Audio stack smoke test. Run this before anything else.

Proves, in order:
  1. sounddevice can see your devices
  2. the microphone opens and actually carries signal
  3. pygame can play sound out
  4. edge-tts can reach Microsoft and produce speech

If step 1 of Jarvis misbehaves, run this first - it tells you which of the
four is broken instead of leaving you guessing.
"""

from __future__ import annotations

import sys
import time
import wave
from pathlib import Path

import config

RECORD_SECONDS = 4.0
TMP_WAV = config.ASSETS_DIR / "_check_recording.wav"


def list_devices() -> bool:
    import sounddevice as sd

    print("=" * 62)
    print("DEVICES")
    print("=" * 62)
    try:
        devices = sd.query_devices()
    except Exception as exc:                             # noqa: BLE001
        print(f"  FAILED to query devices: {exc}")
        return False

    default_in, default_out = sd.default.device
    for idx, dev in enumerate(devices):
        tags = []
        if dev["max_input_channels"] > 0:
            tags.append("in")
        if dev["max_output_channels"] > 0:
            tags.append("out")
        marks = []
        if idx == default_in:
            marks.append("DEFAULT IN")
        if idx == default_out:
            marks.append("DEFAULT OUT")
        print(f"  [{idx:>2}] {dev['name'][:44]:<44} {'/'.join(tags):<7} "
              f"{' '.join(marks)}")
    print()
    print("  To pin a device, set INPUT_DEVICE / OUTPUT_DEVICE in config.py")
    print("  to the index above or a piece of the name.")
    print()
    return True


def record_and_level() -> bool:
    import numpy as np

    import audio

    print("=" * 62)
    print("MICROPHONE")
    print("=" * 62)
    try:
        mic = audio.MicStream()
        mic.start()
    except audio.MicUnavailable as exc:
        print(f"  FAILED: {exc}")
        return False

    print(f"  Say something for {RECORD_SECONDS:.0f} seconds...")
    frames, peak = [], 0.0
    deadline = time.monotonic() + RECORD_SECONDS
    while time.monotonic() < deadline:
        frame = mic.read(timeout=0.5)
        if frame is None:
            continue
        frames.append(frame)
        level = audio.rms(frame)
        peak = max(peak, level)
        bars = int(level * 120)
        print(f"\r  [{'#' * min(bars, 40):<40}] {level:.3f}", end="", flush=True)
    mic.stop()
    print()

    if not frames:
        print("  FAILED: the stream opened but delivered no audio at all.")
        print("  Windows Settings > Privacy & security > Microphone, and check")
        print("  no other app has the device open exclusively.")
        return False

    print(f"  Captured {len(frames)} frames, peak level {peak:.3f}")
    if peak < 0.01:
        print("  WARNING: that is essentially silence. Wrong input device, or")
        print("  the mic is muted in hardware.")

    TMP_WAV.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(TMP_WAV), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(config.SAMPLE_RATE)
        handle.writeframes(np.concatenate(frames).tobytes())
    print(f"  Saved to {TMP_WAV.name}")
    print()
    return peak >= 0.01


def play_back() -> bool:
    import tts

    print("=" * 62)
    print("PLAYBACK")
    print("=" * 62)
    player = tts.Player()
    try:
        player.start()
    except RuntimeError as exc:
        print(f"  FAILED: {exc}")
        return False

    if TMP_WAV.exists():
        print("  Playing your recording back...")
        player.play(TMP_WAV)
    print("  Playback OK")
    print()
    player.shutdown()
    return True


def speak_live() -> bool:
    import tts

    print("=" * 62)
    print("EDGE-TTS")
    print("=" * 62)
    out = config.ASSETS_DIR / "_check_voice.mp3"
    print(f"  Voice: {config.TTS_VOICE}")
    try:
        started = time.monotonic()
        tts.synth("Audio stack is working.", out)
        print(f"  Synthesised in {time.monotonic() - started:.2f}s")
    except tts.TTSUnavailable as exc:
        print(f"  FAILED: {exc}")
        return False

    player = tts.Player()
    player.start()
    player.play(out)
    player.shutdown()
    print("  Speech OK")
    print()
    return True


def main() -> int:
    results = {
        "devices": list_devices(),
        "microphone": record_and_level(),
        "playback": play_back(),
        "edge-tts": speak_live(),
    }
    print("=" * 62)
    for name, ok in results.items():
        print(f"  {name:<12} {'OK' if ok else 'FAILED'}")
    print("=" * 62)
    if all(results.values()):
        print("Audio stack is good. Next: python jarvis.py")
        return 0
    print("Fix the failures above before running jarvis.py.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
