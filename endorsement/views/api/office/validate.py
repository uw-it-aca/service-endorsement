# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from userservice.user import UserService
from endorsement.dao.office import get_office_accessor
from endorsement.views.rest_dispatch import RESTDispatch, invalid_session


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
        mailbox = request.data.get('mailbox', None)
        names = request.data.get('delegates', [])
        for name in names:

            try:
                accessor = get_office_accessor(name)
                is_valid = True
                display_name = accessor.display_name
                message = 'Access Valid'
            except Exception as ex:
                is_valid = False
                display_name = None
                message = "{}".format(ex)

            #
            # call validation dao.access_office
            #

            valid.append({
                'name': name,
                'display_name': display_name,
                'mailbox': mailbox,
                'is_valid': is_valid,
                'message': message
            })

        return self.json_response(valid)
