# SafeCycle — QA Question List

Prepared for presentation Q&A. Organized by module/owner so whoever gets asked can jump straight to the relevant file/function. Answers marked `TODO` need filling in with the actual implementation details before presenting.

## Database — db.py (Ebenezer Kabare Shima)

1. **Why MySQL (Aiven) or SQLite?**
   Q: Which database did you end up using, and why?
   A: Both are supported — the app decides automatically at runtime. `get_connection()` tries MySQL (Aiven) first; if that connection fails for any reason, it transparently falls back to SQLite. This means the app is never blocked by a database outage, and neither `main.py` nor `features.py` needs to know or care which one is active.

2. **Q: How does `db.py` handle the connection — where's that logic?**
   A: `get_connection()` is the single entry point. It checks if an existing connection is still alive via `_connection_alive()`; if not, it calls `_connect_mysql()` first, and falls back to `_connect_sqlite()` only if that returns `None`. `get_db_type()` reports which backend ended up active ("mysql" or "sqlite").

3. **Q: Is the connection secured (SSL)? How did you verify it?**
   A: MySQL credentials (host, port, user, password, database) are read from environment variables (`SC_MYSQL_HOST`, `SC_MYSQL_PORT`, `SC_MYSQL_USER`, `SC_MYSQL_PASSWORD`, `SC_MYSQL_DB`) rather than hardcoded, with the Aiven host/port as defaults. <!-- TODO: worth double-checking with Shima — the current `MYSQL_CONFIG` dict doesn't explicitly set an SSL/CA parameter for mysql-connector, so confirm whether Aiven's connection is enforcing SSL by default or whether that needs to be added explicitly. -->

4. **Q: Walk us through the schema — what tables and fields exist?**
   A: Two tables. `users`: `id` (PK, auto-increment), `name`, `avg_cycle_length` (defaults to 28). `cycle_history`: `id` (PK, auto-increment), `user_id` (foreign key to `users`, cascades on delete), `start_date`. Note that cycle length is stored per-*user* (an average), not per individual entry.

5. **Q: What happens if the database connection fails when the app starts?**
   A: If MySQL is unreachable, `get_connection()` silently falls back to SQLite (a local file, default `safecycle.db`) — there's no error shown to the user in that case, since the fallback is transparent by design.

6. **Q: What do `create_user`, `add_period_entry`, and `get_history` each do, and what do they return?**
   A: `create_user(name, avg_cycle_length=28)` inserts a new user row and returns the new user's id. `add_period_entry(user_id, start_date)` inserts a new period entry and returns the new entry's id. `get_history(user_id)` returns a list of all that user's period entries (each a dict with `id`, `user_id`, `start_date`), ordered newest first. There's also `get_user`, `get_latest_entry`, `update_user_cycle_length`, `update_period_entry`, and `delete_period_entry` covering the rest of CRUD.

7. **Q: Why does only `db.py` touch the database directly — what's the benefit?**
   A: Keeps SQL logic in one place; every other file calls these functions instead of writing raw SQL, so the same `features.py`/`main.py` code works unchanged whether the backend is MySQL or SQLite.

## Architecture — main.py (Digne Gahamanyi Sugira)

8. **Q: Walk us through the file/class structure — why split it this way?**
   A: <!-- TODO -->

9. **Q: How does the menu loop in `main.py` call into `features.py`? Show us one example.**
   A: <!-- TODO: e.g. option 2 → calls `features.log_period(...)` -->

10. **Q: If we swapped Shima's `db.py` for a different database entirely, what would break?**
    A: <!-- TODO: ideally "nothing in main.py or features.py, as long as function names/signatures match" -->

11. **Q: How are errors from lower layers (db.py, features.py) surfaced to the user in the menu?**
    A: <!-- TODO -->

## Create/Read logic — features.py, top half (Grace Mukire)

12. **Q: How does `register_user` work — what does it validate before calling the database?**
    A: <!-- TODO -->

13. **Q: Walk us through `predict_next_period` — what's the prediction logic?**
    A: <!-- TODO: e.g. average cycle length from history + last logged date -->

14. **Q: How is the fertile window calculated?**
    A: <!-- TODO -->

15. **Q: Does `predict_next_period` call any raw SQL, or only Shima's functions?**
    A: Only calls functions from `db.py` (e.g. `get_history`) — no raw SQL in `features.py`.

16. **Q: What does `view_history` display, and how is it formatted for the terminal?**
    A: <!-- TODO -->

17. **Q: What does `next_health_tip` do — is the content static or does it depend on the user's data?**
    A: <!-- TODO -->

## Update/Delete logic & validation — features.py bottom half + validation.py (Job Lamek Odhiambo Ayuko)

18. **Q: Walk us through `update_period` — what can be corrected, and how does it find the right record?**
    A: <!-- TODO: e.g. by entry ID -->

19. **Q: What does `delete_period` do if the entry doesn't exist?**
    A: <!-- TODO -->

20. **Q: What does `update_cycle_length` affect downstream — does it change future predictions immediately?**
    A: <!-- TODO -->

21. **Q: What's validated in `validation.py`, and which menu options use it?**
    A: `validation.py` defines an `InputValidator` class with four static methods: `get_valid_date` (enforces `YYYY-MM-DD` format via `datetime.strptime`, re-prompting on failure), `get_valid_int` (enforces whole numbers within an optional min/max range — e.g. the registration flow uses this to require a cycle length between 15 and 45 days), `get_valid_menu_choice` (only accepts a value from a given set of valid menu options), and `get_non_empty_string` (rejects blank input, e.g. for name entry). Every menu prompt in `main.py` — registration, logging, updating, deleting, and menu navigation — goes through one of these four methods.

22. **Q: What happens if a user enters an invalid date or a negative cycle length?**
    A: The prompt re-asks in a loop rather than crashing or exiting. For an invalid date, it prints "! That doesn't look like a valid date. Please use YYYY-MM-DD (e.g. 2026-07-25)." For an out-of-range cycle length, it prints a message naming the actual min/max allowed (e.g. "Please enter a number of at least 15."). The user just keeps getting reprompted until valid input is given.

## Testing & general (Sandra Jepkosgei)

23. **Q: Walk us through a full app journey — what did you test, start to finish?**
    A: Register → log a period → view prediction → view history → update an entry → delete an entry → exit. Timed at ~15 minutes.

24. **Q: What edge cases did you test?**
    A: <!-- TODO: e.g. empty history predicting, duplicate usernames, deleting a non-existent entry -->

25. **Q: Is everything merged into `main`? Any open branches or conflicts?**
    A: <!-- TODO: confirm before presenting -->

26. **Q: If the database were down during the demo, what would happen?**
    A: <!-- TODO: depends on Shima's error handling — coordinate this answer with him -->

---

**Before presenting:** confirm every `TODO` above with the relevant teammate — these are the questions most likely to expose gaps between what's *claimed* in the README and what's actually in the code.
