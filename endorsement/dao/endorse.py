import logging
from django.utils import timezone
from django.conf import settings
from uw_uwnetid.subscription import (
    get_netid_subscriptions, update_subscription)
from endorsement.models.core import EndorsementRecord
from endorsement.exceptions import NoEndorsementException
from restclients_core.exceptions import DataFailureException


logger = logging.getLogger(__name__)


def store_endorsement(endorser, endorsee, subscription_code):
    update_subscription(
        endorsee.netid, 'permit', subscription_code,
        data_field={
            "expires": "<yyyy-mm-dd>",
            "category": 0,
            "dataValue": "Permit from endorsement.uw.edu",
            "replace": True,
            "sponsor": endorser.netid,
            "status": 0
        })

    logger.info('endorse %s for %s by %s' % (
        subscription_code, endorsee.netid, endorser.netid))

    en, created = EndorsementRecord.objects.update_or_create(
        endorser=endorser,
        subscription_code=subscription_code,
        endorsee=endorsee,
        defaults={'datetime_endorsed': timezone.now()})

    return en


def clear_endorsement(endorser, endorsee, subscription_code):
    updated = update_subscription(
        endorsee.netid, 'unpermit', subscription_code,
        data_field={
            "category": 0,
            "dataValue": "Permit from endorsement.uw.edu",
            "replace": True,
            "sponsor": endorser.netid,
            "status": 0
        })

    logger.info('endorse %s for %s by %s' % (
        subscription_code, endorsee.netid, endorser.netid))

    EndorsementRecord.objects.filter(
        endorser=endorser,
        subscription_code=subscription_code,
        endorsee=endorsee).delete()


def get_endorsement(endorser, endorsee, subscription_code):
    try:
        return EndorsementRecord.objects.get(
            endorser=endorser, endorsee=endorsee,
            subscription_code=subscription_code)
    except EndorsementRecord.DoesNotExist:
        raise NoEndorsementException()


def get_endorsements_by_endorser(endorser):
    return EndorsementRecord.objects.filter(endorser=endorser)


def get_endorsements_for_endorsee(endorsee):
    return EndorsementRecord.objects.filter(endorsee=endorsee)


def store_office365_endorsement(endorser, endorsee):
    return store_endorsement(
        endorser, endorsee, EndorsementRecord.OFFICE_365)


def store_office365_test_endorsement(endorser, endorsee):
    return store_endorsement(
        endorser, endorsee, EndorsementRecord.OFFICE_365_TEST)


def store_google_endorsement(endorser, endorsee):
    return store_endorsement(endorser, endorsee,
                             EndorsementRecord.GOOGLE_APPS)


def store_google_test_endorsement(endorser, endorsee):
    return store_endorsement(endorser, endorsee,
                             EndorsementRecord.GOOGLE_APPS_TEST)


def clear_office365_endorsement(endorser, endorsee):
    return clear_endorsement(
        endorser, endorsee, EndorsementRecord.OFFICE_365)


def clear_office365_test_endorsement(endorser, endorsee):
    return clear_endorsement(
        endorser, endorsee, EndorsementRecord.OFFICE_365_TEST)


def clear_google_endorsement(endorser, endorsee):
    return clear_endorsement(
        endorser, endorsee, EndorsementRecord.GOOGLE_APPS)


def clear_google_test_endorsement(endorser, endorsee):
    return clear_endorsement(
        endorser, endorsee, EndorsementRecord.GOOGLE_APPS_TEST)


def is_permitted(endorser, endorsee, subscription_code):
    active = False
    endorsed = False
    try:
        get_endorsement(endorser, endorsee, subscription_code)
        active = True
        endorsed = True
    except NoEndorsementException:
        endorsed = False
        try:
            get_netid_subscriptions(endorsee.netid, [subscription_code])
        except DataFailureException as ex:
            if ex.status == 404:
                active = False
                if settings.DEBUG:
                    e = EndorsementRecord.objects.filter(endorsee=endorsee)
                    active = len(e) < 0
            else:
                raise

    return active, endorsed


def is_office365_permitted(endorser, endorsee):
    return is_permitted(endorser, endorsee, EndorsementRecord.OFFICE_365)


def is_office365_test_permitted(endorser, endorsee):
    return is_permitted(endorser, endorsee, EndorsementRecord.OFFICE_365_TEST)


def is_google_permitted(endorser, endorsee):
    return is_permitted(endorser, endorsee, EndorsementRecord.GOOGLE_APPS)


def is_google_test_permitted(endorser, endorsee):
    return is_permitted(endorser, endorsee, EndorsementRecord.GOOGLE_APPS_TEST)
