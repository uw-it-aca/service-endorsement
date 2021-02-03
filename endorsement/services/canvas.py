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
from endorsement.dao.canvas import is_canvas_user, create_canvas_user
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
    def service_link(self):
        return 'https://itconnect.uw.edu/learn/tools/canvas/'

    @property
    def shared_parameters(self):
        return {
            'supported_roles': ['owner', 'owner-admin'],
            'supported_types': ['administrator'],
            'excluded_categories': None,
        }

    def is_permitted(self, endorser, endorsee):
        try:
            self.get_endorsement(endorser, endorsee)
            return True, True
        except NoEndorsementException:
            return is_group_member(endorsee.netid, CANVAS_ACCESS_GROUP), False

    def store_endorsement(self, endorser, endorsee, acted_as, reason):
        # make certain endorsee netid is provisioned as a Canvas user

        return super(EndorsementService, self).store_endorsement(
            endorser, endorsee, acted_as, reason)
