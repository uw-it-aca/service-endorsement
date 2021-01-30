from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils import timezone
from endorsement.models import EndorsementRecord
from endorsement.services import endorsement_services
from endorsement.dao.user import get_endorsee_email_model
from endorsement.dao import display_datetime
from endorsement.dao.endorse import clear_endorsement
from endorsement.exceptions import EmailFailureException
from endorsement.policy import (
    endorsements_to_warn, DEFAULT_ENDORSEMENT_LIFETIME, NOTICE_1_DAYS_PRIOR,
    NOTICE_2_DAYS_PRIOR, NOTICE_3_DAYS_PRIOR, NOTICE_4_DAYS_PRIOR)
import logging


logger = logging.getLogger(__name__)
logging.captureWarnings(True)


def _create_endorsee_message(endorser):
    sent_date = timezone.now()
    params = {
        "endorser_netid": endorser['netid'],
        "endorser_name": endorser['display_name'],
        "endorsed_date": display_datetime(sent_date),
        "services": endorser['services']
    }

    names = []
    for k, v in endorser['services'].items():
        names.append(v['name'])
        for service in endorsement_services():
            if k == service.service_name():
                v['service_link'] = service.service_link()

    subject = "Action Required: Your new access to {0}".format(
        '{} and {}'.format(', '.join(names[:-1]), names[-1]) if (
            len(names) > 1) else names[0])

    text_template = "email/endorsee.txt"
    html_template = "email/endorsee.html"

    return (subject,
            loader.render_to_string(text_template, params),
            loader.render_to_string(html_template, params))


def get_unendorsed_unnotified():
    endorsements = {}
    for er in EndorsementRecord.objects.get_unendorsed_unnotified():
        try:
            email = get_endorsee_email_model(er.endorsee, er.endorser).email
        except Exception as ex:
            logger.error("Notify get email failed: {0}, netid: {1}"
                         .format(ex, er.endorsee))
            continue

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
            if er.category_code == service.category_code():
                endorsements[email]['endorsers'][
                    er.endorser.netid]['services'][service.service_name()] = {
                        'code': service.category_code(),
                        'name': service.category_name(),
                        'id': er.id,
                        'accept_url': er.accept_url()
                    }
                break

    return endorsements


def notify_endorsees():
    sender = getattr(settings, "EMAIL_REPLY_ADDRESS",
                     "provision-noreply@uw.edu")

    endorsements = get_unendorsed_unnotified()

    for email, endorsers in endorsements.items():
        for endorser_netid, endorsers in endorsers['endorsers'].items():
            (subject, text_body, html_body) = _create_endorsee_message(
                endorsers)
            try:
                send_email(
                    sender, [email], subject, text_body, html_body, "Endorsee")
                for service, data in endorsers['services'].items():
                    EndorsementRecord.objects.emailed(data['id'])
            except EmailFailureException as ex:
                pass


def _create_endorser_message(endorsed):
    sent_date = timezone.now()
    params = {
        "endorsed_date": display_datetime(sent_date),
        "endorsed": {}
    }

    unique = {}
    for svc, endorsee_list in endorsed.items():
        for e in endorsee_list:
            service_name = e["name"]
            netid = e["netid"]
            unique[netid] = 1
            if service_name in params["endorsed"]:
                params["endorsed"][service_name]['netids'].append(netid)
            else:
                params["endorsed"][service_name] = {
                    'svc': svc,
                    'netids': [netid]
                }

    params["endorsees"] = list(unique.keys())

    services = []
    for s, v in params["endorsed"].items():
        services.append(s)
        for service in endorsement_services():
            if v['svc'] == service.service_name():
                v['service_link'] = service.service_link()

    subject = "Shared NetID access to {}".format(
        '{} and {}'.format(', '.join(services[:-1]), services[-1]) if (
            len(services) > 1) else services[0])

    text_template = "email/endorser.txt"
    html_template = "email/endorser.html"

    return (subject,
            loader.render_to_string(text_template, params),
            loader.render_to_string(html_template, params))


def get_endorsed_unnotified():
    endorsements = {}
    for er in EndorsementRecord.objects.get_endorsed_unnotified():
        # rely on @u forwarding for valid address
        email = "{0}@uw.edu".format(er.endorser.netid)
        if email not in endorsements:
            endorsements[email] = {}

        data = {
            'netid': er.endorsee.netid,
            'name': '',
            'id': er.id
        }

        for service in endorsement_services():
            service_tag = service.service_name()
            if er.category_code == service.category_code():
                data['name'] = service.category_name()
                if service_tag in endorsements[email]:
                    endorsements[email][service_tag].append(data)
                else:
                    endorsements[email][service_tag] = [data]

                break

    return endorsements


def notify_endorsers():
    sender = getattr(settings, "EMAIL_REPLY_ADDRESS",
                     "provision-noreply@uw.edu")
    endorsements = get_endorsed_unnotified()
    for email, endorsed in endorsements.items():
        (subject, text_body, html_body) = _create_endorser_message(endorsed)
        try:
            send_email(
                sender, [email], subject, text_body, html_body, "Endorser")
            for svc in [s.service_name() for s in endorsement_services()]:
                if svc in endorsed:
                    for id in [x['id'] for x in endorsed[svc]]:
                        EndorsementRecord.objects.emailed(id)
        except EmailFailureException as ex:
            pass


def _create_invalid_endorser_message(endorsements):
    params = {
        "endorsed": {}
    }

    services = {}
    for e in endorsements:
        params['endorser_netid'] = e.endorser.netid
        for service in endorsement_services():
            if e.category_code == service.category_code():
                services[service.category_name()] = 1
                try:
                    params['endorsed'][e.endorsee.netid].append(
                        service.category_name())
                except KeyError:
                    params['endorsed'][e.endorsee.netid] = [
                        service.category_name()]

    params['services'] = list(services.keys())

    subject = "{0}{1}".format(
        "Action Required: Services that you provisioned for other ",
        "UW NetIDs will be revoked soon")

    text_template = "email/invalid_endorser.txt"
    html_template = "email/invalid_endorser.html"

    return (subject,
            loader.render_to_string(text_template, params),
            loader.render_to_string(html_template, params))


def notify_invalid_endorser(endorser, endorsements):
    if not (endorsements and len(endorsements) > 0):
        return

    sent_date = timezone.now()
    email = "{0}@uw.edu".format(endorser.netid)
    sender = getattr(settings, "EMAIL_REPLY_ADDRESS",
                     "provision-noreply@uw.edu")
    (subject, text_body, html_body) = _create_invalid_endorser_message(
        endorsements)

    try:
        send_email(
            sender, [email], subject, text_body, html_body, "Invalid endorser")
        endorsements[0].endorser.datetime_emailed = sent_date
        endorsements[0].endorser.save()
        for endorsement in endorsements:
            clear_endorsement(endorsement)
    except EmailFailureException as ex:
        pass


def _create_expire_notice_message(notice_level, lifetime, endorsed):
    context = {
        'endorser': endorsed[0].endorser,
        'notice_time': globals()['NOTICE_{}_DAYS_PRIOR'.format(notice_level)],
        'lifetime': lifetime,
        'expiring': endorsed,
        'expiring_count': len(endorsed)
    }
    if notice_level < 4:
        subject = "{0}{1}".format(
            "Action Required: UW-IT services that you provisioned access to ",
            "for other UW NetIDs will expire soon")
        text_template = "email/notice_warning.txt"
        html_template = "email/notice_warning.html"
    else:
        subject = "{0}{1}".format(
            "Action Required: UW-IT services that you provisioned access to ",
            "for other UW NetIDs have expired")
        text_template = "email/notice_warning_final.txt"
        html_template = "email/notice_warning_final.html"

    return (subject,
            loader.render_to_string(text_template, context),
            loader.render_to_string(html_template, context))


def warn_endorsers(notice_level, lifetime):
    endorsements = endorsements_to_warn(notice_level, lifetime)

    if len(endorsements):
        endorsers = {}
        for e in endorsements:
            endorsers[e.endorser.id] = 1

        for endorser in endorsers.keys():
            endorsed = endorsements.filter(endorser=endorser)

            sent_date = timezone.now()
            email = "{0}@uw.edu".format(endorsed[0].endorser.netid)
            sender = getattr(settings, "EMAIL_REPLY_ADDRESS",
                             "provision-noreply@uw.edu")

            try:
                (subject,
                 text_body,
                 html_body) = _create_expire_notice_message(
                    notice_level, lifetime, endorsed)
                send_email(
                    sender, [email], subject, text_body, html_body,
                    "Invalid endorser")

                sent_date = {
                    'datetime_notice_{}_emailed'.format(
                        notice_level): timezone.now()
                }
                endorsed.update(**sent_date)
            except EmailFailureException as ex:
                pass


def _create_warn_shared_owner_message(owner_netid, endorsements):
    context = {
        'endorser': owner_netid,
        'lifetime': DEFAULT_ENDORSEMENT_LIFETIME,
        'notice_time': NOTICE_1_DAYS_PRIOR,
        'expiring': endorsements,
        'expiring_count': len(endorsements)
    }

    subject = "{0}{1}".format(
        "Action Required: UW-IT services provisioned for Shared ",
        "UW NetIDs you own have expired")
    text_template = "email/notice_new_shared_warning.txt"
    html_template = "email/notice_new_shared_warning.html"

    return (subject,
            loader.render_to_string(text_template, context),
            loader.render_to_string(html_template, context))


def warn_new_shared_netid_owner(new_owner, endorsements):
    if not (endorsements and len(endorsements) > 0):
        return

    sent_date = timezone.now()
    email = "{0}@uw.edu".format(new_owner.netid)
    sender = getattr(settings, "EMAIL_REPLY_ADDRESS",
                     "provision-noreply@uw.edu")
    (subject, text_body, html_body) = _create_warn_shared_owner_message(
        new_owner, endorsements)

    send_email(
        sender, [email], subject, text_body, html_body,
        "Shared Netid Owner")

    for endorsement in endorsements:
        endorsement.datetime_notice_1_emailed = sent_date
        endorsement.save()


def send_email(sender, recipients, subject, text_body, html_body, kind):
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
