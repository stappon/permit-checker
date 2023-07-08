import datetime as dt

from permit_checker.clients.inyo_client import InyoNationalForestClient
from permit_checker.types import AvailableDay, DesiredPermit
from tests.helpers.stub_web_service import StubWebService


def single_case_test_helper(date, division, walkup, remaining, desired):
    stub_service = StubWebService(
        july = {
                date: {
                    division: { 'total': 58, 'remaining': remaining, 'is_walkup': walkup },
                },
            },
        august = {}
    )
    client = InyoNationalForestClient(stub_service)
    return client.get_availability(desired)

def test_inyo_client_simple_match():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=2
    )
    permits = single_case_test_helper('2023-07-21', '406', False, 2, desired)
    assert permits == set([AvailableDay("12345", "406", dt.datetime(2023, 7, 21), 2)])

def test_inyo_client_wrong_date():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=2
    )
    permits = single_case_test_helper('2023-07-23', '406', False, 2, desired)
    assert permits == set()

def test_inyo_client_too_few_spots():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=3
    )
    permits = single_case_test_helper('2023-07-21', '406', False, 2, desired)
    assert permits == set()

def test_inyo_client_skip_walkups():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=2
    )
    permits = single_case_test_helper('2023-07-21', '406', True, 2, desired)
    assert permits == set()

def test_inyo_client_extra_available():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=2
    )
    permits = single_case_test_helper('2023-07-21', '406', False, 3, desired)
    assert permits == set([AvailableDay("12345", "406", dt.datetime(2023, 7, 21), 3)])

def test_inyo_client_multiple_dates_multiple_months():
    service = StubWebService(
        july = {
                '2023-07-01': {
                    '406': { 'total': 58, 'remaining': 3, 'is_walkup': False },
                },
                '2023-07-02': {
                    '406': { 'total': 58, 'remaining': 3, 'is_walkup': False },
                },
            },
        august = {
                '2023-08-05': {
                    '406': { 'total': 58, 'remaining': 3, 'is_walkup': False },
                }
            }
    )
    client = InyoNationalForestClient(service)

    permits = client.get_availability(
        DesiredPermit(
            permit_id="12345",
            dates=[dt.datetime(2023, 7, 1), dt.datetime(2023, 8, 5)],
            divisions=["406"],
            min_people=2
        )
    )
    assert permits == set([
        AvailableDay("12345", "406", dt.datetime(2023, 7, 1), 3),
        AvailableDay("12345", "406", dt.datetime(2023, 8, 5), 3)
    ])

def test_inyo_client_multiple_divisions():
    service = StubWebService(
        july = {
                '2023-07-01': {
                    '406': { 'total': 58, 'remaining': 3, 'is_walkup': False },
                },
                '2023-07-02': {
                    '407': { 'total': 58, 'remaining': 3, 'is_walkup': False },
                },
            },
        august = {
                '2023-08-05': {
                    '408': { 'total': 58, 'remaining': 3, 'is_walkup': False },
                }
            }
    )

    client = InyoNationalForestClient(service)

    permits = client.get_availability(
        DesiredPermit(
            permit_id="12345",
            dates=[dt.datetime(2023, 7, 1), dt.datetime(2023, 7, 2), dt.datetime(2023, 8, 5)],
            divisions=["406", "408"],
            min_people=2
        )
    )
    assert permits == set([
        AvailableDay("12345", "406", dt.datetime(2023, 7, 1), 3),
        AvailableDay("12345", "408", dt.datetime(2023, 8, 5), 3)
    ])

