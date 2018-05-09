from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorsee_email_model
from endorsement.dao.endorse import record_mail_sent
from endorsement.dao import display_datetime
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


def create_endorsee_message(endorser):
    sent_date = datetime.now()
    params = {
        "endorser_netid": endorser['netid'],
        "endorser_name": endorser['display_name'],
        "endorsed_date": display_datetime(sent_date)
    }

    services = ""
    try:
        params['o365_accept_url'] =\
            endorser['services']['o365']['accept_url']
        services += "UW Microsoft"
        params['o365_endorsed'] = True
    except KeyError:
        params['o365_endorsed'] = False

    try:
        params['google_accept_url'] =\
            endorser['services']['google']['accept_url']

        if len(services):
            services += " and "

        services += "Google"
        params['google_endorsed'] = True
    except KeyError:
        params['google_endorsed'] = False

    params['both_endorsed'] = (params['google_endorsed'] and
                               params['o365_endorsed'])

    subject = "Your new access to %s tools" % (services)

    text_template = "email/endorsee.txt"
    html_template = "email/endorsee.html"

    return (subject,
            loader.render_to_string(text_template, params),
            loader.render_to_string(html_template, params))


def notify_endorsees():
    sender = getattr(settings, "EMAIL_REPLY_ADDRESS",
                     "provision-noreply@uw.edu")

    endorsements = {}
    for er in EndorsementRecord.objects.filter(
            datetime_emailed__isnull=True,
            datetime_endorsed__isnull=True):
        try:
            email = get_endorsee_email_model(
                er.endorsee, er.endorser).email
        except Exception as ex:
            logger.error("Notify get email failed: %s, netid: %s" % (
                ex, er.endorsee))

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

        s = endorsements[email]['endorsers'][er.endorser.netid]['services']
        if er.category_code == EndorsementRecord.OFFICE_365_ENDORSEE:
            s['o365'] = {
                'id': er.id,
                'accept_url': er.accept_url()
            }

        if er.category_code == EndorsementRecord.GOOGLE_SUITE_ENDORSEE:
            s['google'] = {
                'id': er.id,
                'accept_url': er.accept_url()
            }

        endorsements[email]['endorsers'][er.endorser.netid]['services'] = s

    for email, endorsers in endorsements.items():
        for endorser_netid, endorsers in endorsers['endorsers'].items():
            (subject, text_body, html_body) = create_endorsee_message(
                endorsers)

            recipients = [email]
            message = EmailMultiAlternatives(
                subject, text_body, sender, recipients,
                headers={'Precedence': 'bulk'}
            )
            message.attach_alternative(html_body, "text/html")

            try:
                message.send()

                for service, data in endorsers['services'].items():
                    record_mail_sent(data['id'])

                logger.info("Submission email sent To: %s, Status: %s" % (
                    email, subject))
            except Exception as ex:
                logger.error(
                    "Submission email failed: %s, To: %s, Status: %s" % (
                        ex, email, subject))
