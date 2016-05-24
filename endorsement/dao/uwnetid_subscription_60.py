"""
This module encapsulates the interactions with
the UW NeTID Subscription code 60
"""

import logging
import json
from restclients.uwnetid.subscription_60 import is_current_staff,\
    is_current_faculty


logger = logging.getLogger(__name__)


def is_valid_endorser(uwnetid):
    return is_current_staff(uwnetid) or is_current_faculty(uwnetid)
