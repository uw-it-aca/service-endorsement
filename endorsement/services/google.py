from endorsement.services import EndorsementService
from endorsement.models import EndorsementRecord
from uw_uwnetid.models import Subscription

# Endorsed Google Suite implementation

#  The expected life cycle for a UW G Suite endorsement would be:
#    *  Add category 234, status 1 record for given endorsee
#    *  Activate subscription 144 for endorsee

exported_service = 'GSuite'


class GSuite(EndorsementService):
    def service_name(self):
        return 'google'

    def category_code(self):
        return EndorsementRecord.GOOGLE_SUITE_ENDORSEE

    def subscription_codes(self):
        return [Subscription.SUBS_CODE_GOOGLE_APPS]

    def service_link(self):
        return ('https://itconnect.uw.edu/connect/email/'
                'google-apps/getting-started/#activate')

    def shared_parameters(self):
        return {
            'supported_roles': ['owner', 'owner-admin'],
            'supported_types': ['shared', 'administrator', 'support'],
            'excluded_categories': [22],
        }
