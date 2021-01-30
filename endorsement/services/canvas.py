from endorsement.services import EndorsementService
from endorsement.models import EndorsementRecord
from endorsement.dao.gws import has_canvas_access
from endorsement.exceptions import NoEndorsementException
from uw_uwnetid.models import Subscription

# Endorsed Canvas LMS implementation

#  The expected life cycle for a Canvas endorsement would be:
#    *  Add category 236, status 1 record for given endorsee
#    *  Activate subscription 79 for endorsee

exported_service = 'Canvas'


class Canvas(EndorsementService):
    def service_name(self):
        return 'canvas'

    def category_code(self):
        return EndorsementRecord.CANVAS_PROVISIONEE

    def subscription_codes(self):
        return [Subscription.SUBS_CODE_CANVAS_SPONSORED]

    def service_link(self):
        return 'https://itconnect.uw.edu/learn/tools/canvas/'

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
            return has_canvas_access(endorsee.netid), False
