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
from endorsement.services import service_supports_shared


logger = logging.getLogger(__name__)


def get_shared_netids_for_netid(netid):
    """
    Return supported resources
    """

    try:
        return get_supported_resources(netid)
    except DataFailureException as ex:
        logger.error(
            'uw_uwnetid get_supported_resources({}) returned {}'.format(
                netid, ex.status))
    except Exception:
        handel_err(logger,
                   '{0} supported resources '.format(netid),
                   traceback.format_exc())

    return []


def valid_supported_netid(netid, service):
    for shared in get_shared_netids_for_netid(netid):
        if shared.name == netid and valid_shared_resource(shared, service):
            return True

    return False


def valid_supported_resource(shared, service):
    # length based on
    # https://wiki.cac.washington.edu/display/SMW/UW+NetID+Namespace
    max_length = 29

    return (service_supports_shared(service) and
            shared.netid_type in service['shared_supported_types'] and
            len(shared.netid_type) <= max_length and
            not shared_netid_category_exclusion(shared, service))


def shared_netid_category_exclusion(shared, service):
    if (service['shared_excluded_categories'] is not None and
            len(service['shared_excluded_categories']) > 0):
        for category in get_shared_categories_for_netid(shared.name):
            if (category.category_code in service[
                    'shared_excluded_categories'] and
                    category.status_code != Category.STATUS_FORMER):
                return True

    return False
