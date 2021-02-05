"""
Module encapsulates the interactions with the uw_gws,
valid endorser authorization test

Valid endorsers are defined as being in the GWS group defined
by VALID_ENDORSER_GROUP.  Unless defined in settings, the group
used for validation is "uw_employee"
"""

from django.conf import settings
from endorsement.util.log import log_exception, log_resp_time
from endorsement.util.time_helper import Timer
from restclients_core.exceptions import InvalidNetID
from restclients_core.exceptions import DataFailureException
from uw_gws import GWS
import logging
import sys
import traceback

logger = logging.getLogger(__name__)
gws = GWS()

ENDORSER_GROUP = getattr(settings, "VALID_ENDORSER_GROUP", "uw_employee")


def is_valid_endorser(uwnetid):
    """
    Return True if the user is in the valid endorsers GWS group
    """
    action = '{0} is_effective_member of {1} group'.format(
        uwnetid, ENDORSER_GROUP)
    timer = Timer()
    try:
        return is_group_member(uwnetid, ENDORSER_GROUP)
    except Exception:
        log_exception(logger,
                      action,
                      traceback.format_exc())
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if isinstance(exc_value, InvalidNetID):
            return False
        if isinstance(exc_value, DataFailureException) and\
                exc_value.status == 404:
            return False
        raise
    finally:
        log_resp_time(logger, action, timer)


def is_group_member(uwnetid, group):
    """
    Return True if the netid is in the specified group
    """
    try:
        return gws.is_effective_member(group, uwnetid)
    except DataFailureException as ex:
        if ex.status != 404:
            raise

    return False
