import itertools
from typing import Set

from permit_checker.datetime_utils import datetime_to_datestring, month_starts_and_ends
from permit_checker.protocols import RecreationWebService
from permit_checker.types import AvailableDay, DesiredPermit


class InyoNationalForestClient:

    def __init__(self, web_service: RecreationWebService):
        self._web_service = web_service

    def get_availability(self, desired: DesiredPermit) -> Set[AvailableDay]:
        payload = dict()
        for (s, e) in set(month_starts_and_ends(desired.dates)):
            new_payload = self._web_service.get_inyo_county_availability(desired.permit_id, s, e)["payload"]
            payload.update(new_payload)

        return self._parse_payload(payload, desired)

    @staticmethod
    def _parse_payload(data: dict, desired: DesiredPermit) -> Set[AvailableDay]:
        available: Set[AvailableDay] = set()

        for date, division in itertools.product(desired.dates, desired.divisions):
            datestring = datetime_to_datestring(date)
            try:
                details = data[datestring][division]
            except KeyError:
                continue
            remaining = details['remaining']
            if remaining >= desired.min_people and not details['is_walkup']:
                available.add(AvailableDay(
                    permit_id=desired.permit_id,
                    division=division,
                    date=date,
                    max_people=remaining
                ))
        return available
