# JARVIS scope

Output of mh1 Prelim. Client: Artificium Struere. Owner and only user: Kev.
Status: **mh1.1 and mh1.2 done Nov 9. mh1.3 and mh1.4 are open STOPs.**

---

## mh1.1 Discovery

These findings come from the evidence: the repo, PR #1, and its README and
config. This session had no live owner interview, so every point the code
can't answer is listed under "Questions for the owner" and still needs Kev's
answer before signing.

### What it is

An always-on voice assistant for Windows. It has a wake word, ears, a mouth and
hands. Claude Code (`claude -p`) is the brain. JARVIS does not reimplement file
search, shell or web tools. It hands those to Claude Code.

### Real data, counted

| Thing | Count | Source |
|---|---|---|
| Users | 1 (Kev) | `config.USER_NAME` |
| Machines | 1 Windows PC (not yet run there) | README "needs testing on your machine" |
| Wake models | 1 pretrained (`hey_jarvis`, onnx), downloaded at setup | `config.WAKE_MODEL` |
| Cached phrases | 3 (greeting, mic_error, offline), rendered at setup | `config.CACHED_PHRASES` |
| Stored records / memory files | 0 today. `memory/` is planned for step 6 | `config.MEMORY_DIR` |
| Code on PR #1 | 11 files, 1,003 lines | PR #1 |
| Code on main | 1 file (README) | `main` |

### User surfaces

Kev is the only user of every surface.

| # | Surface | Flow | Views / outputs | Epic |
|---|---|---|---|---|
| S1 | Voice | "Hey Jarvis" → instant cached greeting → (later) speak a request → spoken answer → back to listening | audio only: greeting, answers, error phrases | E1, E2 |
| S2 | Console | start `jarvis.py`, watch wake events, `--tune` shows the live score bar | banner, status lines, tune meter, loud STOPPED errors | E1 |
| S3 | Setup and diagnostics | `setup_assets.py` once, then `check_audio.py` when anything breaks | asset report; 4-layer check: devices, mic meter, playback, edge-tts | E1 |
| S4 | Claude Code bridge | voice request → allowlist check → `claude -p` with a resumed session → spoken summary | none of its own; it speaks through S1 | E3 |
| S5 | Desktop hands | Jarvis pastes, types into or focuses other windows | effects in other apps | E4 |
| S6 | Tray and hotkey | tray icon state, global hotkey to talk or mute, barge-in to interrupt | tray icon, tray menu, mute state | E5 |
| S7 | Memory and guardrails | `CLAUDE.md` rules, `memory/` notes, starts on boot | text files Kev can read and edit | E6 |

### Questions for the owner (answer before signing)

1. Which tasks should the fast lane (E2) answer locally, and which go to Claude Code (E3)?
2. What may the allowlist (E3) and desktop hands (E4) do without asking first, and what always needs a spoken confirm?
3. Should transcripts or audio be kept? If so, where are they kept and for how long?
4. Which Claude Code plan runs E3, and what monthly usage ceiling is acceptable? (spend cap, rule 6)
5. Which mic and speakers does it run on: a headset, or open speakers? This decides how much barge-in and echo work E5 needs.
6. Which Windows and Python versions? The README targets Python 3.11. It says 3.13 has patchy onnxruntime wheels.

---

## mh1.2 Concept

One package, JARVIS, staged into six epics. These are the README's six steps.

| Epic | What | State of code |
|---|---|---|
| E1 | Wake word + cached greeting | on PR #1, unverified on target machine |
| E2 | Full voice round trip, fast lane (local faster-whisper transcription → reply) | not started |
| E3 | Claude Code bridge: allowlist, session resume | not started |
| E4 | `desktop.py`: paste / type / focus | not started |
| E5 | Tray icon, global hotkey, mute, barge-in | not started |
| E6 | `CLAUDE.md`, `memory/`, guardrails, start on boot | not started |

### Cut list (proposed, Kev confirms at signing)

- Its own file search, shell or web tools. Claude Code does these.
- Cloud speech-to-text and paid TTS voices. The stack stays local and free.
- Custom wake word training. It uses the pretrained `hey_jarvis` model.
- Multi-user support, voice ID, and other machines (Mac, Linux, phone).
- A GUI beyond the tray icon.

---

## mh1.3 Proposal: STOP, builder sets the price

Draft monthly running costs, from the code:

| Service | Cost | Note |
|---|---|---|
| openWakeWord + onnxruntime | $0 | local |
| faster-whisper (E2) | $0 | local, one model download |
| edge-tts | $0 | free Microsoft neural voices, no key. This is an unofficial endpoint and may break or be withdrawn |
| Claude Code (E3) | already paid | Kev's existing plan. No metered API key. Needs a named usage ceiling (rule 6) |
| GitHub | $0 | existing account |
| **Total new per month** | **$0** | |

**Price**: ______ (Kev writes this; an internal build can be $0)
**Monthly running cost accepted**: ______
**Spend cap for Claude Code usage**: ______

## mh1.4 Contract: STOP, client signs

No new code before this line is signed. PR #1 is held at mh3.2 until then.

Signed (Kev, for Artificium Struere): ______  Date: ______
