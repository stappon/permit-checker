import datetime as dt
import smtplib
from unittest.mock import ANY, Mock
from permit_checker.types import AvailableDay, PermitInfo
from permit_checker.email_notifier import EmailNotifier

def test_email_sent():
    mock_smtp = Mock(smtplib.SMTP)
    notifier = EmailNotifier(
        mock_smtp, 'foo@foo.org', 'asdf', 'you@test.com'
    )

    available = set([AvailableDay("12345", "406", dt.datetime(2023, 7, 21), 2)])
    info = PermitInfo("12345", "foo", "131", {"406": "bar"})
    notifier.notify(available, info)

    mock_smtp.starttls.assert_called()
    mock_smtp.login.assert_called_with('foo@foo.org', 'asdf')
    mock_smtp.sendmail.assert_called_with(
        'foo@foo.org',
        'you@test.com',
        ANY
    )

def test_email_content():
    mock_smtp = Mock(smtplib.SMTP)
    notifier = EmailNotifier(
        mock_smtp, 'foo@foo.org', 'asdf', 'you@test.com'
    )

    available = set([
        AvailableDay("12345", "406", dt.datetime(2023, 7, 21), 2),
        AvailableDay("12345", "0", dt.datetime(2023, 7, 22), 2), # Unknown division
    ])
    info = PermitInfo("12345", "foo", "131", {"406": "bar"})
    notifier.notify(available, info)

    class Matcher(str):
        header = [
            'MIME-Version: 1.0',
            'From: foo@foo.org',
            'To: you@test.com',
            'Subject: Permits available!',
            ''
        ]
        body = [
            'Content-Type: text/plain; charset="us-ascii"',
            'MIME-Version: 1.0',
            'Content-Transfer-Encoding: 7bit',
            '',
            'foo permits available:',
            '* 2023-07-21: 2 available (bar)',
            '* 2023-07-22: 2 available (Unknown)'
        ]
        def __eq__(self, other):
            lines = other.split('\n')
            # Untested lines are unique to each message instance
            return lines[1:6] == self.header and lines[7:14] == self.body

    def __repr__(self):
        return "header={}\nbody:{}".format(self.header, self.body)

    mock_smtp.sendmail.assert_called_with(
        ANY,
        ANY,
        Matcher()
    )
