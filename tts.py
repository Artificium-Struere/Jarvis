"""Speech out: edge-tts for synthesis, pygame.mixer for playback.

Two paths deliberately kept separate:

  synth()  - hits Microsoft's servers, takes ~300-800 ms, needs network.
  Player   - plays a file already on disk, takes milliseconds, needs nothing.

Anything latency-critical (the greeting, error phrases) is rendered once by
setup_assets.py and only ever goes through Player.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame                                            # noqa: E402

import config                                            # noqa: E402


class TTSUnavailable(RuntimeError):
    """Synthesis failed - almost always the network."""


# ----------------------------------------------------------------- synthesis
async def _synth_async(text: str, path: Path, voice: str, rate: str, volume: str):
    import edge_tts

    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
    await communicate.save(str(path))


def synth(text: str, path: Path,
          voice: str = config.TTS_VOICE,
          rate: str = config.TTS_RATE,
          volume: str = config.TTS_VOLUME) -> Path:
    """Render `text` to an mp3 at `path`. Raises TTSUnavailable on failure."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        asyncio.run(_synth_async(text, path, voice, rate, volume))
    except Exception as exc:                             # noqa: BLE001
        raise TTSUnavailable(f"edge-tts failed: {exc}") from exc
    if not path.exists() or path.stat().st_size == 0:
        raise TTSUnavailable(
            f"edge-tts produced no audio for {text!r}. "
            "Usually means no network, or the voice name is wrong."
        )
    return path


# ------------------------------------------------------------------ playback
class Player:
    """Wraps pygame.mixer.music. One stream, so a new play() cuts off the old
    one - which is exactly what barge-in needs later."""

    def __init__(self):
        self._ready = False

    def start(self):
        if self._ready:
            return
        try:
            pygame.mixer.init()
        except pygame.error as exc:
            raise RuntimeError(
                f"Could not open an audio output device: {exc}. "
                "Check that Windows has a working playback device selected."
            ) from exc
        self._ready = True

    def stop(self):
        """Cut playback off mid-sentence."""
        if self._ready:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass

    def shutdown(self):
        if self._ready:
            try:
                pygame.mixer.quit()
            except pygame.error:
                pass
            self._ready = False

    def is_playing(self) -> bool:
        return bool(self._ready and pygame.mixer.music.get_busy())

    def play(self, path, block: bool = True):
        """Play a file. Reopens the mixer if Windows swapped the output device."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"No audio file at {path}")
        self.start()
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play()
        except pygame.error:
            # Output device changed underneath us - headphones in or out.
            self.shutdown()
            self.start()
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play()
        if block:
            self.wait()

    def wait(self):
        while self.is_playing():
            pygame.time.wait(20)
