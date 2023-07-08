from permit_checker.protocols import RecreationWebService
from permit_checker.types import PermitInfo


class PermitInfoFetcher:
    def __init__(self, web_service: RecreationWebService):
        self._web_service = web_service

    def get_info(self, permit_id: str):
        payload = self._web_service.get_permit_content(permit_id)['payload']
        display_name = payload['name']
        orgs = payload['orgs']
        division_info = payload['divisions']
        divisions = {id: division_info[id]['name'] for id in division_info.keys()}
        return PermitInfo(permit_id, display_name, orgs, divisions)
