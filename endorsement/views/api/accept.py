import logging
import json
#from django.contrib.auth.decorators import login_required
#from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.dao.endorse import (
    store_office365_endorsement, store_google_endorsement)
from endorsement.util.time_helper import Timer
from endorsement.views.rest_dispatch import RESTDispatch, invalid_session


logger = logging.getLogger(__name__)


class Accept(RESTDispatch):
    """
    validate accept request
    """

    # @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        timer = Timer()

        try:
            accept = json.loads(request.read())
            accept_id = accept['accept_id']
        except KeyError:
            return invalid_session(logger, timer)

        user_service = UserService()
        netid = user_service.get_user()
        if not netid:
            return invalid_session(logger, timer)

        original_user = user_service.get_original_user()
        acted_as = None if (netid == original_user) else original_user

        records = EndorsementRecord.objects.get_accept_endorsement(accept_id)
        if len(records) != 1:
            return invalid_session(logger, timer)

        record = records[0]

        is_o365 = (
            record.category_code == EndorsementRecord.OFFICE_365_ENDORSEE)
        is_google = (
            record.category_code == EndorsementRecord.GOOGLE_SUITE_ENDORSEE)

        if is_o365:
            json_data = store_office365_endorsement(
                record.endorser, record.endorsee,
                acted_as, record.reason).json_data()
        elif is_google:
            json_data = store_google_endorsement(
                record.endorser, record.endorsee,
                acted_as, record.reason).json_data()

        json_data['is_o365'] = is_o365
        json_data['is_google'] = is_google

        return self.json_response(json_data)
