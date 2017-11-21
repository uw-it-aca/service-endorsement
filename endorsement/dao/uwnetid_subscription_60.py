"""
This module encapsulates the interactions with
the UW NeTID Subscription code 60
"""

import logging
import traceback
from uw_uwnetid.models import SubscriptionPermit
from uw_uwnetid.subscription_60 import get_kerberos_subs
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
    AFFILIATE_C_CODE = 15
    DEPARTMENT_C_CODE = 11
    valid_codes = [
        AFFILIATE_C_CODE,
        DEPARTMENT_C_CODE,
        SubscriptionPermit.STAFF_C_CODE,
        SubscriptionPermit.FACULTY_C_CODE,
        SubscriptionPermit.CLINICIAN_C_CODE]
    try:
        subs = get_kerberos_subs(uwnetid)
        if subs is None or subs.permits is None or subs.is_status_inactive():
            return False

        for permit in subs.permits:
            if (permit.category_code in valid_codes and
                    permit.is_status_current()):
                return True

    except Exception:
        return handel_err(logger,
                          '%s subs_60.has_active_kerberos_subs ' % uwnetid,
                          traceback.format_exc())
