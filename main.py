import logging
import os
import smtplib
import sys
from typing import Set
from permit_checker.arg_parser import parse_arguments
from permit_checker.info_fetcher import PermitInfoFetcher

from permit_checker.protocols import RecreationClient, Notifier, RecreationWebService
from permit_checker.types import AvailableDay, DesiredPermit, PermitInfo
from permit_checker.clients.inyo_client import InyoNationalForestClient
from permit_checker.clients.itinerary_client import PermitItineraryApiClient
from permit_checker.datetime_utils import all_days_between_dates
from permit_checker.email_notifier import EmailNotifier
from permit_checker.poller import Poller
from permit_checker.webservice import RealRecreationWebService

# Example calls:
# Mt Whitney day use: python main.py --id 445860 --divisions 406 --earliest 2023-09-20 --latest 2023-10-30
# Rockies east inlet: python main.py --id 4675320 --divisions 4675320127 4675320129 4675320130 4675320131 --earliest 2023-08-05 --latest 2023-08-07 --people 2 --test True

def make_notifier(test_mode: bool) -> Notifier:
    if test_mode:
        class NoOpNotifier:
            def notify(self, available: Set[AvailableDay], info: PermitInfo) -> None:
                for a in available:
                    logging.getLogger(__name__).info("Permit available: %s (%s)", a.date, info.divisions[a.division])
        return NoOpNotifier()
    else:
        return EmailNotifier(
            server = smtplib.SMTP('smtp.mailgun.org', 587),
            recipient = os.getenv('PERMIT_EMAIL_RECEIVER'),
            sender = os.getenv('PERMIT_EMAIL_SENDER'),
            password = os.getenv('PERMIT_EMAIL_PW')
        )

def make_client(web_service: RecreationWebService, info: PermitInfo) -> RecreationClient:
    # This is likely an incomplete heuristic, but works for everything I've tried so far
    if info.orgs == "131":
        return InyoNationalForestClient(web_service)
    else:
        return PermitItineraryApiClient(web_service)


if __name__ == '__main__':

    print(sys.argv)

    config = parse_arguments()

    log_format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    logging.basicConfig(format=log_format, level=logging.INFO)
    logging.getLogger(__name__).info("Starting (manual test mode = %s)", config.test_mode)

    web_service = RealRecreationWebService()
    info = PermitInfoFetcher(web_service).get_info(config.desired.permit_id)

    notifier = make_notifier(test_mode=config.test_mode)
    client = make_client(web_service, info)
    poller = Poller(client, notifier, interval_secs=config.poll_time_secs)

    while True:
        poller.poll_once(config.desired, info)
