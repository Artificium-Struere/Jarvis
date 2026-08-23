"""JARVIS configuration.

Every tunable number, name and phrase in the system lives in this file. Nothing
here imports the rest of the app, so setup_assets.py, the smoke tests and the
main loop can all read it without pulling in audio libraries.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
MEMORY_DIR = ROOT / "memory"

# --------------------------------------------------------------- identity --
USER_NAME = "Kev"
GREETING_TEXT = "What's up killa Kev!"

# ------------------------------------------------------------------ audio --
# openwakeword and faster-whisper both want 16 kHz mono int16. Do not change
# SAMPLE_RATE unless you are replacing both of them.
SAMPLE_RATE = 16000
FRAME_SAMPLES = 1280          # 80 ms at 16 kHz - openwakeword's native frame size

# None = whatever Windows has set as the default device.
# Otherwise: an integer index, or a substring of the device name.
# Run `python check_audio.py` to see the list.
INPUT_DEVICE = None
OUTPUT_DEVICE = None          # pygame follows the system default output

# If no audio frame arrives for this long while the mic is supposed to be
# running, the device has gone away (headphones unplugged, USB mic pulled).
# Reopen it rather than sitting there deaf.
MIC_STALL_SECONDS = 3.0
MIC_REOPEN_BACKOFF = (0.5, 1.0, 2.0, 4.0)   # seconds between reopen attempts

# ------------------------------------------------------------- wake word ---
WAKE_MODEL = "hey_jarvis"     # openwakeword pretrained model, matches "Hey Jarvis"
# Raise toward 0.8 if it fires when you did not speak to it.
# Lower toward 0.3 if it misses you. 0.5 is the openwakeword default.
WAKE_THRESHOLD = 0.5
# Ignore further detections for this long after one fires, so a single
# "Hey Jarvis" cannot trigger three times.
WAKE_REFRACTORY_SECONDS = 2.0
WAKE_INFERENCE_FRAMEWORK = "onnx"

# ------------------------------------------------------------------- tts ---
TTS_VOICE = "en-GB-RyanNeural"
TTS_RATE = "+0%"
TTS_VOLUME = "+0%"

# Rendered to disk once by setup_assets.py and played from file thereafter.
# The greeting in particular must never be generated live - a two second pause
# before "What's up killa Kev" kills the whole illusion.
CACHED_PHRASES = {
    "greeting": GREETING_TEXT,
    "mic_error": "I can't hear you. Something is wrong with the microphone.",
    "offline": "I'm offline. The network is down.",
}


def phrase_path(name: str) -> Path:
    """Where a cached phrase lives on disk."""
    return ASSETS_DIR / f"{name}.mp3"
