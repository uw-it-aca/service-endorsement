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
    supported_types = ['shared', 'administrator', 'support']
    # length based on
    # https://wiki.cac.washington.edu/display/SMW/UW+NetID+Namespace
    max_length = 29

    try:
        shared = []
        for supported in get_supported_resources(netid):
            if (supported.netid_type in supported_types and
                    len(supported.netid_type) <= max_length):
                shared.append(supported)

        return shared
    except DataFailureException as ex:
        if ex.status == 404:
            return []
    except Exception:
        handel_err(logger,
                   '{0} supported resources '.format(netid),
                   traceback.format_exc()):
        return []
