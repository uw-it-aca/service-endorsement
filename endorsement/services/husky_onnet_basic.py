# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
"""
Defines UW Husky OnNet service endorsement steps

To endorse Husky OnNet, the tools should:
   *  Add category XXX, status 1 for given endorsee
   *  Activate subscription 89: Husky OnNet - Extension

Shared netids are excluded from the service.
"""

from endorsement.services import EndorsementServiceBase
from endorsement.models import EndorsementRecord
from uw_uwnetid.models import Subscription


class EndorsementService(EndorsementServiceBase):
    @property
    def service_name(self):
        return 'husky-onnet-basic'

    @property
    def category_code(self):
        return EndorsementRecord.HUSKY_ONNET_EXT_PROVISIONEE

    @property
    def subscription_codes(self):
        return [Subscription.SUBS_CODE_HUSKY_ONNET_EXTENSION]

    @property
    def shared_params(self):
        return {
            'roles': [],
            'types': [],
            'excluded_categories': [],
            'allow_existing_endorsement': False
        }

    @property
    def service_renewal_statement(self):
        return ""

    @property
    def service_link(self):
        return ('https://itconnect.uw.edu/connect/'
                'uw-networks/about-husky-onnet/')
