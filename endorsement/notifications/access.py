# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.models import AccessRecord
from endorsement.policy.access import AccessPolicy
from endorsement.util.email import uw_email_address
from endorsement.dao.notification import send_notification
from endorsement.dao.accessors import get_accessor_email
from endorsement.exceptions import EmailFailureException
from django.template import loader, Template, Context
from django.utils import timezone
import logging


logger = logging.getLogger(__name__)


def _email_template(template_name):
    return "email/access/{}".format(template_name)


def notify_accessors():
    for ar in AccessRecord.objects.get_unnotified_accessors():
        try:
            emails = get_accessor_email(ar)

            (subject, text_body, html_body) = _create_accessor_message(
                ar, emails)

            recipients = []
            for addr in emails:
                recipients.append(addr['email'])

            send_notification(
                recipients, subject, text_body, html_body, "Accessor")

            ar.emailed()
        except EmailFailureException as ex:
            logger.error("Accessor notification failed: {}".format(ex))
        except Exception as ex:
            logger.error("Notify get email failed: {0}, netid: {1}"
                         .format(ex, ar.accessor))


def _create_accessor_message(access_record, emails):
    subject = "Delegated Mailbox Access to {}".format(
        access_record.accessee.netid)

    params = {
        'record': access_record,
        'emails': emails
    }

    text_template = _email_template("accessor.txt")
    html_template = _email_template("accessor.html")

    return (subject,
            loader.render_to_string(text_template, params),
            loader.render_to_string(html_template, params))


def _create_accessee_expiration_notice(notice_level, access, policy):
    context = {
        'access': access,
        'lifetime': policy.lifetime,
        'notice_time': policy.days_till_expiration(notice_level)
    }

    if notice_level < 4:
        subject = ("Action Required: Office 365 Shared Mailbox "
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


def warn_accessees(notice_level):
    policy = AccessPolicy()
    drives = policy.records_to_warn(notice_level)

    for drive in drives:
        try:
            email = [uw_email_address(drive.accessee.netid)]
            (subject,
             text_body,
             html_body) = _create_accessee_expiration_notice(
                 notice_level, drive, policy)
            send_notification(
                email, subject, text_body, html_body,
                "Mailbox Access Warning")

            sent_date = {
                'datetime_notice_{}_emailed'.format(
                    notice_level): timezone.now()
            }
            drives.update(**sent_date)
        except EmailFailureException as ex:
            pass
