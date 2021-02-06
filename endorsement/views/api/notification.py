import logging
from endorsement.views.rest_dispatch import RESTDispatch
from endorsement.models import Endorser, Endorsee, EndorsementRecord
from endorsement.services import endorsement_services, get_endorsement_service
from endorsement.dao.notification import (
    _get_endorsed_unnotified,
    _create_expire_notice_message,
    _create_endorsee_message, _create_endorser_message)
from datetime import datetime, timedelta
import re
import uuid
import random
import traceback


logger = logging.getLogger(__name__)


class Notification(RESTDispatch):
    """
    Return Notification message based on data
    """
    def post(self, request, *args, **kwargs):
        notification = request.data.get('notification', None)
        endorsements = request.data.get('endorsees', {})

        warning_level = None
        m = re.match(r'^warning_([1-4])$', notification)
        if m:
            warning_level = int(m.group(1))

        endorser = Endorser(netid="jfaculty",
                            regid="1234567890abcdef1234567890abcdef",
                            display_name="Dr J Faculty",
                            is_valid=True)

        # gather endorsments
        n = 1
        endorsed = []
        for netid, endorsements in endorsements.items():
            regid = uuid.uuid4().hex
            for endorsement in endorsements:
                s = get_endorsement_service(endorsement)
                record = EndorsementRecord(
                    endorser=endorser,
                    endorsee=Endorsee(
                        netid=netid, regid=regid, display_name=n,
                        is_person=True, kerberos_active_permitted=True),
                    category_code=s.category_code,
                    reason='testing',
                    accept_salt="".join(
                        ["0123456789abcdef"[
                            random.randint(0, 0xF)] for _ in range(32)]))

                if warning_level:
                    record.datetime_endorsed = (
                        datetime.today() - timedelta(days=(
                            365 if warning_level == 4 else
                            (365 - 7) if warning_level == 3 else
                            (365 - 30) if warning_level == 2 else
                            (365 - 90))))

                if notification == 'endorsee':
                    record.accept_id = record.get_accept_id(netid)
                    print("ACCEPT ID: {}".format(record.accept_id))

                endorsed.append(record)

        if not endorsed:
            return self.error_response(
                405, "No endorsement services specified")

        try:
            if warning_level:
                subject, text, html = _create_expire_notice_message(
                    warning_level, 365, endorsed)
            elif notification == 'endorsee':
                unendorsed = _get_unendorsed_unnotified(endorsed)
                for email, endorsers in unendorsed.items():
                    for netid, endorser in endorsers['endorsers'].items():
                        subject, text, html = _create_endorsee_message(
                            endorser)
                        break
            elif notification == 'endorser':
                endorsed_unnotified = _get_endorsed_unnotified(endorsed)
                for email, endorsed in endorsed_unnotified.items():
                    subject, text, html = _create_endorser_message(endorsed)
                    break
            else:
                return self.error_response(
                    405, "unknown notification: {}".format(notification))

            return self.json_response({
                'subject': subject,
                'text': text,
                'html': html
            })
        except Exception as ex:
            return self.error_response(500, "{}".format(
                traceback.format_exc()))


# mimic function in dao.notification
def _get_unendorsed_unnotified(unendorsed):
    endorsements = {}
    for er in unendorsed:
        email = "{}@blackhole.uw.edu".format(er.endorsee.netid)
        print("EMAIL: {}".format(email))

        if email not in endorsements:
            endorsements[email] = {
                'endorsers': {}
            }

        if (er.endorser.netid not in endorsements[email]['endorsers']):
            endorsements[email]['endorsers'][er.endorser.netid] = {
                'netid': er.endorser.netid,
                'display_name': er.endorser.display_name,
                'services': {}
            }

        for service in endorsement_services():
            if er.category_code == service.category_code:
                endorsements[email]['endorsers'][
                    er.endorser.netid]['services'][service.service_name] = {
                        'code': service.category_code,
                        'name': service.category_name,
                        'id': er.id,
                        'accept_url': er.accept_url()
                    }
                break

    return endorsements
