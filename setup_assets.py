"""One-time install step.

Downloads the wake word models and renders the phrases that have to play
instantly to disk. Run it once after pip install, and again any time you
change TTS_VOICE or GREETING_TEXT in config.py.

    python setup_assets.py           # only render what is missing
    python setup_assets.py --force   # re-render everything
"""

from __future__ import annotations

import argparse
import sys

import config


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare JARVIS assets.")
    parser.add_argument("--force", action="store_true",
                        help="re-render phrases that already exist")
    args = parser.parse_args()

    config.ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    failures = []

    # -------------------------------------------------------- wake word models
    print(f"Wake word model: {config.WAKE_MODEL}")
    try:
        import wake
        wake.ensure_models()
        paths = wake.model_paths()
        print(f"  ready: {paths[0].name}")
    except Exception as exc:                             # noqa: BLE001
        print(f"  FAILED: {exc}")
        failures.append("wake word models")

    # ------------------------------------------------------------ tts phrases
    print(f"Voice: {config.TTS_VOICE}")
    import tts

    for name, text in config.CACHED_PHRASES.items():
        path = config.phrase_path(name)
        if path.exists() and not args.force:
            print(f"  {name}: already rendered ({path.name})")
            continue
        print(f"  {name}: rendering {text!r} ...", end=" ", flush=True)
        try:
            tts.synth(text, path)
            print(f"{path.stat().st_size // 1024} KB")
        except tts.TTSUnavailable as exc:
            print("FAILED")
            print(f"    {exc}")
            failures.append(f"phrase '{name}'")

    print()
    if failures:
        print("Setup incomplete: " + ", ".join(failures))
        print("Fix the above and run this again. Jarvis will not start without "
              "the greeting file.")
        return 1

    print(f"Assets ready in {config.ASSETS_DIR}")
    print("Next: python check_audio.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
