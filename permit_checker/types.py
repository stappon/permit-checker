from typing import Dict, List
from dataclasses import dataclass
import datetime as dt


@dataclass(frozen=True)
class DesiredPermit:
    permit_id: str
    divisions: List[str]
    dates: List[dt.datetime]
    min_people: int


@dataclass(frozen=True)
class Configuration:
    desired: DesiredPermit
    test_mode: bool
    poll_time_secs: int


@dataclass(frozen=True)
class AvailableDay:
    permit_id: str
    division: str
    date: dt.datetime
    max_people: int


@dataclass(frozen=True)
class PermitInfo:
    id: str
    display_name: str
    orgs: str
    divisions: Dict[str, str]  # ID to name
