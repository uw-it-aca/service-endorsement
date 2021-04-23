# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
"""
Defines UW Canvas service endorsement steps

Valid Canvas endorsees are members of the UW group defined by
CANVAS_ACCESS_GROUP, default: "u_acadev_canvas_login-users"

The expected Canvas endorsement lifecycle is:
   *  Add category 236, status 1 record for given endorsee
   *  Activate subscription 79 for endorsee

Shared netids that are endorser owned and of type administrator
are allowed.
"""

from django.conf import settings
from endorsement.services import EndorsementServiceBase
from endorsement.models import EndorsementRecord
from endorsement.dao.gws import is_group_member
from endorsement.exceptions import NoEndorsementException
from uw_uwnetid.models import Subscription

CANVAS_ACCESS_GROUP = getattr(settings, "CANVAS_ACCESS_GROUP",
                              "u_acadev_canvas_login-users")


class EndorsementService(EndorsementServiceBase):
    @property
    def service_name(self):
        return 'canvas'

    @property
    def category_code(self):
        return EndorsementRecord.CANVAS_PROVISIONEE

    @property
    def subscription_codes(self):
        return [Subscription.SUBS_CODE_CANVAS_SPONSORED]

    @property
    def service_renewal_statement(self):
        return "Data in Canvas and Panopto accounts will not be deleted."

    @property
    def service_link(self):
        return 'https://itconnect.uw.edu/learn/tools/canvas/'

    @property
    def shared_params(self):
        return {
            'roles': ['owner', 'owner-admin'],
            'types': ['administrator'],
            'excluded_categories': [],
            'allow_existing_endorsement': False
        }

    def is_permitted(self, endorser, endorsee):
        try:
            self.get_endorsement(endorser, endorsee)
            return True, True
        except NoEndorsementException:
            return is_group_member(endorsee.netid, CANVAS_ACCESS_GROUP), False
