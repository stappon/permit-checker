import argparse
import datetime as dt
from permit_checker.datetime_utils import all_days_between_dates
from permit_checker.types import Configuration, DesiredPermit


def default_poll_time(test_mode: bool) -> int:
    return 5 if test_mode else 60


def parse_arguments(args=None) -> Configuration:
    parser = argparse.ArgumentParser(description='Permit tracker argument parser')

    parser.add_argument('--id', type=str, help='Permit ID')
    parser.add_argument('--divisions', type=str, nargs='+', help='List of division IDs')
    parser.add_argument('--earliest', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--latest', type=str, nargs='?', help='End date (YYYY-MM-DD)')
    parser.add_argument('--people', type=int, help='Minimum number of people')
    parser.add_argument('--test', action='store_true', help='Whether to skip sending emails', default=False)
    parser.add_argument('--secs', type=int, nargs='?', help="How often to poll, in seconds")
    args = parser.parse_args(args)

    earliest_date = dt.datetime.strptime(args.earliest, '%Y-%m-%d').date()
    latest_date = dt.datetime.strptime(args.latest, '%Y-%m-%d').date() if args.latest else earliest_date
    return Configuration(
        desired=DesiredPermit(
            permit_id=args.id,
            divisions=args.divisions,
            dates=all_days_between_dates(earliest_date, latest_date),
            min_people=args.people,
        ),
        test_mode=args.test,
        poll_time_secs=args.secs if args.secs else default_poll_time(args.test)
    )
