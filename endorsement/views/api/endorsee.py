# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from endorsement.dao.endorse import get_endorsement_records_for_endorsee_re
from endorsement.util.log import log_data_error_response
from endorsement.views.rest_dispatch import RESTDispatch
from endorsement.util.auth import SupportGroupAuthentication
from rest_framework.authentication import TokenAuthentication


logger = logging.getLogger(__name__)


class Endorsee(RESTDispatch):
    """
    Show endorsements for endorsee
    """
    authentication_classes = [TokenAuthentication, SupportGroupAuthentication]

    def get(self, request, *args, **kwargs):
        endorsee_regex = self.kwargs['endorsee']
        endorsees = {
            'endorsements': []
        }

        try:
            for er in get_endorsement_records_for_endorsee_re(endorsee_regex):
                endorsees['endorsements'].append(er.json_data())
        except Exception as ex:
            log_data_error_response(logger, "{}".format(ex))
            return RESTDispatch().error_response(
                543, """
Data not available due to an error.  Check your regular expression.
""")

        return self.json_response(endorsees)
