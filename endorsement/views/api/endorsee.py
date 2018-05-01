import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from endorsement.views.decorators import admin_required
from endorsement.dao.endorse import get_endorsements_for_endorsee_re
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time
from endorsement.views.rest_dispatch import RESTDispatch
from endorsement.exceptions import UnrecognizedUWNetid


logger = logging.getLogger(__name__)


class Endorsee(RESTDispatch):
    """
    Show endorsements for endorsee
    """
    @method_decorator(login_required)
    @method_decorator(admin_required('PROVISION_ADMIN_GROUP'))
    def get(self, request, *args, **kwargs):
        timer = Timer()

        endorsee_regex = self.kwargs['endorsee']
        endorsees = {
            'endorsements': []
        }

        for er in get_endorsements_for_endorsee_re(endorsee_regex):
            endorsees['endorsements'].append(er.json_data())

        log_resp_time(logger, "endorsee", timer)
        return self.json_response(endorsees)
