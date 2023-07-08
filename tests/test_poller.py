import datetime as dt
from typing import Set
from permit_checker.types import AvailableDay, DesiredPermit, PermitInfo
from permit_checker.poller import Poller


class StubNotifier:
    def __init__(self):
        self.notified = []

    def notify(self, available: Set[AvailableDay], info: PermitInfo) -> None:
        self.notified.append((available, info))

class StubClient:
    def __init__(self, first, second=None, third=None):
        self._first = first
        self._second = first if second is None else second
        self._call = 0

    def get_availability(self, _: DesiredPermit) -> Set[AvailableDay]:
        self._call = self._call + 1
        if self._call == 1:
            return self._first
        if self._call == 2:
            return self._second
        else:
            assert False, "too many calls to client"

def make_desired_and_info():
    return (
        DesiredPermit(
            permit_id="12345",
            dates=[dt.datetime(2023, 7, 21)],
            divisions=["406"],
            min_people=2
        ),
        PermitInfo("12345", "permit", "131", { "406" : "foo"})
    )

def test_notify_on_first_poll():
    available = set([AvailableDay("12345", "406", dt.datetime(2023, 7, 21), 2)])
    info = PermitInfo("12345", "permit", "131", { "406" : "foo"})
    client = StubClient(available)
    notifier = StubNotifier()
    poller = Poller(client, notifier, 0)

    desired, info = make_desired_and_info()
    poller.poll_once(desired, info)
    assert notifier.notified == [(available, info)]

def test_do_not_notify_on_first_poll_if_no_results():
    client = StubClient(set())
    notifier = StubNotifier()
    poller = Poller(client, notifier, 0)

    desired, info = make_desired_and_info()
    poller.poll_once(desired, info)
    assert notifier.notified == []

def test_do_not_notify_if_results_unchanged():
    available = set([AvailableDay("12345", "406", dt.datetime(2023, 7, 21), 2)])
    client = StubClient(available)
    notifier = StubNotifier()
    poller = Poller(client, notifier, 0)

    desired, info = make_desired_and_info()
    poller.poll_once(desired, info)
    poller.poll_once(desired, info)
    assert notifier.notified == [(available, info)]

def test_notify_of_new_results():
    available_day1 = AvailableDay("12345", "406", dt.datetime(2023, 7, 21), 2)
    available_day2 = AvailableDay("12345", "406", dt.datetime(2023, 7, 22), 2)
    client = StubClient(set([available_day1]), set([available_day1, available_day2]))
    notifier = StubNotifier()
    poller = Poller(client, notifier, 0)

    desired, info = make_desired_and_info()
    poller.poll_once(desired, info)
    poller.poll_once(desired, info)
    assert notifier.notified == [(set([available_day1]), info), (set([available_day2]), info)]


def test_do_not_notify_if_fewer_results():
    available_day1 = AvailableDay("12345", "406", dt.datetime(2023, 7, 21), 2)
    available_day2 = AvailableDay("12345", "406", dt.datetime(2023, 7, 22), 2)
    client = StubClient(set([available_day1, available_day2]), set([available_day1]))
    notifier = StubNotifier()
    poller = Poller(client, notifier, 0)

    desired, info = make_desired_and_info()
    poller.poll_once(desired, info)
    poller.poll_once(desired, info)
    assert notifier.notified == [(set([available_day1, available_day2]), info)]
