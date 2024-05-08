# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.dao.notification import send_notification
from endorsement.models import SharedDriveRecord
from endorsement.dao.user import get_endorsee_email_model
from endorsement.dao import display_datetime
from endorsement.policy.shared_drive import (
    shared_drives_to_warn, expiration_warning,
    DEFAULT_SHARED_DRIVE_LIFETIME)
from endorsement.util.email import uw_email_address
from endorsement.exceptions import EmailFailureException
from django.template import loader, Template, Context
from django.utils import timezone
import re
import logging


logger = logging.getLogger(__name__)


def _email_template(template_name):
    return "email/shared_drive/{}".format(template_name)


def _create_notification_expiration_notice(notice_level, lifetime, drive):
    context = {
        'drive': drive,
        'acceptor': drive.acceptor,
        'lifetime': lifetime,
        'notice_time': expiration_warning(notice_level)
    }

    if notice_level < 4:
        subject = ("Action Required: Shared Drive "
                   "service will expire soon")
        text_template = _email_template("notice_warning.txt")
        html_template = _email_template("notice_warning.html")
    else:
        subject = "Action Required: Shared Drive services have expired"
        text_template = _email_template("notice_warning_final.txt")
        html_template = _email_template("notice_warning_final.html")

    return (subject,
            loader.render_to_string(text_template, context),
            loader.render_to_string(html_template, context))


def warn_members(notice_level):
    drives = shared_drives_to_warn(notice_level)
    lifetime = DEFAULT_SHARED_DRIVE_LIFETIME

    for drive in drives:
        try:
            members = [uw_email_address(netid) for (
                netid) in drive.shared_drive.get_members()]
            (subject,
             text_body,
             html_body) = _create_expire_notice_message(
                 notice_level, lifetime, drive)
            send_notification(
                members, subject, text_body, html_body,
                "Shared Drive Warning")

            sent_date = {
                'datetime_notice_{}_emailed'.format(
                    notice_level): timezone.now()
            }
            drives.update(**sent_date)
        except EmailFailureException as ex:
            pass
