from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorsee_email_model
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

    params['both_endorsed'] = (params['google_endorsed'] > 0 and
                               params['o365_endorsed'] > 0)

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
    for er in EndorsementRecord.objects.get_unendorsed_unnotified():
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
                    EndorsementRecord.objects.emailed(data['id'])

                logger.info("Submission email sent To: %s, Status: %s" % (
                    email, subject))
            except Exception as ex:
                logger.error(
                    "Submission email failed: %s, To: %s, Status: %s" % (
                        ex, email, subject))


def create_endorser_message(endorsed):
    sent_date = datetime.now()
    params = {
        "o365_endorsed": endorsed.get('o365', None),
        "google_endorsed": endorsed.get('google', None),
        "o365_endorsed_count": len(endorsed.get('o365', [])),
        "google_endorsed_count": len(endorsed.get('google', [])),
        "endorsed_date": display_datetime(sent_date)
    }

    params["endorsed_count"] = params["o365_endorsed_count"]
    params["endorsed_count"] += params["google_endorsed_count"]
    params['both_endorsed'] = (params['google_endorsed'] > 0 and
                               params['o365_endorsed'] > 0)

    subject = "Shared NetID access to %s%s%s" % (
        'UW Office 365' if params['o365_endorsed'] else '',
        ' and ' if (
            params['o365_endorsed'] and params['google_endorsed']) else '',
        'UW G Suite' if params['google_endorsed'] else '')

    text_template = "email/endorser.txt"
    html_template = "email/endorser.html"

    return (subject,
            loader.render_to_string(text_template, params),
            loader.render_to_string(html_template, params))


def notify_endorsers():
    sender = getattr(settings, "EMAIL_REPLY_ADDRESS",
                     "provision-noreply@uw.edu")
    endorsements = {}
    for er in EndorsementRecord.objects.get_endorsed_unnotified():
        # rely on @u forwarding for valid address
        email = "%s@uw.edu" % er.endorser.netid
        if email not in endorsements:
            endorsements[email] = {}

        data = {
            'netid': er.endorsee.netid,
            'id': er.id
        }

        if er.category_code == EndorsementRecord.OFFICE_365_ENDORSEE:
            if 'o365' in endorsements[email]:
                endorsements[email]['o365'].append(data)
            else:
                endorsements[email]['o365'] = [data]
        elif er.category_code == EndorsementRecord.GOOGLE_SUITE_ENDORSEE:
            if 'google' in endorsements[email]:
                endorsements[email]['google'].append(data)
            else:
                endorsements[email]['google'] = [data]

    for email, endorsed in endorsements.items():
        (subject, text_body, html_body) = create_endorser_message(endorsed)
        recipients = [email]
        message = EmailMultiAlternatives(
            subject, text_body, sender, recipients,
            headers={'Precedence': 'bulk'}
        )

        message.attach_alternative(html_body, "text/html")
        try:
            message.send()
            for svc in ['o365', 'google']:
                if svc in endorsed:
                    for id in [x['id'] for x in endorsed[svc]]:
                        EndorsementRecord.objects.emailed(id)

            logger.info(
                "Endorsement email sent To: %s, Status: %s" % (
                    email, subject))
        except Exception as ex:
            logger.error(
                "Endorsement email failed: %s, To: %s, Status: %s" % (
                    ex, email, subject))
