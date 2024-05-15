# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from endorsement.exceptions import EmailFailureException
import logging


logger = logging.getLogger(__name__)
logging.captureWarnings(True)
EMAIL_REPLY_ADDRESS = getattr(settings, "EMAIL_REPLY_ADDRESS",
                              "provision-noreply@uw.edu")


def send_notification(recipients, subject, text_body, html_body, kind):
    sender = EMAIL_REPLY_ADDRESS
    message = EmailMultiAlternatives(
        subject, text_body, sender, recipients, headers={'Precedence': 'bulk'})
    message.attach_alternative(html_body, "text/html")
    try:
        message.send()
        logger.info(
            "{0} email sent To: {1}, Status: {2}"
            .format(kind, ','.join(recipients), subject))
    except Exception as ex:
        logger.error(
            "{0} email failed: {1}, To: {2}, Status: {3}"
            .format(kind, ex, ','.join(recipients), subject))
        raise EmailFailureException()
