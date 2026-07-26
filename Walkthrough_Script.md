# SafeCycle — 15-Minute Walkthrough Script

Sequence of actions for the live demo, timed to fit ~15 minutes with room to talk through the architecture as you go. Fill in the `TODO`s once you've run it against the real app and know actual timings/output.

## Before you start
- [ ] Confirm latest `main` branch is pulled and running
- [ ] Confirm database is configured (MySQL or SQLite — know which, and say so)
- [ ] Have the QA question list open in case something comes up mid-demo
- [ ] Have a stopwatch/timer running

---

## Segment 1 — Intro & Architecture (~2 min)

**Say:**
> "SafeCycle is a terminal app for period tracking and prediction. It's split into four layers so each of us could work independently: `db.py` owns the database, `main.py` runs the menu, `features.py` holds the logic, and `validation.py` checks inputs. I'll walk through a full user journey now."

**Show:** the project file structure (`main.py`, `db.py`, `features.py`, `validation.py`)

---

## Segment 2 — Register a User (~1.5 min)

**Do:** Launch the app (`python main.py`), select "Register"

**Enter:** a sample username/details <!-- TODO: whatever fields register_user actually asks for -->

**Say:**
> "This calls `register_user` in `features.py`, which validates the input through `validation.py`, then calls `create_user` in `db.py` to write it to the database."

**Expect:** confirmation message <!-- TODO: exact wording -->

---

## Segment 3 — Log a Period (~2 min)

**Do:** Select "Log a new period," enter a start date <!-- TODO: and cycle length if asked -->

**Say:**
> "This goes through `log_period`, which validates the date format before calling `add_period_entry` in `db.py`."

**Try one bad input on purpose** (e.g. invalid date) to show validation catching it live — this is a strong demo moment since it proves `validation.py` actually works, not just that the happy path works.

**Expect:** error message, then successful re-entry <!-- TODO: exact behavior -->

---

## Segment 4 — View Prediction (~2 min)

**Do:** Select "View prediction"

**Say:**
> "`predict_next_period` reads the logged history via `get_history`, then calculates the next expected period and fertile window."

**Expect:** predicted date + fertile window range <!-- TODO: confirm what's shown -->

*(Optional: briefly explain the calculation method if you know it — average cycle length from history, etc.)*

---

## Segment 5 — View History (~1.5 min)

**Do:** Select "View history"

**Say:**
> "This just calls `view_history`, which pulls every logged entry through `get_history` and formats it for the terminal."

**Expect:** list of logged entries <!-- TODO: confirm format -->

---

## Segment 6 — Update an Entry (~2 min)

**Do:** Select "Update," correct the date or cycle length you entered earlier

**Say:**
> "`update_period` (or `update_cycle_length`) validates the new value, then calls into `db.py` to update the record — no raw SQL outside `db.py`."

**Expect:** confirmation, and prediction changes accordingly if you re-check it <!-- TODO: verify this actually updates the prediction live -->

---

## Segment 7 — Delete an Entry (~1.5 min)

**Do:** Select "Delete," remove the entry you just logged

**Say:**
> "This calls `delete_period`. If you try to delete something that doesn't exist, validation should catch that too." <!-- TODO: demo this if there's time -->

**Expect:** confirmation, entry gone from history

---

## Segment 8 — Health Tip & Exit (~1 min)

**Do:** Select "Health tip," then "Exit"

**Say:**
> "`next_health_tip` gives a short piece of educational content — this ties back to the project's real-world goal of health literacy, not just tracking."

---

## Segment 9 — Wrap-up (~1.5 min)

**Say:**
> "That's the full journey — create, read, update, delete, all going through the same layered structure. The database layer is swappable: we tested Aiven MySQL first, and had SQLite ready as a fallback, and neither `main.py` nor `features.py` had to change either way."

**Invite questions** — hand off to whoever owns the relevant file if something specific comes up (use the QA list's file/owner mapping).

---

## Timing checklist
| Segment | Target | Actual (fill in after a practice run) |
|---|---|---|
| Intro | 2 min | |
| Register | 1.5 min | |
| Log period | 2 min | |
| Prediction | 2 min | |
| History | 1.5 min | |
| Update | 2 min | |
| Delete | 1.5 min | |
| Health tip + exit | 1 min | |
| Wrap-up | 1.5 min | |
| **Total** | **~15 min** | |

**Do at least one full timed practice run before presenting** — adjust segment lengths based on where you actually run long.
