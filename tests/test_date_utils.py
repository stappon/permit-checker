import datetime as dt
from permit_checker.datetime_utils import all_days_between_dates, datetime_to_datestring, month_starts_and_ends, tuples_to_datetimes

def test_month_starts_and_ends():
    desired_dates = [dt.datetime(*x) for x in [
        (2023, 7, 5),
        (2023, 7, 30),
        (2023, 9, 2)
    ]]
    actual = set(month_starts_and_ends(desired_dates))
    expected = set([
        (dt.datetime(2023, 7, 1), dt.datetime(2023, 7, 31)),
        (dt.datetime(2023, 9, 1), dt.datetime(2023, 9, 30)),
    ])
    assert actual == expected

def test_days_between_dates():
    actual = all_days_between_dates(dt.datetime(2023, 7, 30), dt.datetime(2023, 8, 2))
    expected = tuples_to_datetimes([
        (2023, 7, 30),
        (2023, 7, 31),
        (2023, 8, 1),
        (2023, 8, 2)
    ])
    assert actual == expected, "Wrong days between dates"

def test_datetime_to_datestring():
    actual = datetime_to_datestring(dt.datetime(2023, 7, 1))
    expected = "2023-07-01"
    assert actual == expected, "Wrong datestring {}".format(actual)
