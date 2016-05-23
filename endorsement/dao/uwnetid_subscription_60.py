"""
This module encapsulates the interactions with
the UW NeTID Subscription code 60
"""

import logging
from restclients.uwnetid.subscription_60 import is_current_staff,\
    is_current_faculty
from endorsement.dao import get_netid_of_current_user


logger = logging.getLogger(__name__)


def is_current_user_valid_endorser():
    return is_valid_endorser(get_netid_of_current_user())


def is_valid_endorser(uwnetid):
    return is_current_staff(uwnetid) or is_current_faculty(uwnetid)


def get_user_affiliations():
    uwnetid = get_netid_of_current_user()
    entry = {'netid': uwnetid,
             'is_staff': is_current_staff(uwnetid),
             'is_faculty': is_current_faculty(uwnetid)
             }
    return json.dumps(entry)
