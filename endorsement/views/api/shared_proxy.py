# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
import logging
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from uw_saml.decorators import group_required
from userservice.user import UserService
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.services import get_endorsement_service, is_valid_endorser
from endorsement.views.rest_dispatch import RESTDispatch, invalid_endorser
from endorsement.exceptions import (
    InvalidNetID, UnrecognizedUWNetid, NoEndorsementException,
    CategoryFailureException, SubscriptionFailureException,
    MissingReasonException)


logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
@method_decorator(group_required(settings.PROVISION_ADMIN_GROUP),
                  name='dispatch')
class SharedProxyEndorse(RESTDispatch):
    """
    Endorse provided shared netid on behalf of session user (admin)
    """
    def post(self, request, *args, **kwargs):
        service_name = request.data.get('service', '')
        reason = request.data.get('reason', '')
        endorse = request.data.get('endorse', 'true')
        endorsee_netid = request.data.get('endorsee', '')
        endorser_netid = request.data.get('endorser', '')
        if not is_valid_endorser(endorser_netid):
            return invalid_endorser(logger)

        admin_netid = UserService().get_original_user()

        try:
            endorser = get_endorser_model(endorser_netid)
        except UnrecognizedUWNetid:
            return self.error_response(
                401, ('Shared netid owner "{}" is'
                      ' not a valid endorser').format(endorser_netid))

        try:
            endorsee = get_endorsee_model(endorsee_netid)
            if not endorsee.kerberos_active_permitted:
                return self.error_response(
                    405, "Shared netid has no Kerberos Principle")
        except (UnrecognizedUWNetid, InvalidNetID):
            return self.error_response(
                404, "Shared netid not found")

        service = get_endorsement_service(service_name)
        if service is None:
            return self.error_response(405, 'Invalid Service Provided')

        if endorse.lower() in ['1', 'true', 'yes']:
            reason = request.data.get('reason', '')
            if len(reason) <= 0:
                return self.error_response(405, 'Invalid Reason Provided')

            endorsement = service.store_endorsement(
                endorser, endorsee, admin_netid, reason)
        elif endorse.lower() in ['0', 'false', 'no']:
            endorsement = service.clear_endorsement(endorser, endorsee)

        return self.json_response(endorsement.json_data())
