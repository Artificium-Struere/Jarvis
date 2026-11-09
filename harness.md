# harness.md

The one source for this project. Every session reads this first.
Three parts: 1 The play, 2 Status, 3 Model log.

---

# Part 1: The play

The Super Harness Book. State Mint mastermind, Nov 8, 2026.
Copied in by Apply. Changed only by the new model pass (below), never edited ad hoc.

## The idea

A mini harness (mh) is one phase of four steps. The super harness (SH) chains
all four in a ring. Post feeds the next Prelim, so lessons become rules before
the next build starts.

- **mh1 Prelim**: Discovery, Concept, Proposal, Contract. Stops: price, client signs.
- **mh2 Design**: Wireframes, Prototype, Walkthrough, Freeze. Stop: client signs off.
- **mh3 Dev**: Branch, Push, Merge, Deploy. Stop: the gates.
- **mh4 Post**: Code sweep, Security sweep, Post mortem, Upskill. Stop: builder approves new rules.

16 steps, 5 human stops. The agent runs the rest. mh2.3 means mini 2, step 3.

## Run it local

Run your agent on your own machine, not in a cloud session. Local lets you turn
on bypass permissions (Claude Code: `--dangerously-skip-permissions`), so the
agent stops asking before every command and the ring runs at full speed.

Bypass skips the confirm clicks, not the STOPs. The 5 human stops and the mh3
gates still hold. Keep production keys out of reach until mh3.4.

## mh1 Prelim

What gets built, for whom, for how much.

1. **Discovery**: interview the owner. Count the real data (records, files,
   users). Name every user surface (sales, ops, customer, vendor): who uses it,
   the flow, the views.
2. **Concept**: one package staged into epics, plus the cut list.
3. **Proposal**: price and monthly running costs. **STOP: the builder sets the price.**
4. **Contract**: **STOP: the client signs.** No code before this.

Output: `scope.md`.
Exit: a signed scope with every surface named.

## mh2 Design

What it looks like, before a line of code.

1. **Wireframes**: a design canvas, every screen of every surface. Doc 1 of 3.
2. **Prototype**: clickable, real sample data. Doc 2 of 3.
3. **Walkthrough**: the client clicks through it. Log every change and fold it in.
4. **Freeze**: **STOP: client signs off.** New ideas go on a concepts canvas,
   never on the frozen target.

Output: canvas link, prototype link, freeze date.
Exit: a frozen design the build is checked against.

## mh3 Dev

The ship pipeline, one step per stage.

1. **Branch**: work on a side branch, never on main.
2. **Push**: on GitHub, PR opened.
3. **Merge**: PR lands in main. Preview builds on the PR, production on the merge.
4. **Deploy**: live on the client's domain. Doc 3 of 3: live vs design, side by side.

**The gates**: spending money, migrating the live database, app store
publishing, rotating keys, sending to a contact list. STOP on those, nothing else.

Verify: drive it in a browser and say what you saw. "It builds" isn't verification.
Exit: live, verified, matching the frozen design.

## mh4 Post

Where the ring closes.

1. **Code sweep**: dead code, drift from the design, tech debt.
2. **Security sweep**: keys, permissions, row level access. Every paid service
   has a named spend cap.
3. **Post mortem**: what broke, what it cost, what got learned twice.
4. **Upskill**: lessons become rules, skills and agent changes.
   **STOP: the builder approves new rules.**

Output: `post.md` and a diff of the rules.
Exit: the next mh1 starts smarter than this one.

## The four pillars

One Build Hub per client, four tabs. The ring fills them.

- **P1 Data KPIs**: PRs merged, PRs a day, lines shipped, agent and connector use. Fed by mh3, mh4.
- **P2 Projects**: every build, its step, who it waits on, three docs per app. Fed by every mh.
- **P3 Designs**: canvases, prototypes, live vs design, brand system and drift. Fed by mh2, mh3.4.
- **P4 Platforms**: every service, key names only, spend caps, state. Fed by mh1, mh4.2.

## Build Hub layout

Every build gets a Build Hub: the one place the client sees where the build is,
what it looks like and what it runs on. Make it at mh1.4, in the client's
brand, share it with the client's owner, and update it every time a build
changes step. Lay it out like this:

- **Top bar**: client logo, "Build Hub", tabs Overview, Projects, Designs, Platforms.
- **Overview**: four boxes, mh1 to mh4, each with its build count and names.
  Tap one for its steps, the builds at each, and the human stops. Then big
  numbers for shipping (PRs merged, PRs a day, lines shipped, migrations) and
  call counts for agents, skills and connectors.
- **Projects**: one line per build: build, step, where it runs, who it waits
  on. Tap for notes. Then the three docs per app, with "Owed" where one is missing.
- **Designs**: every design as a thumbnail in a phone or desktop frame, or a
  list. Filter, search, tap to preview. Then how to edit, the brand system,
  and a drift table.
- **Platforms**: one line per service: used for, login and key count masked,
  state. Tap for key names. Never values.

## Agent rules

1. Keep harness.md at the project root. It is the one source: read it at the start of every session.
2. Run every step that isn't a STOP. At a STOP, write the one thing the person does, and keep working on anything unblocked.
3. Report as the step: "CRM at mh3.3, next mh3.4." Never "done" without the step.
4. Never skip mh2. A build shipped before design still owes its three docs.
5. Key names only in docs, never values.
6. Every paid service gets a named spend cap the day it's wired.
7. Verify in the running app, not from a passing build.
8. Long jobs skip bad records into a log, stop after 3 identical failures, keep a running total.
9. At mh4.4, propose rule changes as a diff. The builder approves.
10. When a step finishes, move the build and update harness.md in the same pass.
11. Every client gets a Build Hub, made at mh1.4, shared with the client's owner.
12. Run locally with bypass permissions. Bypass never overrides a STOP or a gate.
13. When a new model ships, run the model update pass below before the next build.

## New model, new pass

When a new model ships, run one pass the same day:

1. **Read**: the new model's release notes, specs and prompting guidance from the source.
2. **Diff**: every place this play, skills, agent files and CLAUDE.md conflict with the new guidance.
3. **Patch**: rewrite to fit.
4. **Test**: rerun the Audit on one live build with the new model. Compare against the last audit.
5. **STOP builder**: approves the patch, same as mh4.4.

The patch lands in Part 1. The pass gets a line in Part 3.

## Shorthand

- mh1 to mh4: a mini harness. mh2.3 is mini 2, step 3.
- SH: the super harness, all four in the ring.
- mhNgo: run that mini to its end, no check ins. mh3go means take it live.
- P1 to P4: the Build Hub pillars.
- Three docs: canvas, prototype, live vs design.
- STOP: a step that is genuinely a person's.

---

# Part 2: Status

Client: Artificium Struere. Owner: Kev (owner, builder and only user, so Kev
answers every STOP in both roles).
Build Hub: `hub/build-hub.html`, published privately at https://claude.ai/artifact/6Bciomnfpr1QxqstS89fN7

`build | step | waits on | last updated`

JARVIS | mh1.3 (code already at mh3.2: PR #1 open, held) | Kev: set price + monthly running cost (mh1.3 STOP), then sign scope.md (mh1.4 STOP) | Nov 9

### Placement evidence (Nov 9)

- Furthest step reached: **mh3.2**. Branch `claude/jarvis-windows-voice-assistant-j3xj57`,
  PR #1 open against `main` (mergeable, no CI checks, 1,003 lines added). `main`
  holds only the initial README. Not merged and never run on the target Windows
  machine, so there is no mh3.3 or mh3.4.
- Owed earlier steps:
  - mh1: no scope, price or signature existed. mh1.1 and mh1.2 run Nov 9 → `scope.md`.
    mh1.3 and mh1.4 are open STOPs.
  - mh2: all three docs owed (canvas, prototype, live vs design). No design work exists.
- PR #1 is held at mh3.2 until mh1.4 is signed and mh2.4 is frozen (rule 4, "no code
  before contract"). It is not closed: the code is kept and is checked against the
  frozen design when mh3 resumes.

### Open STOPs: the one thing the person does

- **mh1.3 (Kev, as builder)**: write the price and the monthly running cost into
  `scope.md` → Proposal. The draft running cost is $0 plus the Claude Code plan you
  already pay for.
- **mh1.4 (Kev, as client)**: sign `scope.md` → Contract (name and date).

---

# Part 3: Model log

`model | date | what changed`

No new model passes have run yet. Apply ran Nov 9, 2026, and copied in the play
unchanged.
