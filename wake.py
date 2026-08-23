"""Wake word detection with openwakeword.

Runs entirely on your machine. Nothing leaves the PC until this fires.
"""

from __future__ import annotations

import time
from pathlib import Path

import config


class WakeUnavailable(RuntimeError):
    """The wake word model could not be loaded."""


def model_paths(name: str = config.WAKE_MODEL):
    """Locate the pretrained .onnx for `name` inside the installed package."""
    try:
        import openwakeword
    except ImportError as exc:                           # pragma: no cover
        raise WakeUnavailable("openwakeword is not installed") from exc

    pkg_dir = Path(openwakeword.__file__).parent / "resources" / "models"
    return sorted(pkg_dir.glob(f"{name}*.onnx"))


def ensure_models(name: str = config.WAKE_MODEL) -> None:
    """Download the pretrained models if they are not already on disk."""
    from openwakeword.utils import download_models

    if model_paths(name):
        return
    try:
        download_models(model_names=[name])
    except TypeError:
        # Older signature: no model_names kwarg, fetches everything.
        download_models()
    if not model_paths(name):
        raise WakeUnavailable(
            f"Downloaded openwakeword models but found no '{name}' model. "
            "Check the model name against openwakeword's pretrained list."
        )


class WakeListener:
    """Feed it frames, ask it if the wake word fired.

    Detection is edge-triggered with a refractory period, so one spoken
    "Hey Jarvis" produces exactly one fire, not three.
    """

    def __init__(self, name: str = config.WAKE_MODEL,
                 threshold: float = config.WAKE_THRESHOLD,
                 refractory: float = config.WAKE_REFRACTORY_SECONDS):
        self.name = name
        self.threshold = threshold
        self.refractory = refractory
        self._last_fire = 0.0
        self.last_score = 0.0

        ensure_models(name)
        try:
            from openwakeword.model import Model
        except ImportError as exc:                       # pragma: no cover
            raise WakeUnavailable("openwakeword is not installed") from exc

        paths = model_paths(name)
        try:
            self._model = Model(
                wakeword_models=[str(paths[0])],
                inference_framework=config.WAKE_INFERENCE_FRAMEWORK,
            )
        except Exception as exc:                         # noqa: BLE001
            raise WakeUnavailable(
                f"Could not load the '{name}' wake word model: {exc}"
            ) from exc

    def score(self, frame) -> float:
        """Highest confidence across the loaded models for this frame."""
        if frame is None:
            return 0.0
        predictions = self._model.predict(frame)
        matching = [v for k, v in predictions.items() if self.name.split("_")[-1] in k]
        self.last_score = float(max(matching or predictions.values() or [0.0]))
        return self.last_score

    def detect(self, frame) -> bool:
        """True exactly once per utterance of the wake word."""
        score = self.score(frame)
        if score < self.threshold:
            return False
        now = time.monotonic()
        if now - self._last_fire < self.refractory:
            return False
        self._last_fire = now
        self.reset()
        return True

    def reset(self):
        """Clear the model's internal audio buffer after a detection."""
        try:
            self._model.reset()
        except Exception:                                # noqa: BLE001
            pass
