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
    # properties required for shared netid service provisioning
    SHARED_SUPPORTED_ROLES = ['owner', 'owner-admin']
    SHARED_SUPPORTED_TYPES = ['shared', 'administrator', 'support']
#    SHARED_SUPPORTED_TYPES = ['administrator']
    SHARED_EXCLUDED_CATEGORIES = [Category.ALTID_SHARED_CLINICAL_1]
    SHARED_ALLOW_EXISTING = True

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
    def service_link(self):
        return ('https://itconnect.uw.edu/connect/email/'
                'google-apps/getting-started/#activate')
