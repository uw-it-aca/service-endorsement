# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from userservice.user import UserService
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)


logger = logging.getLogger(__name__)


class Validate(RESTDispatch):
    """
    Return valid names for maibox access
    """
    def post(self, request, *args, **kwargs):
        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger)

        # if not has_office_inbox(netid):
        #     return invalid_endorser(logger)

        valid = []
        mailbox = request.data.get('mailbox', None);
        names = request.data.get('delegates', [])
        for name in names:

            #
            # call validation dao.access_office
            #

            valid.append({
                'name': name,
                'mailbox': mailbox,
                'can_access': True,
                'message': 'Access valid'
            })

        return self.json_response(valid)
