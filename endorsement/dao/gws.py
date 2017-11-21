"""
This module encapsulates the interactions with the uw_gws,
provides access to the existing endorsement groups
"""

import logging
import re
import sys
import traceback
from restclients_core.exceptions import InvalidNetID
from restclients_core.exceptions import DataFailureException
from uw_gws import GWS
from endorsement.util.log import log_exception, log_resp_time
from endorsement.util.time_helper import Timer


logger = logging.getLogger(__name__)
NAME_PREFIX = "u_msca_endorse_splync_*"
GROUP_NAME_PATTERN = r"^u_msca_endorse_splync_(.+)$"
ENDORSER_GROUP = "uw_employee"
gws = GWS()


def get_endorser_endorsees():
    """
    Returns a list of {'endorser': uwnetid, 'endorsees': [uwnetid]}
    of the msca_endorsement_groups on uw Group Service.
    """
    ret_list = []
    for gr in get_msca_endorsement_groups():
        match = re.search(GROUP_NAME_PATTERN, gr.name)
        if match:
            endorser_uwnetid = match.group(1)
            endorsees = []
            members = gws.get_effective_members(gr.name)
            if members is not None:
                for mem in members:
                    if mem.is_uwnetid():
                        endorsees.append(mem.name)
            ret_list.append({'endorser': endorser_uwnetid,
                             'endorsees': endorsees})

    return ret_list


def get_msca_endorsement_groups():
    """
    Returns a list of uw_gws.GroupReference objects
    """
    action = 'search groups with name=%s' % NAME_PREFIX
    timer = Timer()
    try:
        return gws.search_groups(name=NAME_PREFIX)
    finally:
        log_resp_time(logger, action, timer)


def is_valid_endorser(uwnetid):
    """
    Return True if the user is in PersonReg currently
    """
    action = '%s is_effective_member of %s group' % (uwnetid, ENDORSER_GROUP)
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
