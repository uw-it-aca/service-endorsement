# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
"""
Defines UW Google Suite service endorsement steps

The expected life cycle for a UW G Suite endorsement would be:
   *  Add category 234, status 1 record for given endorsee
   *  Activate subscription 144 for endorsee

Shared netids that are endorser owned and either shared, support, or
administrator are allowed as long as such shared netids do not have
the category: Category.ALTID_SHARED_CLINICAL_1 which are implicitly
permitted to the appropriate collaboration service
"""

from endorsement.services import EndorsementServiceBase
from endorsement.models import EndorsementRecord
from uw_uwnetid.models import Subscription, Category


class EndorsementService(EndorsementServiceBase):
    @property
    def service_name(self):
        return 'google'

    @property
    def category_code(self):
        return EndorsementRecord.GOOGLE_SUITE_ENDORSEE

    @property
    def subscription_codes(self):
        return [Subscription.SUBS_CODE_GOOGLE_APPS]

    @property
    def shared_params(self):
        return {
            'roles': ['owner', 'owner-admin'],
            'types': ['administrator'],
            'allow_existing_endorsement': True,
        }

    @property
    def service_renewal_statement(self):
        return ("Data in {{ service_names_google_o365 }} "
                "account{{service_names_count|pluralize}} may be deleted.")

    @property
    def service_link(self):
        return ('https://itconnect.uw.edu/connect/email/'
                'google-apps/getting-started/#activate')
