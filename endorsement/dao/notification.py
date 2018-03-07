from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from endorsement.dao.pws import get_person
from endorsement.dao.endorse import record_mail_sent
from endorsement.dao import display_datetime
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


def create_endorsee_message(endorser, endorsement):
    sent_date = datetime.now()
    params = {
        "endorser_name": get_person(endorser.netid).display_name,
        "endorsed_date": display_datetime(sent_date)
    }

    services = ""
    try:
        if endorsement['o365']['endorsed']:
            services += "UW Microsoft"
            params['o365_endorsed'] = True
    except KeyError:
        params['o365_endorsed'] = False
        pass

    try:
        if endorsement['google']['endorsed']:
            if len(services):
                services += " and "

            services += "Google"
            params['google_endorsed'] = True
    except KeyError:
        params['google_endorsed'] = False
        pass

    params['both_endorsed'] = (params['google_endorsed'] and
                               params['o365_endorsed'])

    subject = "Your new access to %s tools" % (services)

    text_template = "email/endorsee.txt"
    html_template = "email/endorsee.html"

    return (subject,
            loader.render_to_string(text_template, params),
            loader.render_to_string(html_template, params))


def notify_endorsees(endorser, endorsements):
    sender = getattr(settings, "EMAIL_NOREPLY_ADDRESS",
                     "endorsement-noreply@example.com")

    for netid, endorsement in endorsements.items():
        endorsed = False
        for e in ['o365', 'google']:
            try:
                if endorsement[e]['endorsed']:
                    endorsed = True
            except KeyError:
                pass

        if not endorsed:
            continue

        (subject, text_body, html_body) = create_endorsee_message(
            endorser, endorsement)

        recipients = [endorsement['email']]

        message = EmailMultiAlternatives(
            subject, text_body, sender, recipients)
        message.attach_alternative(html_body, "text/html")

        try:
            message.send()
            record_mail_sent(endorser, endorsement)
            log_message = "Submission email sent"
        except Exception as ex:
            log_message = "Submission email failed: %s" % ex

        logger.info("%s, To: %s, Status: %s" % (
            log_message, endorsement['email'], subject))
