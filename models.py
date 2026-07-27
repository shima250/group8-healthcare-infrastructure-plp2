import itertools
from datetime import datetime, timedelta


class User:

    def __init__(self, db, user_id, name, avg_cycle_length):
        self.db = db
        self.id = user_id
        self.name = name
        self.avg_cycle_length = avg_cycle_length

    @classmethod
    def register(cls, db, name, avg_cycle_length):
        user_id = db.insert_user(name, avg_cycle_length)
        return cls(db, user_id, name, avg_cycle_length)

    @classmethod
    def load(cls, db, user_id):
        row = db.get_user_row(user_id)
        if row is None:
            return None
        return cls(db, row["id"], row["name"], row["avg_cycle_length"])

    def update_cycle_length(self, new_avg_cycle_length):
        success = self.db.update_user_row(self.id, new_avg_cycle_length)
        if success:
            self.avg_cycle_length = new_avg_cycle_length
        return success

    def __repr__(self):
        return f"User(id={self.id}, name={self.name!r}, avg_cycle_length={self.avg_cycle_length})"


class CycleTracker:

    def __init__(self, db, user: User):
        self.db = db
        self.user = user

    def log_period(self, start_date):
        return self.db.insert_period(self.user.id, start_date)

    def predict_next_period(self):
        latest = self.db.get_latest_period_row(self.user.id)
        if latest is None:
            return None

        last_start = datetime.strptime(latest["start_date"], "%Y-%m-%d")
        cycle_length = self.user.avg_cycle_length

        next_period = last_start + timedelta(days=cycle_length)
        ovulation = next_period - timedelta(days=14)
        fertile_start = ovulation - timedelta(days=5)
        fertile_end = ovulation + timedelta(days=1)

        return {
            "next_period": next_period.strftime("%Y-%m-%d"),
            "fertile_window_start": fertile_start.strftime("%Y-%m-%d"),
            "fertile_window_end": fertile_end.strftime("%Y-%m-%d"),
        }

    def view_history(self):
        entries = self.db.get_history_rows(self.user.id)
        annotated = []
        previous_date = None

        for entry in entries:
            current_date = datetime.strptime(entry["start_date"], "%Y-%m-%d")
            cycle_length = None

            if previous_date is not None:
                cycle_length = (current_date - previous_date).days

            annotated.append({
                "id": entry["id"],
                "start_date": entry["start_date"],
                "cycle_length_since_previous": cycle_length,
            })

            previous_date = current_date

        return annotated

    def update_period(self, entry_id, new_start_date):
        return self.db.update_period_row(entry_id, new_start_date)

    def delete_period(self, entry_id):
        return self.db.delete_period_row(entry_id)


class HealthTips:

    TIPS = [
        "Menstrual health means having access to accurate information, safe materials, and the ability to manage your period with dignity and without shame.",
        "Changing pads, tampons, or cups regularly (roughly every 4-8 hours) helps prevent infection and discomfort.",
        "It's normal for cycle length to vary by a few days from month to month - tracking over several cycles gives a more reliable average than any single cycle.",
        "Period poverty (lack of access to menstrual products or facilities) is a real barrier to school attendance for many girls worldwide - you're not alone if this has affected you.",
        "Cramps, mood changes, and fatigue around your period are common. Severe or unusual pain is worth mentioning to a trusted adult or health worker.",
    ]

    def __init__(self):
        self._cycle = itertools.cycle(self.TIPS)

    def next_tip(self):
        return next(self._cycle)