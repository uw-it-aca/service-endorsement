"""
This module encapsulates the interactions with the restclients.pws,
provides Person information of the current user
"""

import logging
from django.conf import settings
from restclients.pws import PWS
from endorsement.dao.user import get_netid_of_current_user


logger = logging.getLogger(__name__)
pws = PWS()


def _get_person_of_current_user():
    """
    Retrieve the person data using the netid of the current user
    """
    return pws.get_person_by_netid(get_netid_of_current_user())


def get_regid_of_current_user():
    """
    Return the regid of the current user
    """
    return _get_person_of_current_user().uwregid


def is_staff():
    """
    Return True if the user is an UW staff currently
    """
    return _get_person_of_current_user().is_staff


def is_faculty():
    """
    Return True if the user is an UW faculty currently
    """
    return _get_person_of_current_user().is_faculty


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
