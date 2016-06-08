"""
This module encapsulates the interactions with the restclients.pws,
provides Person information of the current user
"""

import logging
import traceback
from restclients.pws import PWS
from endorsement.dao import handel_err


logger = logging.getLogger(__name__)
pws = PWS()


def _get_person(uwnetid):
    """
    Retrieve the person data using the given netid
    """
    return pws.get_person_by_netid(uwnetid)


def get_regid(uwnetid):
    return _get_person(uwnetid).uwregid


def is_valid_endorsee(uwnetid):
    """
    Return True if the user is in PersonReg currently
    """
    try:
        return _get_person(uwnetid) is not None
    except Exception:
        return handel_err(logger,
                          '%s pws.get_person_by_netid ' % uwnetid,
                          traceback.format_exc())
