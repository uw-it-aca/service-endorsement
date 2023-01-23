# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.dao.office import get_office_accessor
from endorsement.views.rest_dispatch import RESTDispatch, invalid_session
from userservice.user import UserService
from restclients_core.exceptions import DataFailureException
from uw_msca.validate_user import validate_user
import logging


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

            try:
                validate_user(name)
            except DataFailureException as ex:
                valid.append({
                    'name': name,
                    'display_name': display_name,
                    'mailbox': mailbox,
                    'is_valid': False,
                    'message': "{} Outlook Access{}".format(
                        "Unknown" if (ex.status == 404) else "Invalid",
                        " user" if (
                            ex.status == 404) else ": {}".format(ex.msg))
                })
                continue

            valid.append({
                'name': name,
                'display_name': display_name,
                'mailbox': mailbox,
                'is_valid': is_valid,
                'message': message
            })

        return self.json_response(valid)
