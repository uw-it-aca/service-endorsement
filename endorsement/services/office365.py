from endorsement.services import EndorsementServiceBase
from endorsement.models import EndorsementRecord
from uw_uwnetid.models import Subscription

# Endorsed Office 365 implementation

#  To endorse O365, the tools should:
#    *  Add category 235, status 1 for given endorsee
#    *  Activate subscription 59 Office 365 Pilot
#    *  Activate subscription 250 Future Office 365


class EndorsementService(EndorsementServiceBase):
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

    @property
    def shared_parameters(self):
        return {
            'supported_roles': ['owner', 'owner-admin'],
            'supported_types': ['shared', 'administrator', 'support'],
            'excluded_categories': [22]
        }
