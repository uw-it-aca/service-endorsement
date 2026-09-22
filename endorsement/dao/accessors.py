# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging

from endorsement.dao.gws import get_group_admin_emails
from endorsement.exceptions import UnrecognizedGroupID
from endorsement.util.email import uw_email_address

logger = logging.getLogger(__name__)


def get_accessor_email(access_record):
    """
    return an accessor's context (personal or group and email address[s])
    @exception: DataFailureException
    """
    accessor = access_record.accessor
    if accessor.is_group:
        # group accessor email goes to group admins
        try:
            return get_group_admin_emails(accessor.name)
        except UnrecognizedGroupID:
            logger.error(
                f"get_accessor_email: unrecognized group: {accessor.name}")
            return []

    return [{
        'email': uw_email_address(accessor.name),
        'display_name': accessor.display_name
    }]
