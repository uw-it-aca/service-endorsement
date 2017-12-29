"""
This module encapsulates the interactions with the uw_pws,
provides Person information of the current user
"""

import logging
import traceback
from uw_pws import PWS
from restclients_core.exceptions import DataFailureException
from endorsement.exceptions import UnrecognizedUWNetid
from endorsement.util.log import log_exception


logger = logging.getLogger(__name__)
pws = PWS()


def get_entity(uwnetid):
    """
    Retrieve the Entity object for the given netid
    """
    try:
        return pws.get_entity_by_netid(uwnetid)
    except DataFailureException as ex:
        if ex.status == 404:
            raise UnrecognizedUWNetid(uwnetid)

        log_exception(logger,
                      '%s get_entity ' % uwnetid,
                      traceback.format_exc())
        raise


def get_person(uwnetid):
    """
    Retrieve the Person object for the given netid
    """
    return pws.get_person_by_netid(uwnetid)


def get_endorsee_data(uwnetid):
    """
    Return uwregid, display_anme retrieved from PWS/Entity for the
    given uwnetid.
    """
    entity = get_entity(uwnetid)
    return entity.uwregid, entity.display_name


def get_endorser_regid(uwnetid):
    """
    Get from PWS/person, make sure it is a valid personal uwnetid
    """
    return get_person(uwnetid).uwregid


def is_renamed_uwnetid(uwnetid):
    try:
        get_entity(uwnetid)
        return False
    except UnrecognizedUWNetid:
        return False
    except DataFailureException as ex:
        log_exception(logger,
                      '%s get_entity ' % uwnetid,
                      traceback.format_exc())
        return ex.status == 301
