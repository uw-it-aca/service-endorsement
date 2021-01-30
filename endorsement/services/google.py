from endorsement.services import EndorsementServiceBase
from endorsement.models import EndorsementRecord
from uw_uwnetid.models import Subscription

# Endorsed Google Suite implementation

#  The expected life cycle for a UW G Suite endorsement would be:
#    *  Add category 234, status 1 record for given endorsee
#    *  Activate subscription 144 for endorsee


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
    def service_link(self):
        return ('https://itconnect.uw.edu/connect/email/'
                'google-apps/getting-started/#activate')

    @property
    def shared_parameters(self):
        return {
            'supported_roles': ['owner', 'owner-admin'],
            'supported_types': ['shared', 'administrator', 'support'],
            'excluded_categories': [22],
        }
