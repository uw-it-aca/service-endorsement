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
from endorsement.util.auth import is_only_support_user
from uw_msca.access_rights import get_access_rights
import logging
import random


logger = logging.getLogger(__name__)


class Access(RESTDispatch):
    """
    Return maiboxes and access associated with netid
    """
    def get(self, request, *args, **kwargs):
        try:
            netid = self._validate_user(request)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

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

    def delete(self, request, *args, **kwargs):
        try:
            netid = self._validate_user(request)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)



        ## do stuff here


        return self.json_response({'response': 'OK'})

    def post(self, request, *args, **kwargs):
        try:
            netid = self._validate_user(request)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        # if not has_office_inbox(netid):
        #     return invalid_endorser(logger)


        mailbox = request.data.get('mailbox', None)
        delegate = request.data.get('delegate', None)
        access_type = request.data.get('access_type', None)


        # Do stuff here


        access = {
            'mailbox': mailbox,
            'delegate': delegate,
            'right_id': access_type
        }

        return self.json_response(access)

    def _load_access_for_netid(self, mailbox):
        if (random.random() * 100) < 60.0:
            return []
        else:
            l = []
            for n in range(random.choice([0, 1, 2, 3])):
                l.append({
                    'mailbox': mailbox,
                    'delegate': 'delegate{}'.format(n),
                    'right_id': random.choice([1, 2, 3, 4]),
                    'status': 'Provisioned'
                })

            return l

    def _validate_user(self, request):
        user_service = UserService()
        netid = user_service.get_user()
        if not netid:
            raise UnrecognizedUWNetid()

        original_user = user_service.get_original_user()
        acted_as = None if (netid == original_user) else original_user
        if acted_as and is_only_support_user(request):
            raise InvalidNetID()

        return netid


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
