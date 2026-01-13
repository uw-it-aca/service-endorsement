# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Office Mailbox Access lifecycle policy

Basic notions:
  * Intial and subsequent warnings are sent prior to expiration.
  * The expiration clock starts on the date of the first warning notice.
"""
from endorsement.models import AccessRecord
from endorsement.policy import PolicyBase
from endorsement.dao.access import revoke_access


class AccessPolicy(PolicyBase):
    @property
    def record_model(self):
        return AccessRecord

    @property
    def datetime_provisioned_key(self):
        return "datetime_granted"


def expire_office_access(gracetime, lifetime):
    """
    """
    for a in access_to_expire(gracetime, lifetime):
        revoke_access(a)
