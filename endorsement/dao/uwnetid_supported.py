"""
This module encapsulates the interactions with
the UW NeTID Subscription code 60
"""

import logging
import traceback
from uw_uwnetid.models import Category
from uw_uwnetid.supported import get_supported_resources
from endorsement.dao.uwnetid_categories import get_shared_categories_for_netid
from endorsement.dao import handel_err
from restclients_core.exceptions import DataFailureException


logger = logging.getLogger(__name__)


SUPPORTED_TYPES = [
    'shared',
    'administrator',
    'support'
]

EXCLUDED_CATEGORIES = [
    Category.ALTID_SHARED_CLINICAL_1
]


def get_shared_netids_for_netid(netid):
    """
    Return supported resources
    """
    # length based on
    # https://wiki.cac.washington.edu/display/SMW/UW+NetID+Namespace
    max_length = 29

    try:
        shared = []
        for supported in get_supported_resources(netid):
            if (supported.netid_type in SUPPORTED_TYPES and
                    len(supported.netid_type) <= max_length):
                shared.append(supported)

        return shared
    except DataFailureException as ex:
        logger.error(
            'uw_uwnetid get_supported_resources({}) returned {}'.format(
                netid, ex.status))
    except Exception:
        handel_err(logger,
                   '{0} supported resources '.format(netid),
                   traceback.format_exc())

    return []


def shared_netid_in_excluded_category(netid):
    for category in get_shared_categories_for_netid(netid):
        if (category.category_code in EXCLUDED_CATEGORIES and
                category.status_code != Category.STATUS_FORMER):
            return True

    return False
