# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.dao.gws import get_group_admin_emails
from endorsement.util.email import uw_email_address
import logging


logger = logging.getLogger(__name__)


def get_accessor_email(access_record):
    """
    return an accessor's context (personal or group and email address[s])
    @exception: DataFailureException
    """
    accessor = access_record.accessor
    if accessor.is_group:
        # group accessor email goes to group admins
        return get_group_admin_emails(accessor.name)

    return [{
        'email': uw_email_address(accessor.name),
        'display_name': accessor.display_name
    }]
