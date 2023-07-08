from typing import Protocol
import datetime as dt
from typing import Set

from permit_checker.types import AvailableDay, DesiredPermit, PermitInfo


class Notifier(Protocol):
    def notify(self, available: Set[AvailableDay], info: PermitInfo) -> None:
        pass


class RecreationClient(Protocol):
    def get_availability(self, desired: DesiredPermit) -> Set[AvailableDay]:
        pass


class RecreationWebService(Protocol):
    def get_inyo_county_availability(
        self,
        permit_id: str,
        start_date: dt.datetime,
        end_date: dt.datetime
    ) -> dict:
        pass

    def get_permit_itinerary_availability(self, permit_id: str, division: str, month: int, year: int) -> dict:
        pass

    def get_permit_content(self, permit_id: str) -> dict:
        pass
