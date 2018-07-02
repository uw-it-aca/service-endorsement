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


def get_shared_netids_for_netid(netid):
    """
    Return supported resources
    """
    try:
        shared = []
        for supported in get_supported_resources(netid):
            if supported.is_shared_netid():
                shared.append(supported)

        return shared
    except DataFailureException as ex:
        if ex.status == 404:
            return []
    except Exception:
        return handel_err(logger,
                          '%s supported resources ' % netid,
                          traceback.format_exc())
