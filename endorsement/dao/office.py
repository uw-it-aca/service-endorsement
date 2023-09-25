# Copyright 2023 UW-IT, University of Washington
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
    """
    o365 = get_endorsement_service('o365')
    endorsee = get_endorsee_model(netid)
    for er in EndorsementRecord.objects.get_endorsements_for_endorsee(
            endorsee, o365.category_code):
        if er.datetime_endorsed and not er.datetime_expired:
            return True

    # if no endorsement record, check subscription_codes
    try:
        return active_subscriptions_for_netid(netid, o365.subscription_codes)
    except Exception as ex:
        logger.error("is_office_permitted: {}: {}".format(netid, ex))
        pass

    return False


def get_office_accessor(name):
    return get_accessor_model(name, validate_office_access)


def validate_office_access(name):
    try:
        # get netid (personal/shared) data
        uwregid, display_name, email, is_person = get_endorsee_data(name)
        if is_person:
            return display_name, False, False
        elif '_' not in name:
            return display_name, True, False

        return validate_group(name, display_name)
    except UnrecognizedUWNetid:
        return validate_group(name, None)


def validate_group(name, display_name):
    try:
        group = get_group_by_id(name)
        return group.name, False, True
    except UnrecognizedGroupID:
        raise
    except Exception as ex:
        logger.error(
            "validate_office_access get_group {}: {}".format(name, ex))
        raise
