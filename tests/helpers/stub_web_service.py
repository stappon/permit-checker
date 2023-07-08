import datetime as dt

class StubWebService:

    def __init__(self, july, august={}):
        self._july = july
        self._august = august

    def get_inyo_county_availability(self, permit_id: str, start_date: dt.datetime, end_date: dt.datetime) -> dict:
        # This endpoint requires start/end dates to be the first/last of a month
        assert start_date.day == 1
        assert (end_date + dt.timedelta(1)).day == 1

        return self._get_fake_data(start_date.month)

    def get_permit_itinerary_availability(self, permit_id: str, division: str, month: int, year: int) -> dict:
        return self._get_fake_data(month)

    def _get_fake_data(self, month):
        if month == 7:
            payload = self._july
        if month == 8:
            payload = self._august
        return { "payload": payload }
