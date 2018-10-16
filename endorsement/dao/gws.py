"""
This module encapsulates the interactions with the uw_gws,
provides access to the existing endorsement groups
"""

import logging
import sys
import traceback
from restclients_core.exceptions import InvalidNetID
from restclients_core.exceptions import DataFailureException
from uw_gws import GWS
from endorsement.util.log import log_exception, log_resp_time
from endorsement.util.time_helper import Timer


logger = logging.getLogger(__name__)
ENDORSER_GROUP = "uw_employee"
gws = GWS()


def is_valid_endorser(uwnetid):
    """
    Return True if the user is in PersonReg currently
    """
    action = '{0} is_effective_member of {1} group'.format(
        uwnetid, ENDORSER_GROUP)
    timer = Timer()
    try:
        return gws.is_effective_member(ENDORSER_GROUP, uwnetid)
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
