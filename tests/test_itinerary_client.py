import datetime as dt
from permit_checker.clients.itinerary_client import PermitItineraryApiClient
from permit_checker.types import AvailableDay, DesiredPermit
from tests.helpers.stub_web_service import StubWebService

def make_submap(date, walkup, hidden, remaining):
    return {
        date: {
        'is_hidden': hidden,
        'remaining': remaining,
        'season_type': 'High',
        'show_walkup': walkup,
        'total': remaining}
    }


def single_case_test_helper(date, walkup, hidden, remaining, desired, group_remaining=True):
    member_submap = make_submap(date, walkup, hidden, remaining)
    constant_submap = make_submap(date, walkup, hidden, 1 if group_remaining else 0)
    service = StubWebService(
        july = {
            'quota_type_maps': {
                'QuotaUsageByMemberDaily': member_submap,
                'ConstantQuotaUsageDaily': constant_submap
            }
        }
    )
    client = PermitItineraryApiClient(service)
    return client.get_availability(desired)

def test_itinerary_simple_match():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=2
    )
    permits = single_case_test_helper('2023-07-21', False, False, 2, desired)
    assert permits == set([AvailableDay("12345", "406", dt.datetime(2023, 7, 21), 2)])

def test_itinerary_client_wrong_date():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=2
    )
    permits = single_case_test_helper('2023-07-23', False, False, 2, desired)
    assert permits == set()

def test_itinerary_client_too_few_spots():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=3
    )
    permits = single_case_test_helper('2023-07-21', False, False, 2, desired)
    assert permits == set()

def test_itinerary_client_skip_walkups():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=2
    )
    permits = single_case_test_helper('2023-07-21', True, False, 2, desired)
    assert permits == set()

def test_itinerary_client_skip_hidden():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=2
    )
    permits = single_case_test_helper('2023-07-21', False, True, 2, desired)
    assert permits == set()

def test_itinerary_client_extra_available():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=2
    )
    permits = single_case_test_helper('2023-07-21', False, False, 3, desired)
    assert permits == set([AvailableDay("12345", "406", dt.datetime(2023, 7, 21), 3)])

def test_itinerary_client_group_quota_filled():
    desired = DesiredPermit(
        permit_id="12345",
        dates=[dt.datetime(2023, 7, 21)],
        divisions=["406"],
        min_people=2
    )
    permits = single_case_test_helper('2023-07-21', False, True, 2, desired, group_remaining=False)
    assert permits == set()

def test_itinerary_client_multiple_dates_multiple_months():
    service = StubWebService(
        july = {
            'quota_type_maps': {
                'QuotaUsageByMemberDaily': make_submap('2023-07-01', False, False, 15),
                'ConstantQuotaUsageDaily': make_submap('2023-07-01', False, False, 1)
        }},
        august = {
            'quota_type_maps': {
                'QuotaUsageByMemberDaily': make_submap('2023-08-05', False, False, 15),
                'ConstantQuotaUsageDaily': make_submap('2023-08-05', False, False, 1)
        }}
    )
    client = PermitItineraryApiClient(service)

    permits = client.get_availability(
        DesiredPermit(
            permit_id="12345",
            dates=[dt.datetime(2023, 7, 1), dt.datetime(2023, 8, 5)],
            divisions=["406"],
            min_people=2
        )
    )
    assert permits == set([
        AvailableDay("12345", "406", dt.datetime(2023, 7, 1), 15),
        AvailableDay("12345", "406", dt.datetime(2023, 8, 5), 15)
    ])

def test_itinerary_client_multiple_divisions():
    class StubMultiDivisionWebService:
        def __init__(self):
            self._one = {
                'quota_type_maps': {
                    'QuotaUsageByMemberDaily': make_submap('2023-07-01', False, False, 15),
                    'ConstantQuotaUsageDaily': make_submap('2023-07-01', False, False, 1)
            }}
            self._two = {
                'quota_type_maps': {
                    'QuotaUsageByMemberDaily': make_submap('2023-07-05', False, False, 15),
                    'ConstantQuotaUsageDaily': make_submap('2023-07-05', False, False, 1)
            }}

        def get_inyo_county_availability(self, permit_id: str, start_date: dt.datetime, end_date: dt.datetime) -> dict:
            assert False, "Not supported in this stub"

        def get_permit_itinerary_availability(self, permit_id: str, division: str, month: int, year: int) -> dict:
            if division == "1":
                payload = self._one
            if division == "2":
                payload = self._two
            return { "payload": payload }

    client = PermitItineraryApiClient(StubMultiDivisionWebService())

    permits = client.get_availability(
        DesiredPermit(
            permit_id="12345",
            dates=[dt.datetime(2023, 7, 1), dt.datetime(2023, 7, 5)],
            divisions=["1", "2"],
            min_people=2
        )
    )
    assert permits == set([
        AvailableDay("12345", "1", dt.datetime(2023, 7, 1), 15),
        AvailableDay("12345", "2", dt.datetime(2023, 7, 5), 15)
    ])
