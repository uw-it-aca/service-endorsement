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
    Return uwregid, display_name and email1 retrieved from PWS/Person for the
    given uwnetid.  Failing that, fetch entity
    """
    try:
        person = get_person(uwnetid)
        return person.uwregid, person.display_name, person.email1, True
    except DataFailureException as ex:
        if int(ex.status) == 404:
            entity = get_entity(uwnetid)
            return entity.uwregid, entity.display_name, None, False

        raise UnrecognizedUWNetid(uwnetid)


def get_endorser_data(uwnetid):
    """
    Get from PWS/person, make sure it is a valid personal uwnetid
    """
    try:
        person = get_person(uwnetid)
        return person.uwregid, person.display_name
    except DataFailureException as ex:
        if ex.status == 404:
            # v0.1 does not endorse non-person/shared uwnetids
            #     entity = get_entity(uwnetid)
            #     return entity.uwregid, entity.display_name, None
            raise UnrecognizedUWNetid(uwnetid)

        raise


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
