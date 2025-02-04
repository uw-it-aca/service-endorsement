# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Shared Drive lifecycle policy

Basic notions:
  * Intial and subsequent warnings are sent prior to expiration.
  * The expiration clock starts on the date of the first warning notice.
"""

from endorsement.models import SharedDriveRecord
from endorsement.policy import PolicyBase


class SharedDrivePolicy(PolicyBase):
    @property
    def record_model(self):
        return SharedDriveRecord

    @property
    def datetime_provisioned_key(self):
        return "datetime_accepted"
