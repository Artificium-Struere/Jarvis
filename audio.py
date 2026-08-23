"""Microphone input.

One job: hand out 16 kHz mono int16 frames, and survive Windows moving the
audio device out from under us. Everything that listens (wake word now,
speech capture later) reads from a single MicStream so there is exactly one
place that can be stopped while Jarvis is speaking.
"""

from __future__ import annotations

import queue
import time

import numpy as np
import sounddevice as sd

import config


class MicUnavailable(RuntimeError):
    """The input device could not be opened at all."""


def resolve_device(spec):
    """Turn None / an int / a name substring into a sounddevice index."""
    if spec is None:
        return None
    if isinstance(spec, int):
        return spec
    needle = str(spec).lower()
    for idx, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] > 0 and needle in dev["name"].lower():
            return idx
    raise MicUnavailable(f"No input device matching {spec!r}")


class MicStream:
    """A restartable input stream.

    pause() genuinely stops the stream rather than throwing frames away - while
    Jarvis is talking the microphone is closed, so it cannot hear itself
    through the speakers and start a conversation with itself.
    """

    def __init__(self, device=config.INPUT_DEVICE,
                 samplerate=config.SAMPLE_RATE,
                 blocksize=config.FRAME_SAMPLES):
        self.device_spec = device
        self.samplerate = samplerate
        self.blocksize = blocksize
        self._stream = None
        self._queue: queue.Queue = queue.Queue(maxsize=64)
        self._last_frame = 0.0
        self._running = False
        self.last_error = None

    # ------------------------------------------------------------- lifecycle
    def start(self):
        if self._running:
            return
        self._open()
        self._running = True

    def stop(self):
        self._running = False
        self._close()

    def pause(self):
        """Go deaf. Called before playback."""
        if self._stream is not None:
            self._close()

    def resume(self):
        """Come back. Drops anything buffered so we do not process stale audio."""
        if not self._running:
            return
        if self._stream is None:
            self._open()
        self.drain()

    def drain(self):
        while True:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                return

    # ------------------------------------------------------------------ read
    def read(self, timeout: float = 1.0):
        """Return one int16 frame, or None if nothing arrived in `timeout`.

        A None does not necessarily mean trouble - it can just be a slow
        moment - but a long run of them means the device went away, so we
        check the clock and reopen.
        """
        try:
            frame = self._queue.get(timeout=timeout)
            self._last_frame = time.monotonic()
            return frame
        except queue.Empty:
            if self._running and self._stalled():
                self._reopen()
            return None

    def _stalled(self) -> bool:
        return (time.monotonic() - self._last_frame) > config.MIC_STALL_SECONDS

    # -------------------------------------------------------------- internals
    def _callback(self, indata, frames, time_info, status):
        if status:
            # Overflows are normal under load and not worth reporting; keep the
            # last one around so the tray can show it if things get bad.
            self.last_error = str(status)
        try:
            self._queue.put_nowait(np.frombuffer(bytes(indata), dtype=np.int16).copy())
        except queue.Full:
            # Prefer fresh audio over complete audio: drop the oldest frame.
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(np.frombuffer(bytes(indata), dtype=np.int16).copy())
            except (queue.Empty, queue.Full):
                pass

    def _open(self):
        last_exc = None
        for delay in (0.0,) + tuple(config.MIC_REOPEN_BACKOFF):
            if delay:
                time.sleep(delay)
            try:
                sd._terminate()      # force PortAudio to re-enumerate devices
                sd._initialize()
            except Exception:
                pass                 # older sounddevice builds; not fatal
            try:
                device = resolve_device(self.device_spec)
                stream = sd.RawInputStream(
                    samplerate=self.samplerate,
                    blocksize=self.blocksize,
                    device=device,
                    dtype="int16",
                    channels=1,
                    callback=self._callback,
                )
                stream.start()
                self._stream = stream
                self._last_frame = time.monotonic()
                self.last_error = None
                return
            except Exception as exc:                     # noqa: BLE001
                last_exc = exc
        self._stream = None
        self.last_error = str(last_exc)
        raise MicUnavailable(
            f"Could not open the microphone: {last_exc}. "
            "Check Windows Settings > Privacy > Microphone, and that no other "
            "app has exclusive control of the device."
        )

    def _close(self):
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:                            # noqa: BLE001
                pass
            self._stream = None
        self.drain()

    def _reopen(self):
        print("[mic] input device stalled - reopening", flush=True)
        self._close()
        try:
            self._open()
        except MicUnavailable as exc:
            print(f"[mic] {exc}", flush=True)

    # ---------------------------------------------------------------- context
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()
        return False


def rms(frame: np.ndarray) -> float:
    """Amplitude of a frame, 0.0 - 1.0. Used by the level meter and, later, by
    silence detection."""
    if frame is None or len(frame) == 0:
        return 0.0
    return float(np.sqrt(np.mean((frame.astype(np.float32) / 32768.0) ** 2)))
