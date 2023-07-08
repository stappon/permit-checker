from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Set

from permit_checker.datetime_utils import datetime_to_datestring
from permit_checker.types import AvailableDay, PermitInfo


class EmailNotifier:
    def __init__(self, server, sender, password, recipient):
        self._server = server
        self._sender = sender
        self._password = password
        self._recipient = recipient

        server.starttls()
        server.login(self._sender, self._password)

    def notify(self, available: Set[AvailableDay], info: PermitInfo) -> None:
        self._server.sendmail(
            self._sender,
            self._recipient,
            self._make_message(
                "Permits available!",
                self._make_email_body(available, info)
            )
        )

    def _make_message(self, subject, body) -> str:
        msg = MIMEMultipart()
        msg['From'] = self._sender
        msg['To'] = self._recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body))
        return msg.as_string()

    @staticmethod
    def _make_email_body(available: Set[AvailableDay], info: PermitInfo):
        header = "{} permits available:\n".format(info.display_name)

        def to_string(day: AvailableDay):
            return '* {}: {} available ({})'.format(
                datetime_to_datestring(day.date),
                day.max_people,
                info.divisions.get(day.division) or "Unknown",
            )

        sorted = list(available)
        sorted.sort(key=lambda d: d.date)
        return header + '\n'.join([to_string(d) for d in sorted])
