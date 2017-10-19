"""
This module encapsulates the interactions with
the UW NeTID Subscription code 60
"""

import logging
import traceback
from uw_uwnetid.subscription_60 import get_kerberos_subs
from endorsement.dao import handel_err


logger = logging.getLogger(__name__)


def get_kerberos_subs_status(netid):
    """
    Return status_name and permitted value
    """
    subs = get_kerberos_subs(netid)
    return (subs.status_name, subs.permitted) if subs else (None, None)


def is_valid_endorsee(uwnetid):
    try:
        status, permitted = get_kerberos_subs_status(uwnetid)
        return (permitted and status.lower() == 'active')
    except Exception:
        return handel_err(logger,
                          '%s subs_60.has_active_kerberos_subs ' % uwnetid,
                          traceback.format_exc())
