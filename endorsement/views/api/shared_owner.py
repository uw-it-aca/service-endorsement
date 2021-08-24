# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
import logging
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from uw_saml.decorators import group_required
from endorsement.views.rest_dispatch import RESTDispatch
from uw_uwnetid.admin import get_admins_for_shared_netid
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import get_endorsements_for_endorsee
from endorsement.services import endorsement_services
from endorsement.exceptions import (
    NoEndorsementException, UnrecognizedUWNetid, InvalidNetID)


logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
@method_decorator(group_required(settings.PROVISION_ADMIN_GROUP),
                  name='dispatch')
class SharedOwner(RESTDispatch):
    def get(self, request, *args, **kwargs):
        shared_netid = self.kwargs['shared_netid']

        if len(shared_netid) <= 0:
            return self.error_response(401, "Invalid shared netid")

        active_services = set()

        try:
            for admin in get_admins_for_shared_netid(shared_netid):
                if admin.is_owner():
                    try:
                        endorser = get_endorser_model(admin.name)
                    except UnrecognizedUWNetid:
                        return self.error_response(
                            401, ('Shared netid owner "{}" is'
                                  ' not a valid endorser').format(admin.name))

                    try:
                        endorsee = get_endorsee_model(shared_netid)
                        if not endorsee.kerberos_active_permitted:
                            return self.error_response(
                                405, "Shared netid has no Kerberos Principle")
                    except (UnrecognizedUWNetid, InvalidNetID):
                        return self.error_response(
                            404, "Shared netid not found")

                    data = {
                        'endorser': endorser.json_data(),
                        'endorsee': endorsee.json_data(),
                        'endorsements': {}
                    }

                    for service in endorsement_services():
                        # if there are absolutely no shared netids
                        # allowed don't provide a back door
                        if not service.shared_params:
                            continue

                        try:
                            endorsement_record = service.get_endorsement(
                                endorser, endorsee)
                            endorsement = endorsement_record.json_data()
                            endorsement['endorser'] = endorser.json_data()
                            endorsement['endorsers'] = [
                                ee.endorser.json_data()
                                for ee in get_endorsements_for_endorsee(endorsee)
                                if ee.category_code == service.category_code]

                            active_services.add(service.service_name)
                        except (EndorsementRecord.DoesNotExist,
                                NoEndorsementException):
                            endorsement = {
                                'category_name': service.category_name,
                                'valid_shared': True
                            }

                        data['endorsements'][service.service_name] = endorsement

                    return self.json_response(data)
        except Exception as ex:
            return self.error_response(412, "{}".format(ex))

        return self.error_response(400, 'Provided netid is not a shared netid')
