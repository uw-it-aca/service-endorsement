"""
Defines UW Office 365 service endorsement steps

To endorse O365, the tools should:
   *  Add category 235, status 1 for given endorsee
   *  Activate subscription 250 Future Office 365

Shared netids that are endorser owned and either shared, support, or
administrator are allowed as long as such shared netids do not have
the category: Category.ALTID_SHARED_CLINICAL_1 which are implicitly
permitted to Office 365
"""

from endorsement.services import EndorsementServiceBase
from endorsement.models import EndorsementRecord
from uw_uwnetid.models import Subscription, Category


class EndorsementService(EndorsementServiceBase):
    # properties required for shared netid service provisioning
    SHARED_SUPPORTED_ROLES = ['owner', 'owner-admin']
    SHARED_SUPPORTED_TYPES = ['shared', 'administrator', 'support']
    SHARED_EXCLUDED_CATEGORIES = [Category.ALTID_SHARED_CLINICAL_1]

    @property
    def service_name(self):
        return 'o365'

    @property
    def category_code(self):
        return EndorsementRecord.OFFICE_365_ENDORSEE

    @property
    def subscription_codes(self):
        return [Subscription.SUBS_CODE_FUTURE_OFFICE_365]

    @property
    def service_link(self):
        return ('https://itconnect.uw.edu/connect/'
                'productivity-platforms/uw-office-365/')
