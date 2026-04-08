import calendar
from datetime import date

def get_dates_for_month(year: int, month: int) -> list[date]:
    """Return a list of all dates in the given month and year."""
    num_days = calendar.monthrange(year, month)[1]
    return [date(year, month, day) for day in range(1, num_days + 1)]

# get_dates_for_month(2026, 3)
# [date(2026,3,1), date(2026,3,2), ..., date(2026,3,31)]