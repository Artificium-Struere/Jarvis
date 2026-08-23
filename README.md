# JARVIS

An always-on voice assistant for Windows. Wake word, ears, mouth, hands.
Claude Code is the brain — this repo does not reimplement file search, shell
or web tools, it hands those to `claude -p`.

**Status: step 1 of 6.** Wake word and greeting only. No conversation yet.

| Step | What | State |
|---|---|---|
| 1 | Wake word + cached greeting | **built, needs testing on your machine** |
| 2 | Full voice round trip, fast lane | not started |
| 3 | Claude Code bridge, allowlist, session resume | not started |
| 4 | `desktop.py` — paste / type / focus | not started |
| 5 | Tray icon, global hotkey, mute, barge-in | not started |
| 6 | `CLAUDE.md`, `memory/`, guardrails, start on boot | not started |

---

## Step 1 setup

Python 3.11 is the safe target on Windows. 3.12 works. 3.13 has patchy
`onnxruntime` wheels — avoid it.

```bat
git clone <this repo>
cd Jarvis
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Then, in order:

```bat
python setup_assets.py     :: downloads the wake model, renders the greeting
python check_audio.py      :: proves the audio stack works
python jarvis.py           :: say "Hey Jarvis"
```

### What each one should do

**`setup_assets.py`** downloads the pretrained `hey_jarvis` model and renders
three phrases to `assets/` as mp3 — the greeting plus two error phrases. The
greeting is rendered once, here, and played from disk forever after. It is
never generated live; a two second pause before "What's up killa Kev" would
kill the whole illusion. Re-run with `--force` after changing `TTS_VOICE` or
`GREETING_TEXT`.

**`check_audio.py`** is the thing to run when something is wrong. It tests four
things separately and tells you which one broke: device enumeration, the
microphone (with a live level meter — talk at it and watch the bar move),
playback, and edge-tts reaching Microsoft. Run this before you debug anything
else.

**`jarvis.py`** listens. Say "Hey Jarvis" and it says "What's up killa Kev!"
straight back. Then it goes back to listening. That is all step 1 does.

## Tuning the wake word

If it fires when you did not speak to it, or misses you:

```bat
python jarvis.py --tune
```

That prints the live confidence score. Say the wake phrase a few times, note
what it peaks at, say some other things and note the noise floor, then set
`WAKE_THRESHOLD` in `config.py` somewhere between the two. Default is `0.5`.

## Everything tunable lives in `config.py`

Input and output device, sample rate, wake model and threshold, refractory
period, mic stall timeout, voice, rate, and the cached phrases themselves.
Nothing is hardcoded anywhere else.

To pin a specific microphone, run `check_audio.py`, find your device in the
list, and set `INPUT_DEVICE` to its index or a piece of its name.

## Cost

Zero so far. `openwakeword`, `onnxruntime` and `faster-whisper` run locally.
`edge-tts` uses Microsoft's free neural voices with no key and no account.
Steps 2 and 3 route through your existing Claude Code subscription rather than
a metered API key. Running total per month: nothing.

## Troubleshooting step 1

| Symptom | Cause |
|---|---|
| `STOPPED: No greeting audio` | run `python setup_assets.py` |
| `check_audio` mic peak near 0.000 | wrong input device, or muted in hardware |
| mic opens but delivers no frames | Windows Settings → Privacy → Microphone, or another app holds the device exclusively |
| edge-tts fails | no network, or a proxy is blocking it — it is the only part of step 1 that touches the internet |
| greeting triggers itself repeatedly | shouldn't happen: the mic is explicitly closed during playback. If it does, report it |
