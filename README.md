# SafeCycle

A terminal-based Python app for period tracking and health education, built for rural adolescent girls as part of ALU's GCGO framework project.

## Table of Contents
- [Overview](#overview)
- [Team & Contributions](#team--contributions)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Database Configuration](#database-configuration)
- [Running the App](#running-the-app)
- [Testing Notes](#testing-notes)
- [Known Issues / Future Work](#known-issues--future-work)

## Overview

SafeCycle lets a user register, log period entries, view predictions (next period + fertile window) and history, correct or delete entries, and get basic health tips — all through a terminal menu.

<!-- TODO: 2-3 sentence description of the problem this solves and who it's for -->

## Team & Contributions

| Name | Role | Files Owned | Contribution |
|---|---|---|---|
| Ebenezer Kabare Shima | Database | `db.py` (or `db_mysql.py`) | Schema, connection logic, CRUD-supporting functions (`create_user`, `add_period_entry`, `get_history`, etc.)  sole owner of all direct database access |
| Digne Gahamanyi Sugira | Architecture & Integration Lead | `main.py` | File/class structure, menu loop, wiring to `db.py` functions |
| Grace Mukire | Feature Logic Lead (Create/Read) | `features.py` (top half) | `register_user`, `log_period`, `predict_next_period`, `view_history`, `next_health_tip` |
| Job Lamek Odhiambo Ayuko | Feature Logic Lead (Update/Delete) & Validation | `features.py` (bottom half), `validation.py` | `update_period`, `delete_period`, `update_cycle_length`, input validation and error handling across all menu options |
| Sandra Jepkosgei | Testing, Documentation & Presentation Lead | `README.md` | Full app-journey walkthrough (15 min), QA question list, this README, confirming merges to `main` |

<!-- TODO: link each name to their GitHub handle if the repo requires it -->

## Project Structure

```
safecycle/
├── main.py          # Menu loop, wiring, overall architecture
├── db.py            # All database access (schema, connection, CRUD)
├── features.py       # Create/Read (top) + Update/Delete (bottom) logic
├── validation.py     # Input validation and error handling
├── README.md
└── requirements.txt
```

<!-- TODO: confirm final filenames once merged — e.g. is it db.py or db_mysql.py? -->

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd safecycle
   ```
2. (Recommended) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the database — see [Database Configuration](#database-configuration) below.
5. Run the app:
   ```bash
   python main.py
   ```

## Database Configuration

SafeCycle supports **both MySQL (Aiven) and SQLite**, and picks automatically: on startup, `db.py` tries to connect to MySQL first, and transparently falls back to a local SQLite file if that connection can't be made. You don't need to choose manually — you can check which one is active by calling `get_db_type()`.

### MySQL (Aiven) — primary
1. Set the following environment variables (do not hardcode credentials or commit them):
   ```
   SC_MYSQL_HOST=<your-aiven-host>
   SC_MYSQL_PORT=<your-aiven-port>
   SC_MYSQL_USER=<your-username>
   SC_MYSQL_PASSWORD=<your-password>
   SC_MYSQL_DB=<your-database-name>
   ```
2. Requires the `mysql-connector` package (falls back automatically if it isn't installed).
3. <!-- TODO: confirm with Shima whether SSL needs to be configured explicitly for the Aiven connection, or whether it's handled by the connector's defaults. -->

### SQLite — automatic fallback
1. No setup needed. If MySQL isn't reachable (missing package, bad credentials, network issue), the app creates/uses a local file automatically  default path `safecycle.db`, configurable via the `SC_SQLITE_PATH` environment variable.
2. To reset local data, delete the SQLite file and rerun the app.

### Initializing the schema
Run `python db.py` directly to create tables and self-test the full CRUD flow (create a user, log entries, read history, update, delete)  this is a good first step to confirm everything is wired up correctly before running `main.py`.

### Why this database was chosen
MySQL (Aiven) was the primary target for cloud persistence and shared team access. Rather than making a one-time manual decision, `db.py` was designed to try Aiven first and fall back to SQLite automatically if the connection isn't available — so the app is never blocked by a database outage, and the rest of the codebase (`main.py`, `features.py`) never needs to change based on which backend ends up active.

## Running the App

Once set up, `python main.py` launches the menu:

```
1. Register user
2. Log a new period
3. View next period / fertile window prediction
4. View history
5. Update a logged entry
6. Delete a logged entry
7. Get a health tip
8. Exit
```

<!-- TODO: confirm actual menu text/numbering matches Digne's main.py -->

## Testing Notes

- Full app-journey walkthrough tested end-to-end, timed at **~15 minutes** (register → log → predict → view history → update → delete → exit).
- Test environment: <!-- TODO: OS, Python version -->
- Known edge cases tested: <!-- TODO: e.g. invalid dates, duplicate users, empty history -->
- QA question list (with exact file/function references) prepared separately for presentation — see `<link or filename>`.

## Known Issues / Future Work

<!-- TODO: list anything not finished by submission -->



