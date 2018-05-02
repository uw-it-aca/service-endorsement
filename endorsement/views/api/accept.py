import logging
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.dao.user import (
    get_endorser_model, get_endorsee_model, get_endorsee_email_model)
from endorsement.dao.endorse import (
    store_office365_endorsement, store_google_endorsement)
from endorsement.util.time_helper import Timer
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import (
    InvalidNetID, UnrecognizedUWNetid,
    CategoryFailureException, SubscriptionFailureException,
    MissingReasonException)


logger = logging.getLogger(__name__)


class Accept(RESTDispatch):
    """
    validate accept request
    """
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        timer = Timer()

        try:
            accept = json.loads(request.read())
            accept_id = accept['accept_id']
        except KeyError:
            return invalid_session(logger, timer)

        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger, timer)

        records = EndorsementRecord.objects.filter(accept_id=accept_id)
        if len(records) != 1:
            return invalid_session(logger, timer)

        record = records[0]

        is_o365 = (
            record.category_code == EndorsementRecord.OFFICE_365_ENDORSEE)
        is_google = (
            record.category_code == EndorsementRecord.GOOGLE_SUITE_ENDORSEE)

        if is_o365:
            json_data = store_office365_endorsement(
                record.endorser, record.endorsee, record.reason).json_data()
        elif is_google:
            json_data = store_google_endorsement(
                record.endorser, record.endorsee, record.reason).json_data()

        json_data['is_o365'] = is_o365
        json_data['is_google'] = is_google

        return self.json_response(json_data)
