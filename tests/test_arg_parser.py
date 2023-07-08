import datetime as dt
from permit_checker.arg_parser import parse_arguments
from permit_checker.types import Configuration, DesiredPermit


def test_basic_args():
    config = parse_arguments([
        '--id', '123',
        '--divisions', '4', '5',
        '--earliest', '2023-01-01',
        '--latest', '2023-01-02',
        '--people', '2',
        '--secs', '45',
        '--test'
    ])

    assert config == Configuration(
        DesiredPermit(
            permit_id='123',
            divisions=['4', '5'],
            dates=[dt.date(2023, 1, 1), dt.date(2023, 1, 2)],
            min_people=2
        ),
        test_mode=True,
        poll_time_secs=45
    )


def test_no_latest():
    config = parse_arguments([
        '--id', '123',
        '--divisions', '4', '5',
        '--earliest', '2023-01-01',
        '--people', '2',
        '--secs', '45',
        '--test'
    ])

    assert config.desired.dates == [dt.date(2023, 1, 1)]


def test_no_test_flag():
    config = parse_arguments([
        '--id', '123',
        '--divisions', '4', '5',
        '--earliest', '2023-01-01',
        '--people', '2',
        '--secs', '45',
    ])

    assert config.test_mode is False

def test_default_secs_no_test_flag():
    config = parse_arguments([
        '--id', '123',
        '--divisions', '4', '5',
        '--earliest', '2023-01-01',
        '--people', '2'
    ])

    assert config.poll_time_secs == 60

def test_default_secs_test_flag():
    config = parse_arguments([
        '--id', '123',
        '--divisions', '4', '5',
        '--earliest', '2023-01-01',
        '--people', '2',
        '--test'
    ])

    assert config.poll_time_secs == 5
