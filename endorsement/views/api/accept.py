import logging
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.services import endorsement_services
from endorsement.views.rest_dispatch import RESTDispatch, invalid_session


logger = logging.getLogger(__name__)


class Accept(RESTDispatch):
    """
    validate accept request
    """

    def post(self, request, *args, **kwargs):
        try:
            accept_id = request.data['accept_id']
        except KeyError:
            return invalid_session(logger)

        user_service = UserService()
        netid = user_service.get_user()
        if not netid:
            return invalid_session(logger)

        original_user = user_service.get_original_user()
        acted_as = None if (netid == original_user) else original_user

        records = EndorsementRecord.objects.get_accept_endorsement(accept_id)
        if len(records) != 1:
            return invalid_session(logger)

        record = records[0]

        for service in endorsement_services():
            if record.category_code == service.category_code:
                json_data = service.store_endorsement(
                    record.endorser, record.endorsee,
                    acted_as, record.reason).json_data()
                json_data['service_tag'] = service.service_name
                json_data['service_link'] = service.service_link

        return self.json_response(json_data)
