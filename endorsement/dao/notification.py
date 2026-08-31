# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives

from endorsement.dao.gws import get_effective_member_emails
from endorsement.exceptions import EmailFailureException

logger = logging.getLogger(__name__)
logging.captureWarnings(True)
EMAIL_REPLY_ADDRESS = getattr(settings, "EMAIL_REPLY_ADDRESS",
                              "provision-noreply@uw.edu")


def send_notification(recipients, subject, text_body, html_body=None, kind=''):
    sender = EMAIL_REPLY_ADDRESS
    if html_body:
        message = EmailMultiAlternatives(
            subject, text_body, sender, recipients,
            headers={'Precedence': 'bulk'})
        message.attach_alternative(html_body, "text/html")
    else:
        message = EmailMessage(subject, text_body, sender, recipients)

    log_recipients = f"To: {','.join(recipients)}, Status: {subject}"

    try:
        message.send()
        logger.info(f"{kind} email sent {log_recipients}")
    except Exception as ex:
        logger.error(f"{kind} email failed: {ex}, {log_recipients}")
        raise EmailFailureException()


def send_admin_notification(subject, text_body):
    try:
        admins = [m['email'] for m in get_effective_member_emails(
            settings.PROVISION_ADMIN_GROUP)]
        send_notification(admins, subject, text_body, kind="Admin")
    except EmailFailureException:
        pass
