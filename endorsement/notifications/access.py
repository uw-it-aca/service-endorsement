# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.models import AccessRecord
from endorsement.dao.notification import send_notification
from endorsement.dao.accessors import get_accessor_email
from endorsement.exceptions import EmailFailureException
from django.template import loader, Template, Context
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


