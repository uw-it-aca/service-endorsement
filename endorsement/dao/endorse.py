import logging
from django.utils import timezone
from django.conf import settings
from uw_uwnetid.models import Subscription, Category
from uw_uwnetid.category import update_catagory
from uw_uwnetid.subscription import (
    get_netid_subscriptions, update_subscription)
from endorsement.dao.user import get_endorsee_model
from endorsement.models import EndorsementRecord
from endorsement.exceptions import (
    NoEndorsementException, CategoryFailureException,
    SubscriptionFailureException)
from restclients_core.exceptions import DataFailureException


logger = logging.getLogger(__name__)


def store_endorsement(endorser, endorsee, reason, category_code):
    logger.info('activate category %s for %s because %s by %s' % (
        category_code, endorsee.netid, reason, endorser.netid))

    en, created = EndorsementRecord.objects.update_or_create(
        endorser=endorser,
        category_code=category_code,
        reason=reason,
        endorsee=endorsee,
        defaults={'datetime_endorsed': timezone.now()})

    return en


def clear_endorsement(endorser, endorsee, category_code):
    logger.info('former category %s for %s by %s' % (
        category_code, endorsee.netid, endorser.netid))

    EndorsementRecord.objects.filter(
        endorser=endorser,
        category_code=category_code,
        endorsee=endorsee).delete()


def get_endorsement(endorser, endorsee, category_code):
    try:
        return EndorsementRecord.objects.get(
            endorser=endorser, endorsee=endorsee,
            category_code=category_code)
    except EndorsementRecord.DoesNotExist:
        raise NoEndorsementException()


def get_endorsements_by_endorser(endorser):
    return EndorsementRecord.objects.filter(endorser=endorser)


def get_endorsements_for_endorsee(endorsee):
    return EndorsementRecord.objects.filter(endorsee=endorsee)


def store_office365_endorsement(endorser, endorsee, reason):
    """
    To endorse O365, the tools should:
      *  Add category 235, status 1 for given endorsee
      *  Activate subscription 59 Office 365 Pilot
      *  Activate subscription 251 Office 365 Addee
    """
    _activate_category(endorsee.netid, Category.OFFICE_365_ENDORSEE)
    _activate_subscriptions(endorsee.netid, endorser.netid,
                            [
                                Subscription.SUBS_OFFICE_356_PILOT,
                                Subscription.SUBS_CODE_OFFICE_365_ADDEE,
                            ])

    return store_endorsement(
        endorser, endorsee, reason, EndorsementRecord.OFFICE_365_ENDORSEE)


def store_google_endorsement(endorser, endorsee, reason):
    """
    The expected life cycle for a UW G Suite endorsement would be:
      *  Add category 234, status 1 record for given endorsee
      *  Activate subscription 144 for endorsee
    """
    _activate_category(endorsee.netid, Category.GOOGLE_SUITE_ENDORSEE)
    _activate_subscriptions(endorsee.netid, endorser.netid,
                            [Subscription.SUBS_CODE_GOOGLE_APPS])
    return store_endorsement(endorser, endorsee, reason,
                             EndorsementRecord.GOOGLE_SUITE_ENDORSEE)


def clear_office365_endorsement(endorser, endorsee):
    """
    Upon failure to renew, the endorsement tools should:
      *  mark category 235 it former (status 3).
    """
    _former_category(endorsee.netid, Category.OFFICE_365_ENDORSEE)
    clear_endorsement(
        endorser, endorsee, EndorsementRecord.OFFICE_365_ENDORSEE)


def clear_google_endorsement(endorser, endorsee):
    """
    Upon failure to renew, the endorsement tools should:
      *  mark category 234 it former (status 3).
    """
    _former_category(endorsee.netid, Category.GOOGLE_SUITE_ENDORSEE)
    clear_endorsement(
        endorser, endorsee, EndorsementRecord.GOOGLE_SUITE_ENDORSEE)


def is_permitted(endorser, endorsee, subscription_codes):
    active = False
    try:
        response = get_netid_subscriptions(endorsee.netid, subscription_codes)
        for sub in response:
            if sub.subscription_code in subscription_codes:
                subscription_codes.remove(sub.subscription_code)

        active = len(subscription_codes) == 0
    except DataFailureException as ex:
        if ex.status == 404:
            active = False
            # weirdness for testing with mock data
            if getattr(settings, "RESTCLIENTS_DAO_CLASS", 'File') == 'File':
                e = EndorsementRecord.objects.filter(endorsee=endorsee)
                active = len(e) < 0
        else:
            raise

    return active


def is_office365_permitted(endorser, endorsee):
    try:
        get_endorsement(endorser, endorsee,
                        EndorsementRecord.OFFICE_365_ENDORSEE)
        return True, True
    except NoEndorsementException:
        return is_permitted(
            endorser, endorsee, [
                Subscription.SUBS_CODE_OFFICE_365
            ]), False


def is_google_permitted(endorser, endorsee):
    try:
        get_endorsement(endorser, endorsee,
                        EndorsementRecord.GOOGLE_SUITE_ENDORSEE)
        return True, True
    except NoEndorsementException:
        return is_permitted(
            endorser, endorsee, [
                Subscription.SUBS_CODE_GOOGLE_APPS
            ]), False


def _activate_category(netid, category_code):
    """
    return with given netid activated in category_code
    """
    _update_category(netid, category_code, Category.STATUS_ACTIVE)


def _former_category(netid, category_code):
    """
    return with given netid activated in category_code
    """
    _update_category(netid, category_code, Category.STATUS_FORMER)


def _update_category(netid, category_code, status):
    try:
        response = update_catagory(netid, category_code, status)
        if response['responseList'][0]['result'].lower() != "success":
            raise CategoryFailureException(
                '%s' % response['responseList'][0]['result'])
    except (KeyError, DataFailureException) as ex:
        raise CategoryFailureException('%s' % ex)


def _activate_subscriptions(endorsee_netid, endorser_netid, subscriptions):
    try:
        response_list = update_subscription(
            endorsee_netid, 'activate', subscriptions)

        for response in response_list:
            sub_code = int(response.query['subscriptionCode'])
            if (response.http_status == 200 and
                sub_code in subscriptions and
                response.result.lower() == 'success'):
                subscriptions.remove(sub_code)

        if len(subscriptions) > 0:
            for response in response_list:
                if response.result.lower() != 'success':
                    logger.error('subscription error: %s: %s - %s' % (
                            response.query['subscriptionCode'],
                            response.result, response.more_info))

            raise SubscriptionFailureException(
                'Invalid Subscription Response')

    except DataFailureException as ex:
        raise SubscriptionFailureException('%s' % ex)


def record_mail_sent(endorser, endorsement):
    if endorsement['o365']['endorsed']:
        category_code = EndorsementRecord.OFFICE_365_ENDORSEE
        endorsee_netid = endorsement['o365']['endorsee']['netid']
    elif endorsement['google']['endorsed']:
        category_code = EndorsementRecord.GOOGLE_SUITE_ENDORSEE
        endorsee_netid = endorsement['google']['endorsee']['netid']

    EndorsementRecord.objects.filter(
        category_code=category_code,
        endorser=endorser,
        endorsee=get_endorsee_model(endorsee_netid)).update(
            datetime_emailed=timezone.now())
