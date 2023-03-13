# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from userservice.user import UserService
from endorsement.models import AccessRecord
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.persistent_messages import get_persistent_messages
from endorsement.dao.access import (
    get_accessee_model, store_access, revoke_access)
from endorsement.dao.office import is_office_permitted, get_office_accessor
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser, data_error)
from endorsement.exceptions import UnrecognizedUWNetid, InvalidNetID
from endorsement.util.auth import is_only_support_user
from uw_msca.access_rights import get_access_rights
import logging


logger = logging.getLogger(__name__)


class Access(RESTDispatch):
    """
    Return maiboxes and access associated with netid
    """
    def get(self, request, *args, **kwargs):
        try:
            netid, acted_as = self._validate_user(request)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        netids = {}

        if is_office_permitted(netid):
            accessee = get_accessee_model(netid)
            netids[netid] = {
                'name': accessee.display_name,
                'access': self._load_access_for_accessee(accessee)
            }

        for supported in get_supported_resources_for_netid(netid):
            if supported.is_owner() and (
                    supported.is_shared_netid() or supported.is_admin()):
                if is_office_permitted(supported.name):
                    accessee = get_accessee_model(supported.name)
                    netids[supported.name] = {
                        'name': accessee.display_name,
                        'access': self._load_access_for_accessee(accessee)
                    }

        return self.json_response({
            'netids': netids,
            'messages': get_persistent_messages()
        })

    def post(self, request, *args, **kwargs):
        try:
            netid, acted_as = self._validate_user(request)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        mailbox = request.data.get('mailbox', None)
        delegate = request.data.get('delegate', None)
        access_type = request.data.get('access_type', None)
        previous_access_type = request.data.get('previous_access_type', None)

        if not is_office_permitted(mailbox):
            return invalid_endorser(logger)

        accessee = get_accessee_model(mailbox)
        accessor = get_office_accessor(delegate)

        # remove previous access type before setting updated type
        if previous_access_type and previous_access_type != access_type:
            revoke_access(
                accessee, accessor, previous_access_type, acted_as)

        access = store_access(accessee, accessor, access_type, acted_as)

        return self.json_response(access.json_data())

    def delete(self, request, *args, **kwargs):
        try:
            netid, acted_as = self._validate_user(request)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        mailbox = request.GET.get('mailbox')
        delegate = request.GET.get('delegate')
        access_type = request.GET.get('access_type')

        accessee = get_accessee_model(mailbox)
        accessor = get_office_accessor(delegate)
        access = revoke_access(accessee, accessor, access_type, acted_as)
        return self.json_response(access.json_data())

    def _load_access_for_accessee(self, accessee):
        accessors = []
        for ar in AccessRecord.objects.get_access_for_accessee(accessee):
            accessors.append(ar.json_data())

        return accessors

    def _validate_user(self, request):
        user_service = UserService()
        netid = user_service.get_user()
        if not netid:
            raise UnrecognizedUWNetid()

        original_user = user_service.get_original_user()
        acted_as = None if (netid == original_user) else original_user
        if acted_as and is_only_support_user(request):
            raise InvalidNetID()

        return netid, acted_as


class AccessRights(RESTDispatch):
    """
    Return Office mailbox access right list
    """
    def get(self, request, *args, **kwargs):
        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger)

        try:
            access_rights = []

            for t in get_access_rights():
                access_rights.append(t.json_data())

            return self.json_response(access_rights)
        except Exception as ex:
            return data_error(logger, "{}".format(ex))
