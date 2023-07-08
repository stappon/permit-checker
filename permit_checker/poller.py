import logging
from pprint import pformat
from time import sleep
from typing import Set
from permit_checker.protocols import Notifier, RecreationClient
from permit_checker.types import AvailableDay, DesiredPermit, PermitInfo


class Poller:
    def __init__(self, client: RecreationClient, notifier: Notifier, interval_secs: int):
        self._client = client
        self._notifier = notifier
        self._secs = interval_secs
        self._logger = logging.getLogger(__name__)

        # quick 'n dirty in-memory caching to cut down on redundant notifications
        self._last_received: Set[AvailableDay] = set()

    def poll_once(self, desired: DesiredPermit, info: PermitInfo) -> None:
        try:
            received = self._client.get_availability(desired)
            newly_available = received - self._last_received
            if len(newly_available) > 0:
                self._notifier.notify(newly_available, info)
                self._last_received = received
                self._logger.info("%s new permits found for %s", len(newly_available), info.display_name)
                self._logger.debug("Details: %s", pformat(newly_available))
            else:
                self._logger.info("No new permits found")
        except Exception as e:
            self._logger.exception(e)

        sleep(self._secs)
