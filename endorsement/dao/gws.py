# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Module encapsulates the interactions with the uw_gws,
valid endorser authorization test

Valid endorsers are defined as being in the GWS group defined
by VALID_ENDORSER_GROUP.  Unless defined in settings, the group
used for validation is "uw_employee"
"""

from endorsement.util.log import log_exception
from endorsement.util.email import uw_email_address
from endorsement.exceptions import UnrecognizedGroupID
from restclients_core.exceptions import DataFailureException
from uw_gws import GWS
from uw_gws.exceptions import InvalidGroupID
import logging
import traceback

logger = logging.getLogger(__name__)
gws = GWS()


def is_group_member(uwnetid, group):
    """
    Return True if the netid is in the specified group
    """
    try:
        return gws.is_effective_member(group, uwnetid)
    except DataFailureException as ex:
        if ex.status == 404:
            return False

        log_exception(logger,
                      '{0} is_effective_member of {1} group'.format(
                          uwnetid, group),
                      traceback.format_exc())
        raise


def get_group_by_id(group):
    """
    Return GWS group
    """
    try:
        return gws.get_group_by_id(group)
    except InvalidGroupID as ex:
        raise UnrecognizedGroupID()
    except DataFailureException as ex:
        if ex.status == 404:
            raise UnrecognizedGroupID()

        log_exception(logger,
                      'get_group_by_id {}: {}'.format(group, ex),
                      traceback.format_exc())
        raise


def get_group_admin_emails(group_id):
    group = gws.get_group_by_id(group_id)
    emails = []
    for admin in group.admins:
        if admin.is_uwnetid():
            emails.append({
                'email': uw_email_address(admin.name),
                'display_name': admin.display_name})
        elif admin.is_eppn():
            emails.append({
                'email': admin.name,
                'display_name': admin.display_name})
        elif admin.is_group():
            emails += get_group_admin_emails(admin.name)

    return emails
