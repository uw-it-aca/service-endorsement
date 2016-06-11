"""
This module encapsulates the interactions with
the UW NeTID Subscription code 60
"""

import logging
import json
import traceback
from restclients.uwnetid.subscription_60 import has_active_kerberos_subs,\
    get_kerberos_subs
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
        return has_active_kerberos_subs(uwnetid)
    except Exception:
        return handel_err(logger,
                          '%s subs_60.has_active_kerberos_subs ' % uwnetid,
                          traceback.format_exc())
