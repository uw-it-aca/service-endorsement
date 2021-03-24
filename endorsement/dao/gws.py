"""
Module encapsulates the interactions with the uw_gws,
valid endorser authorization test

Valid endorsers are defined as being in the GWS group defined
by VALID_ENDORSER_GROUP.  Unless defined in settings, the group
used for validation is "uw_employee"
"""

from django.conf import settings
from endorsement.util.log import log_exception
from restclients_core.exceptions import DataFailureException
from uw_gws import GWS
import logging
import traceback

logger = logging.getLogger(__name__)
gws = GWS()

ENDORSER_GROUP = getattr(settings, "VALID_ENDORSER_GROUP", "uw_employee")


def is_valid_endorser(uwnetid):
    """
    Return True if the user is in the valid endorsers GWS group
    """
    try:
        return endorser_group_member(uwnetid)
    except Exception:
        return False


def endorser_group_member(uwnetid):
    return is_group_member(uwnetid, ENDORSER_GROUP)


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
                          uwnetid, ENDORSER_GROUP),
                      traceback.format_exc())
        raise

