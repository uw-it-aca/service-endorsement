import logging
from endorsement.views.rest_dispatch import RESTDispatch
from endorsement.models import Endorser, Endorsee, EndorsementRecord
from endorsement.services import get_endorsement_service
from endorsement.dao.notification import _create_expire_notice_message
from datetime import datetime, timedelta
import re
import uuid


logger = logging.getLogger(__name__)


class Notification(RESTDispatch):
    """
    Return Notification message based on data
    """
    def post(self, request, *args, **kwargs):
        notification = request.data.get('notification', None)
        endorsements = request.data.get('endorsees', {})

        endorser = Endorser(netid="endorser",
                            regid="1234567890abcdef1234567890abcdef",
                            display_name="Endorser",
                            is_valid=True)

        m = re.match(r'^warning_([1-4])$', notification)
        level = m.group(1)

        n = 1
        endorsed = []
        for netid, endorsements in endorsements.items():
            regid = uuid.uuid4().hex
            for endorsement in endorsements:
                s = get_endorsement_service(endorsement)
                endorsed.append(EndorsementRecord(
                    endorser=endorser,
                    endorsee=Endorsee(
                        netid=netid, regid=regid, display_name=n,
                        is_person=True, kerberos_active_permitted=True),
                    category_code=s.category_code,
                    reason='testing',
                    datetime_endorsed=(
                        datetime.today() - timedelta(days=365))))

        subject, text, html = _create_expire_notice_message(
            int(level), 365, endorsed)

        return self.json_response({
            'subject': subject,
            'text': text,
            'html': html
        })
