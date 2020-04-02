import logging
from endorsement.dao.endorse import get_endorsement_records_for_endorsee_re
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time, log_data_error_response
from endorsement.views.rest_dispatch import RESTDispatch
from endorsement.util.auth import AdminGroupAuthentication
from rest_framework.authentication import TokenAuthentication


logger = logging.getLogger(__name__)


class Endorsee(RESTDispatch):
    """
    Show endorsements for endorsee
    """
    authentication_classes = [AdminGroupAuthentication, TokenAuthentication]

    def get(self, request, *args, **kwargs):
        timer = Timer()

        endorsee_regex = self.kwargs['endorsee']
        endorsees = {
            'endorsements': []
        }

        try:
            for er in get_endorsement_records_for_endorsee_re(endorsee_regex):
                endorsees['endorsements'].append(er.json_data())
        except Exception:
            log_data_error_response(logger, timer)
            return RESTDispatch().error_response(
                543, """
Data not available due to an error.  Check your regular expression.
""")

        log_resp_time(logger, "endorsee", timer)
        return self.json_response(endorsees)
