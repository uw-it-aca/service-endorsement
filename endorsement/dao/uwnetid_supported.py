"""
This module encapsulates the interactions with
the UW NeTID Subscription code 60
"""

import logging
import traceback
from uw_uwnetid.supported import get_supported_resources
from endorsement.dao import handel_err
from restclients_core.exceptions import DataFailureException

logger = logging.getLogger(__name__)


def get_supported_resources_for_netid(netid):
    """
    Return supported resources
    """
    try:
        supported = []
        for resource in get_supported_resources(netid):
            if resource.status != 'former':
                supported.append(resource)

        return supported
    except DataFailureException as ex:
        logger.error(
            'uw_uwnetid get_supported_resources({}) returned {}'.format(
                netid, ex.status))
    except Exception:
        handel_err(logger,
                   '{0} supported resources '.format(netid),
                   traceback.format_exc())

    return []
