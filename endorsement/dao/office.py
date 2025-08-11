# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from endorsement.models import EndorsementRecord
from endorsement.services import get_endorsement_service
from endorsement.dao.user import get_endorsee_model
from endorsement.dao.access import get_accessor_model
from endorsement.dao.pws import get_endorsee_data
from endorsement.dao.gws import get_group_by_id
from endorsement.dao.uwnetid_subscriptions import (
    active_subscriptions_for_netid)
from endorsement.exceptions import UnrecognizedUWNetid, UnrecognizedGroupID


logger = logging.getLogger(__name__)


def is_office_permitted(netid):
    """
    test for office mailbox availability
    NOTE: test both o365 and o365student services
    """
    endorsee = get_endorsee_model(netid)
    o365 = get_endorsement_service('o365')
    o365_student = get_endorsement_service('o365student')

    records = EndorsementRecord.objects.get_endorsements_for_endorsee(
        endorsee, o365.category_code) |\
        EndorsementRecord.objects.get_endorsements_for_endorsee(
        endorsee, o365_student.category_code)

    for er in records:
        if er.datetime_endorsed and not er.datetime_expired:
            return True

    # if no endorsement record, check subscription_codes
    try:
        subscription_codes = list(set(
            o365.subscription_codes + o365_student.subscription_codes))
        return active_subscriptions_for_netid(netid, subscription_codes)
    except Exception as ex:
        logger.error("is_office_permitted: {}: {}".format(netid, ex))
        pass

    return False


def get_office_accessor(name):
    return get_accessor_model(name, validate_office_access)


def validate_office_access(name):
    """
    Validate uw netid or group

    Return tuple (display_name, is_shared_netid, is_group)
    """
    try:
        # get netid (personal or shared) data
        uwregid, display_name, email, is_person = get_endorsee_data(name)
        return display_name, not is_person, False
    except UnrecognizedUWNetid:
        return validate_group(name, None)


def validate_group(name, display_name):
    """
    Validate uw group

    Return tuple (display_name, is_shared_netid, is_group)
    """
    try:
        group = get_group_by_id(name)
        return group.name, False, True
    except UnrecognizedGroupID:
        raise
    except Exception as ex:
        logger.error(
            "validate_office_access get_group {}: {}".format(name, ex))
        raise
