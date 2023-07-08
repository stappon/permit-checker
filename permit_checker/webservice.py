
import datetime as dt
import requests
from requests import Response

from permit_checker.datetime_utils import datetime_to_datestring


class RealRecreationWebService:
    _HEADERS = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    }
    _INYO_URL = "https://www.recreation.gov/api/permitinyo/{}/availability"
    _ITINERARY_URL = "https://www.recreation.gov/api/permititinerary/{}/division/{}/availability/month"
    _PERMIT_CONTENT_URL = "https://www.recreation.gov/api/permitcontent/{}"

    def get_inyo_county_availability(self, permit_id: str, start_date: dt.datetime, end_date: dt.datetime) -> dict:
        query_params = (
            ('start_date', datetime_to_datestring(start_date)),
            ('end_date', datetime_to_datestring(end_date)),
            ('commercial_acct', 'false'),
            ('is_lottery', 'false')
        )
        response = requests.get(
            self._INYO_URL.format(permit_id),
            headers=self._HEADERS,
            params=query_params
        )
        return self._process_response(response)

    def get_permit_itinerary_availability(self, permit_id: str, division: str, month: int, year: int) -> dict:
        query_params = (
             ('month', month),
             ('year', year)
        )
        response = requests.get(
            self._ITINERARY_URL.format(permit_id, division),
            headers=self._HEADERS,
            params=query_params
        )
        return self._process_response(response)

    def get_permit_content(self, permit_id: str) -> dict:
        response = requests.get(
            self._PERMIT_CONTENT_URL.format(permit_id),
            headers=self._HEADERS
        )
        return self._process_response(response)

    @staticmethod
    def _process_response(response: Response) -> dict:
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(str("%s %s" % (response.status_code, response.text)))
