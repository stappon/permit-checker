from typing import Set
from permit_checker.datetime_utils import datetime_to_datestring, month_starts_and_ends
from permit_checker.protocols import RecreationWebService
from permit_checker.types import AvailableDay, DesiredPermit


class PermitItineraryApiClient:

    def __init__(self, web_service: RecreationWebService):
        self._web_service = web_service

    def get_availability(self, desired: DesiredPermit) -> Set[AvailableDay]:
        available = set()
        years_months = [(start.year, start.month) for start, _ in month_starts_and_ends(desired.dates)]
        for division in desired.divisions:
            member_quota_dict = dict()
            constant_quota_dict = dict()
            for year, month in sorted(years_months):
                payload = self._web_service.get_permit_itinerary_availability(
                    permit_id=desired.permit_id,
                    division=division,
                    month=month,
                    year=year
                )
                quota_maps = payload['payload']['quota_type_maps']
                member_quota_dict.update(quota_maps['QuotaUsageByMemberDaily'])
                constant_quota_dict.update(quota_maps['ConstantQuotaUsageDaily'])
            available.update(self._parse_quota_dict(member_quota_dict, constant_quota_dict, desired, division))

        return available

    @classmethod
    def _parse_quota_dict(
        cls,
        member_quota_dict: dict,
        group_quota_dict: dict,
        desired: DesiredPermit,
        division: str
    ) -> Set[AvailableDay]:
        available: Set[AvailableDay] = set()

        for date in desired.dates:
            datestring = datetime_to_datestring(date)
            try:
                member = member_quota_dict[datestring]
                constant = group_quota_dict[datestring]
            except KeyError:
                continue
            # Confirm assumed invariants
            assert member['show_walkup'] == constant['show_walkup']
            assert member['is_hidden'] == constant['is_hidden']
            remaining = member['remaining'] if constant['remaining'] > 0 else 0
            if (
                remaining >= desired.min_people and
                not member['show_walkup'] and
                not member['is_hidden']
            ):
                available.add(AvailableDay(
                    permit_id=desired.permit_id,
                    division=division,
                    date=date,
                    max_people=remaining
                ))
        return available
