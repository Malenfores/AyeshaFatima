# 🕵️ Murder Mystery Detective — Advanced Edition (Python / Tkinter)

## What's in this folder

```
detective_game.py       <- RUN THIS FILE to play
cases_data.py             <- all 14 cases (story, suspects, clues, solutions, alibi statements)
generate_assets.py        <- optional: regenerates every image & sound (needs Pillow)
assets/
    images/                 <- 14 case backgrounds + title/menu/result art + suspect portraits
    sounds/                 <- SFX + music tracks + horror jump-scare stinger
.vscode/launch.json       <- lets VS Code run the game with one click (F5)
detective_profile.json    <- created on first launch - your detective ID, XP, play time
detective_save.json       <- created when you save an in-progress game
player_records.json       <- created automatically - overall leaderboard
case_records.json         <- created automatically - every accusation you've ever made
evidence_log.json         <- created automatically - every clue you've ever found
achievements.json         <- created automatically - unlocked achievements
settings.json             <- created automatically - difficulty + volume preferences
```

## ▶️ How to run it (VS Code or terminal)

1. Open this folder in VS Code, make sure a Python 3 interpreter is selected,
   open `detective_game.py`, and press **Run ▶** / `F5`.
2. Or from a terminal: `python detective_game.py`

No `pip install` is required to play. **Linux only**, if Tkinter is missing:
`sudo apt-get install python3-tk`.

## ✨ Full feature list

**Restart Game (full data wipe)** — a red "🔄 RESTART GAME" button on the
title screen lets you erase everything and start completely fresh: your
detective profile, saved game, player records, case history, achievements,
evidence locker, and settings are all permanently deleted. It asks for
confirmation first ("YES, ERASE EVERYTHING" / "CANCEL") since this cannot
be undone, then takes you straight back through detective registration.

**Complete investigation flow, no dead ends** — every case runs the full loop:
pick a case → read the briefing → investigate the scene for clues → interrogate
suspects → the Accuse button unlocks once you've done enough → make your
accusation → get a full case report and verdict → move to the next case.

**Accuse button is gated** — it stays locked (and visibly shows what's still
needed) until you've collected enough clues for your difficulty level (and,
on Hard, interrogated every suspect too). Trying to accuse early explains
exactly what's missing instead of silently failing.

**Detective Profile with XP, Level & Rank** — created on first launch (name,
agency, badge number, chosen difficulty). Every case you solve earns XP;
your level and rank (Trainee → Legend Detective) are derived automatically
from total XP and shown on your ID card and in Statistics.

**Player Statistics screen** — cases attempted/solved/failed, accuracy %,
total play time (tracked across every session), current level/rank/XP, and
your active difficulty.

**Case History screen** — every one of the 14 cases shown as Solved, Failed
(with a retry available), or not yet attempted.

**Professional Case Report** — after every accusation you get a report with
your letter grade (S/A/B/C/D/F), XP earned, time taken, evidence collected,
and suspects interrogated, alongside the full explanation of who did it and
why.

**Detective Notebook** — automatically logs every clue you find during an
investigation, always visible on the investigation screen.

**Evidence Locker** — every clue you've ever discovered, across every
session, browsable by case from the title screen.

**Suspect Database** — a spoiler-free reference: browse every suspect's
background and alibi for any case without it counting as an accusation or
revealing who the killer is.

**Save/Load system** — manual Save button, a "Continue Saved Case" option
from the title screen, and **auto-save** after every clue you find, every
interrogation, and every accusation, so you're never far from your last
checkpoint.

**Achievements & rank progression** — a working achievement system (First
Blood, Flawless Detective, Quick Draw, Evidence Hound, Master Interrogator,
Living Legend, and more), unlocked live and shown on the Case Report the
moment you earn them, plus the 8-tier rank ladder from Trainee to Legend
Detective.

**Difficulty modes** — Easy / Medium / Hard, chosen at registration or
changed anytime in Settings. Difficulty controls how much of a case you must
investigate before Accuse unlocks, and multiplies the XP you earn.

**Music for every mood** — a mellow theme for all menu screens, a moodier
looping "murder mystery" ambient track (drone + heartbeat + distant clock)
during case briefings and investigation, a triumphant victory theme, and a
somber game-over theme, plus an occasional **horror jump-scare stinger**
(with a screen flash) while investigating, for genuine tension.

**Sound effects** for button clicks, clue discovery, evidence, a door
opening as you enter a case, footsteps as you begin investigating,
interrogation chimes, success/failure stings, and save notifications.

**Volume controls in Settings** — separate Music and Sound Effects sliders.
These fully apply with the optional `pygame` package installed; without it,
the game still plays music and effects through your OS's built-in sound
tools, just without live volume attenuation (noted in the Settings screen).

**Animations** — flickering candlelight title text, occasional lightning
flashes, a horror jump-scare flash while investigating, and a subtle scene
transition wipe between major screens.

  - Best audio experience: `pip install pygame` (optional) — plays music
    and effects together, with working volume sliders, on every OS.
  - Without pygame: Windows still loops background music via the built-in
    `winsound` module; macOS/Linux use whatever system player is available
    (`afplay` / `paplay` / `aplay` / `ffplay`).

## 🎨 Regenerating the artwork / sound (optional)

```bash
pip install pillow
python generate_assets.py
```
This overwrites everything in `assets/images/` and `assets/sounds/`.

## 🏆 Ranks

| Score (out of 14) | Rank |
|---|---|
| 14 | Legend Detective |
| 12–13 | Chief Inspector |
| 10–11 | Inspector |
| 8–9 | Senior Detective |
| 6–7 | Detective |
| 4–5 | Junior Detective |
| 2–3 | Officer |
| 0–1 | Trainee |

Good luck, Detective — the truth is always hiding in the details. 🔍
