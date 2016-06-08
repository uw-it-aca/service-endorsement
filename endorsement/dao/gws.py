"""
This module encapsulates the interactions with the restclients.gws,
provides access to the existing endorsement groups
"""

import logging
import re
import sys
import traceback
from restclients.exceptions import InvalidNetID
from restclients.exceptions import DataFailureException
from restclients.models.gws import Group, GroupReference, GroupUser
from restclients.gws import GWS
from endorsement.util.log import log_exception, log_resp_time
from endorsement.util.time_helper import Timer


logger = logging.getLogger(__name__)
NAME_PREFIX = "u_msca_endorse_splync_*"
ENDORSER_GROUP = "uw_employee"
gws = GWS()


def get_endorsees_by_endorser(endorser_uwnetid):
    """
    Returns a list of netids of the endorsees currently
    endorsed by the given endorser_uwnetid on uw Group Service.
    """
    ret_list = []
    for gr in get_msca_endorsement_groups():
        pattern = r"^%s%s$" % (NAME_PREFIX[:-1], endorser_uwnetid)
        if re.match(pattern, gr.name):
            members = gws.get_effective_members(gr.name)
            if members is None:
                return ret_list
            for mem in members:
                if mem.is_uwnetid():
                    ret_list.append(mem.name)
    return ret_list

def get_msca_endorsement_groups():
    """
    Returns a list of restclients.models.gws.GroupReference objects
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
