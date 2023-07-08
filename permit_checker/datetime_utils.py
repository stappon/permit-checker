import datetime as dt
from typing import List, Tuple


def all_days_between_dates(start_date, end_date):
    return [start_date + dt.timedelta(days=x) for x in range((end_date-start_date).days + 1)]


def datetime_to_datestring(datetime: dt.datetime):
    return datetime.strftime('%Y-%m-%d')


def tuples_to_datetimes(tuples: List[Tuple[int, int, int]]):
    return [dt.datetime(*t) for t in tuples]


def month_starts_and_ends(desired_dates):

    def _start_of_month(date, month_offset=0):
        return dt.datetime(date.year, (date.month + month_offset) % 12, 1)

    start_of_months = set([_start_of_month(d) for d in desired_dates])
    return [(s, _start_of_month(s, month_offset=1) - dt.timedelta(1)) for s in start_of_months]
