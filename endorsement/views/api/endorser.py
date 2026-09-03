# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging

from endorsement.dao.endorse import get_all_endorsements_by_endorser
from endorsement.dao.user import get_endorser_model
from endorsement.exceptions import UnrecognizedUWNetid
from endorsement.util.auth import SupportGroupAuthentication
from endorsement.util.log import log_data_error_response
from endorsement.views.rest_dispatch import RESTDispatch

logger = logging.getLogger(__name__)


class Endorser(RESTDispatch):
    """
    Return endorsements for given endorser
    """
    authentication_classes = [SupportGroupAuthentication]

    def get(self, request, *args, **kwargs):
        endorser_netid = self.kwargs['endorser']
        endorsees = {
            'endorsements': []
        }

        try:
            endorser = get_endorser_model(endorser_netid)
            for er in get_all_endorsements_by_endorser(endorser):
                endorsees['endorsements'].append(er.json_data())
        except UnrecognizedUWNetid:
            return RESTDispatch().error_response(
                404, f"Netid {endorser_netid} appears to be invalid.")
        except Exception as ex:
            log_data_error_response(logger, f"{ex}")
            return RESTDispatch().error_response(
                543, f"Error: {ex}")

        return self.json_response(endorsees)
