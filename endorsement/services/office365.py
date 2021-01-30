from endorsement.services import EndorsementService
from endorsement.models import EndorsementRecord
from uw_uwnetid.models import Subscription

# Endorsed Office 365 implementation

#  To endorse O365, the tools should:
#    *  Add category 235, status 1 for given endorsee
#    *  Activate subscription 59 Office 365 Pilot
#    *  Activate subscription 250 Future Office 365

exported_service = 'Office365'


class Office365(EndorsementService):
    def service_name(self):
        return 'o365'

    def category_code(self):
        return EndorsementRecord.OFFICE_365_ENDORSEE

    def subscription_codes(self):
        return [Subscription.SUBS_CODE_FUTURE_OFFICE_365]

    def service_link(self):
        return ('https://itconnect.uw.edu/connect/'
                'productivity-platforms/uw-office-365/')

    def shared_parameters(self):
        return {
            'supported_roles': ['owner', 'owner-admin'],
            'supported_types': ['shared', 'administrator', 'support'],
            'excluded_categories': [22]
        }
