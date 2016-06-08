"""
This module encapsulates the interactions with
the UW NeTID Subscription code 60
"""

import logging
import json
import traceback
from restclients.uwnetid.subscription_60 import has_current_permit
from endorsement.dao import handel_err


logger = logging.getLogger(__name__)


def is_valid_endorsee(uwnetid):
    try:
        return has_current_permit(uwnetid)
    except Exception:
        return handel_err(logger,
                          '%s subscription_60.has_current_permit ' % uwnetid,
                          traceback.format_exc())
