# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from userservice.user import UserService
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.persistent_messages import get_persistent_messages
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser, data_error)
from endorsement.exceptions import (
    NoEndorsementException, UnrecognizedUWNetid, InvalidNetID)
from endorsement.services import get_endorsement_service
from uw_msca.access_rights import get_access_rights
import logging
import random


logger = logging.getLogger(__name__)


class Access(RESTDispatch):
    """
    Return maiboxes and access associated with netid
    """
    def get(self, request, *args, **kwargs):
        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger)

        o365 = get_endorsement_service('o365')
        netids = {}

        endorser = get_endorser_model(netid)
        endorsee = get_endorsee_model(netid)
        if o365.is_permitted(endorser, endorsee):
            netids[netid] = {
                'name': endorser.display_name,
                'access': self._load_access_for_netid(netid)
            }

        for supported in get_supported_resources_for_netid(netid):
            if supported.is_owner() and supported.is_shared_netid():
                endorsee = get_endorsee_model(supported.name)
                if o365.is_permitted(endorser, endorsee):
                    netids[supported.name] = {
                        'name': endorsee.display_name,
                        'access': self._load_access_for_netid(supported.name)
                    }

        return self.json_response({
            'netids': netids,
            'messages': get_persistent_messages()
        })

    def post(self, request, *args, **kwargs):
        user_netid = UserService().get_user()
        if not user_netid:
            return invalid_session(logger)

        # if not has_office_inbox(netid):
        #     return invalid_endorser(logger)

        netid = request.data.get('netid', None)
        delegate = request.data.get('delegate', None)
        access_type = request.data.get('access_type', None)


        # Do stuff here


        access = {
            'netid': netid,
            'delegate': delegate,
            'right_id': access_type
        }

        return self.json_response(access)

    def _load_access_for_netid(self, netid):
        if (random.random() * 100) < 60.0:
            return []
        else:
            l = []
            for n in range(random.choice([0, 1, 2, 3])):
                l.append({
                    'delegate': 'delegate{}'.format(n),
                    'right_id': random.choice([1, 2, 3, 4])
                })

            return l


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
