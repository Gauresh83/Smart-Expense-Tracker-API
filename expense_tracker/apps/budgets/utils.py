from datetime import date
import calendar


def get_period_dates(period: str):
    """Return (start_date, end_date) for the current period."""
    today = date.today()

    if period == "weekly":
        # ISO week: Monday to Sunday
        start = today - __import__("datetime").timedelta(days=today.weekday())
        end = start + __import__("datetime").timedelta(days=6)
        return start, end

    elif period == "monthly":
        start = today.replace(day=1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        end = today.replace(day=last_day)
        return start, end

    elif period == "yearly":
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)
        return start, end

    return today, today
