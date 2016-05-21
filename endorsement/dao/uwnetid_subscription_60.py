"""
This module encapsulates the interactions with
the UW NeTID Subscription code 60
"""

import logging
from restclients.uwnetid.subscription_60 import is_current_staff,\
    is_current_faculty
from endorsement.dao.user import get_netid_of_current_user


logger = logging.getLogger(__name__)


def is_valid_endorser():
    return is_staff() or is_faculty()


def is_staff():
    """
    Return True if the user is an UW staff currently
    """
    return is_current_staff(get_netid_of_current_user())


def is_faculty():
    """
    Return True if the user is an UW faculty currently
    """
    return is_current_faculty(get_netid_of_current_user())


def get_user_affiliations():
    entry = {'netid': get_netid_of_current_user(),
             'is_staff': None,
             'is_faculty': None
             }
    try:
        entry['is_staff'] = is_staff()
    except Exception:
        pass

    try:
        entry['is_faculty'] = is_faculty()
    except Exception:
        pass

    return json.dumps(entry)
