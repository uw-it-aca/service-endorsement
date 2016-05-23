"""
This module encapsulates the interactions with the restclients.pws,
provides Person information of the current user
"""

import logging
import sys
import traceback
from restclients.pws import PWS
from restclients.exceptions import InvalidNetID
from restclients.exceptions import DataFailureException
from endorsement.util.log_err import log_exception


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
        log_exception(logger,
                      '%s is_valid_endorsee ' % uwnetid,
                      traceback.format_exc())
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if isinstance(exc_value, InvalidNetID):
            return False
        if isinstance(exc_value, DataFailureException) and\
                exc_value.status == 404:
            return False
        raise
