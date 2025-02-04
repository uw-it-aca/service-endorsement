# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This module encapsulates the interactions with
the UW NeTID Shared Admin resource
"""

import logging
import traceback
from uw_uwnetid.admin import get_admins_for_shared_netid
from endorsement.dao import handel_err
from restclients_core.exceptions import DataFailureException


logger = logging.getLogger(__name__)


def get_owner_for_shared_netid(netid):
    """
    Return admin resources
    """
    try:
        for admin in get_admins_for_shared_netid(netid):
            if admin.is_owner():
                return admin.name
    except DataFailureException as ex:
        if ex.status == 404:
            pass
    except Exception:
        return handel_err(logger,
                          '{0} admin resources '.format(netid),
                          traceback.format_exc())

    return None
