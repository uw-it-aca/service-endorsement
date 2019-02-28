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
    try:
        subs = get_kerberos_subs(uwnetid)
        if subs is None or subs.permits is None or subs.is_status_inactive():
            return False

        for permit in subs.permits:
            if (permit.is_status_current() and
                (permit.is_category_staff() or
                 permit.is_category_faculty() or
                 permit.is_category_affiliate_employee() or
                 permit.is_category_department() or
                 permit.is_category_system_administrator())):
                return True

    except Exception:
        return handel_err(logger,
                          '{0} subs_60.has_active_kerberos_subs '.format(
                              uwnetid),
                          traceback.format_exc())
