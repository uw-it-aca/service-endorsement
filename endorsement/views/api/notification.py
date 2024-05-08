# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from endorsement.views.rest_dispatch import RESTDispatch
from endorsement.models import (
    Endorser, Endorsee, EndorsementRecord,
    Accessor, Accessee, AccessRight, AccessRecord,
    Member, Role, SharedDriveMember, SharedDrive,
    SharedDriveQuota, SharedDriveRecord, SharedDriveRecord)
from endorsement.services import endorsement_services, get_endorsement_service
from endorsement.util.auth import SupportGroupAuthentication
from endorsement.notifications.endorsement import (
    _get_endorsed_unnotified,
    _create_expire_notice_message,
    _create_endorsee_message, _create_endorser_message,
    _create_warn_shared_owner_message)
from endorsement.notifications.access import (
    _create_accessor_message)
from endorsement.notifications.shared_drive import (
    _create_notification_expiration_notice)
from endorsement.dao.accessors import get_accessor_email
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
    authentication_classes = [SupportGroupAuthentication]

    def post(self, request, *args, **kwargs):
        notice_type = request.data.get('type', None)

        if notice_type == 'service':
            return self._service_notification(request)
        elif notice_type == 'access':
            return self._access_notification(request)
        elif notice_type == 'shared_drive':
            return self._shared_drive_notification(request)

        return self.error_response(400, "Incomplete or unknown notification.")

    def _service_notification(self, request):
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
                    reason='An example reason',
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
            elif notification == 'new_shared':
                subject, text, html = _create_warn_shared_owner_message(
                    endorser, endorsed)
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

    def _access_notification(self, request):
        notification = request.data.get('notification', None)
        right = request.data.get('right', "")
        right_name = request.data.get('right_name', "")
        is_shared_netid = request.data.get('is_shared_netid', False)
        is_group = request.data.get('is_group', False)

        accessee = Accessee(netid="jfaculty",
                            regid="1234567890abcdef1234567890abcdef",
                            display_name="Dr J Faculty",
                            is_valid=True)
        accessor = Accessor(
            name="u_javerage_admin" if is_group else "javerage",
            display_name="Jamie Average", is_valid=True,
            is_shared_netid=is_shared_netid, is_group=is_group)

        if right == "":
            return self.error_response(400, "Unknown notification.")

        try:
            access_right = AccessRight.objects.get(name=right)
        except AccessRight.DoesNotExist:
            return self.error_response(400, "Unknown access right.")

        ar = AccessRecord(
            accessee=accessee, accessor=accessor, access_right=access_right)

        if notification == 'delegate':
            (subject, text_body, html_body) = _create_accessor_message(
                ar, get_accessor_email(ar))
        else:
            return self.error_response(400, "Unknown notification.")

        return self.json_response({
            'subject': subject,
            'text': text_body,
            'html': html_body
        })

    def _shared_drive_notification(self, request):
        notification = request.data.get('notification', None)

        warning_level = None
        m = re.match(r'^warning_([1-4])$', notification)
        if m:
            warning_level = int(m.group(1))

        record = SharedDriveRecord.objects.filter(
            is_deleted__isnull=True).first()

        if warning_level:
            subject, text, html = _create_notification_expiration_notice(
                warning_level, 365, record)
        else:
            return self.error_response(400, "Unknown notification.")

        return self.json_response({
            'subject': subject,
            'text': text,
            'html': html
        })


# mimic function in dao.notification
def _get_unendorsed_unnotified(unendorsed):
    endorsements = {}
    for er in unendorsed:
        email = "{}@blackhole.uw.edu".format(er.endorsee.netid)

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
