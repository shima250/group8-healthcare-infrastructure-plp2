from db import Database
from models import User, CycleTracker, HealthTips
from validation import InputValidator

MENU_TEXT = """
==================================================
              SafeCycle - Main Menu
==================================================
  1. Log a new period start date
  2. View predicted next period
  3. View cycle history
  4. Update a logged entry
  5. Delete a logged entry
  6. View a health tip
  7. Exit
==================================================
"""


def show_welcome():
    print("=" * 50)
    print("  Welcome to SafeCycle")
    print("  Track your cycle. Know what's coming. Stay informed.")
    print("=" * 50)


def register_flow(db):
    print("\nLet's get you set up.")
    name = InputValidator.get_non_empty_string("What is your name? ")
    avg_cycle_length = InputValidator.get_valid_int(
        "What is your average cycle length in days? (e.g. 28): ",
        min_value=15,
        max_value=45,
    )
    user = User.register(db, name, avg_cycle_length)
    print(f"\nThanks, {name}! You're all set up.\n")
    return user

def login_or_register_flow(db):
    users = db.get_all_users()

    if users:
        print("\nExisting users found:")
        for u in users:
            print(f"  {u['id']}. {u['name']} (cycle: {u['avg_cycle_length']} days)")
        print(f"  {len(users) + 1}. Register as new user")

        choice = InputValidator.get_valid_int(
            "Choose a user number: ",
            min_value=1, max_value=len(users) + 1
        )

        if choice <= len(users):
            selected = users[choice - 1]
            user = User.load(db, selected['id'])
            print(f"\nWelcome back, {user.name}!\n")
            return user

    return register_flow(db)


def handle_log_period(tracker):
    print("\n-- Log a New Period --")
    start_date = InputValidator.get_valid_date("Enter the date (YYYY-MM-DD): ")
    tracker.log_period(start_date)
    print("Logged successfully.\n")


def handle_view_prediction(tracker):
    print("\n-- Predicted Next Period --")
    result = tracker.predict_next_period()
    if result is None:
        print("No history logged yet. Log a period first (option 1).\n")
        return
    print(f"Next expected period: {result['next_period']}")
    print(
        f"Estimated fertile window: {result['fertile_window_start']} "
        f"to {result['fertile_window_end']}\n"
    )


def handle_view_history(tracker):
    print("\n-- Cycle History --")
    entries = tracker.view_history()
    if not entries:
        print("No history logged yet.\n")
        return

    for e in entries:
        cycle_info = (
            f"{e['cycle_length_since_previous']} days since previous"
            if e["cycle_length_since_previous"] is not None
            else "first logged entry"
        )
        print(f"  [Entry #{e['id']}] {e['start_date']}  ({cycle_info})")
    print()


def handle_update_entry(tracker):
    print("\n-- Update a Logged Entry --")
    entry_id = InputValidator.get_valid_int(
        "Enter the Entry # you want to update: "
    )
    new_date = InputValidator.get_valid_date(
        "Enter the corrected date (YYYY-MM-DD): "
    )
    success = tracker.update_period(entry_id, new_date)
    print(
        "Entry updated successfully.\n"
        if success
        else "No entry found with that number.\n"
    )


def handle_delete_entry(tracker):
    print("\n-- Delete a Logged Entry --")
    entry_id = InputValidator.get_valid_int(
        "Enter the Entry # you want to delete: "
    )
    success = tracker.delete_period(entry_id)
    print(
        "Entry deleted successfully.\n"
        if success
        else "No entry found with that number.\n"
    )


def handle_health_tip(tips):
    print("\n-- Health Tip --")
    print(tips.next_tip())
    print()


def main():
    db = Database("safecycle.db")
    show_welcome()
    user = login_or_register_flow(db)
    tracker = CycleTracker(db, user)
    tips = HealthTips()

    valid_choices = {"1", "2", "3", "4", "5", "6", "7"}

    while True:
        print(MENU_TEXT)
        choice = InputValidator.get_valid_menu_choice(
            "Choose an option (1-7): ",
            valid_choices,
        )

        if choice == "1":
            handle_log_period(tracker)
        elif choice == "2":
            handle_view_prediction(tracker)
        elif choice == "3":
            handle_view_history(tracker)
        elif choice == "4":
            handle_update_entry(tracker)
        elif choice == "5":
            handle_delete_entry(tracker)
        elif choice == "6":
            handle_health_tip(tips)
        elif choice == "7":
            print("\nThanks for using SafeCycle. Take care!\n")
            db.close()
            break


if __name__ == "__main__":
    main()
