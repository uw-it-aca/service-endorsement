"""
This module encapsulates the interactions with
the UW NeTID Subscription code 60
"""

import logging
import traceback
from uw_uwnetid.subscription_60 import (
    get_kerberos_subs, get_kerberos_subs_permits)
from endorsement.dao import handel_err


logger = logging.getLogger(__name__)


def get_kerberos_subs_status(netid):
    """
    Return status_name and permitted value
    """
    subs = get_kerberos_subs(netid)
    if subs is None:
        return None, None
    return subs.status_name, subs.permitted


def is_valid_endorsee(uwnetid):
    try:
        permits = get_kerberos_subs_permits(uwnetid)
        if permits is None:
            return False
        for permit in permits:
            if ((permit.is_category_staff() or
                 permit.is_category_faculty() or
                 permit.is_status_current())
                    and permit.is_status_current()):
                return True

    except Exception:
        return handel_err(logger,
                          '%s subs_60.has_active_kerberos_subs ' % uwnetid,
                          traceback.format_exc())
