from datetime import datetime


class InputValidator:

    @staticmethod
    def get_valid_date(prompt):
        while True:
            raw = input(prompt).strip()
            try:
                parsed = datetime.strptime(raw, "%Y-%m-%d")
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                print(
                    "  ! That doesn't look like a valid date. Please use YYYY-MM-DD (e.g. 2026-07-25)."
                )

    @staticmethod
    def get_valid_int(prompt, min_value=1, max_value=None):
        while True:
            raw = input(prompt).strip()

            if not raw.lstrip("-").isdigit():
                print("  ! Please enter a whole number.")
                continue

            value = int(raw)

            if value < min_value:
                print(f"  ! Please enter a number of at least {min_value}.")
                continue

            if max_value is not None and value > max_value:
                print(f"  ! Please enter a number no greater than {max_value}.")
                continue

            return value

    @staticmethod
    def get_valid_menu_choice(prompt, valid_choices):
        while True:
            raw = input(prompt).strip()

            if raw in valid_choices:
                return raw

            print(f"  ! Please enter one of: {', '.join(sorted(valid_choices))}.")

    @staticmethod
    def get_non_empty_string(prompt):
        while True:
            raw = input(prompt).strip()

            if raw:
                return raw

            print("  ! This can't be empty. Please try again.")