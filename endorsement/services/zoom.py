# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
"""
Defines UW Zoom service endorsement steps

Valid Zoom endorsees are members of the UW group defined by
ZOOM_ACCESS_GROUP, default: "u_acadev_zoom_login-users"

The expected Zoom endorsement lifecycle is:
   *  Add category xxx, status 1 record for given endorsee
   *  Activate subscription xxx for endorsee

Shared netids are not allowed.
"""

from django.conf import settings
from endorsement.services import EndorsementServiceBase
from endorsement.models import EndorsementRecord
from endorsement.dao.gws import is_group_member
from endorsement.exceptions import NoEndorsementException
from uw_uwnetid.models import Subscription

ZOOM_ACCESS_GROUP = getattr(settings, "ZOOM_ACCESS_GROUP",
                            "u_acadev_zoom_login-users")


class EndorsementService(EndorsementServiceBase):
    @property
    def service_name(self):
        return 'zoom'

    @property
    def category_code(self):
        return EndorsementRecord.ZOOM_LICENSED_PROVISIONEE

    @property
    def subscription_codes(self):
        return [Subscription.SUBS_CODE_ZOOM_LICENSE_ACCESS]

    @property
    def shared_params(self):
        return {
            'roles': ['owner', 'owner-admin'],
            'types': ['administrator'],
            'excluded_categories': [],
            'allow_existing_endorsement': False
        }

    def valid_person_endorsee(self, endorsee):
        # personal netids ineligible
        return False

    @property
    def service_renewal_statement(self):
        return "Data accessible by UW Zoom accounts may be deleted."

    @property
    def service_link(self):
        return ("https://itconnect.uw.edu/connect/phones"
                "/conferencing/zoom-video-conferencing/")

    def is_permitted(self, endorser, endorsee):
        try:
            self.get_endorsement(endorser, endorsee)
            return True, True
        except NoEndorsementException:
            return is_group_member(endorsee.netid, ZOOM_ACCESS_GROUP), False
