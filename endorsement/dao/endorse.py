# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.utils import timezone
from django.conf import settings
from endorsement.dao.uwnetid_categories import (
    set_active_category, set_former_category)
from endorsement.dao.uwnetid_subscriptions import (
    activate_subscriptions, active_subscriptions_for_netid)
from endorsement.models import EndorsementRecord
from endorsement.exceptions import NoEndorsementException
from restclients_core.exceptions import DataFailureException
import logging


logger = logging.getLogger(__name__)


def initiate_endorsement(endorser, endorsee, reason, category_code):
    logger.info('initiate category {0} for {1} because {2} by {3}'.format(
        category_code, endorsee.netid, reason, endorser.netid))
    now = timezone.now()
    try:
        en = EndorsementRecord.objects.get(
            endorser=endorser,
            category_code=category_code,
            endorsee=endorsee)
        en.reason = reason
        en.datetime_emailed = None
        en.datetime_endorsed = None
        en.datetime_renewed = now if en.is_deleted else None
        en.datetime_expired = None
        en.is_deleted = None
        en.accept_id = None
        en.accept_salt = None
        en.save()
    except EndorsementRecord.DoesNotExist:
        en = EndorsementRecord.objects.create(
            endorser=endorser,
            category_code=category_code,
            reason=reason,
            endorsee=endorsee,
            datetime_created=now,
            datetime_emailed=None,
            datetime_endorsed=None,
            datetime_renewed=None,
            datetime_expired=None,
            is_deleted=None)

    return en


def store_endorsement(endorser, endorsee, category_code,
                      subscription_codes, acted_as, reason):
    """Return with endorsee category active and subscribed
    """
    logger.info('activate category {0} for {1}{2} because {3} by {4}'.format(
        category_code, endorsee.netid,
        " (by {0})".format(acted_as if acted_as else ""),
        reason, endorser.netid))

    set_active_category(endorsee.netid, category_code)
    activate_subscriptions(
        endorsee.netid, endorser.netid, subscription_codes)
    return _store_endorsement(
        endorser, endorsee, acted_as, reason, category_code)


def _store_endorsement(endorser, endorsee, acted_as, reason, category_code):
    now = timezone.now()
    try:
        en = EndorsementRecord.objects.get(
            endorser=endorser,
            category_code=category_code,
            endorsee=endorsee)
        en.reason = reason
        en.datetime_endorsed = now
        en.acted_as = acted_as
        en.datetime_emailed = None
        en.datetime_notice_1_emailed = None
        en.datetime_notice_2_emailed = None
        en.datetime_notice_3_emailed = None
        en.datetime_notice_4_emailed = None
        en.datetime_renewed = now if en.is_deleted else None
        en.datetime_expired = None
        en.is_deleted = None
        en.save()
    except EndorsementRecord.DoesNotExist:
        en = EndorsementRecord.objects.create(
            endorser=endorser,
            category_code=category_code,
            endorsee=endorsee,
            reason=reason,
            datetime_endorsed=now,
            acted_as=acted_as,
            datetime_emailed=None,
            datetime_notice_1_emailed=None,
            datetime_notice_2_emailed=None,
            datetime_notice_3_emailed=None,
            datetime_notice_4_emailed=None,
            datetime_renewed=None,
            datetime_expired=None,
            is_deleted=None)

    return en


def clear_endorsement(endorsement):
    if (endorsement.datetime_endorsed is not None and
        EndorsementRecord.objects.get_endorsements_for_endorsee(
            endorsement.endorsee, endorsement.category_code).count() <= 1):
        set_former_category(
            endorsement.endorsee.netid, endorsement.category_code)

        logger.info('former category {0} for {1} by {2}'.format(
            endorsement.category_code,
            endorsement.endorsee.netid,
            endorsement.endorser.netid))

    logger.info('clearing record {0} for {1} by {2}'.format(
        endorsement.category_code,
        endorsement.endorsee.netid,
        endorsement.endorser.netid))
    endorsement.revoke()
    return endorsement


def get_endorsement(endorser, endorsee, category_code):
    try:
        return EndorsementRecord.objects.get_endorsement(
            endorser, endorsee, category_code)
    except EndorsementRecord.DoesNotExist:
        raise NoEndorsementException()


def get_endorsements_by_endorser(endorser):
    return EndorsementRecord.objects.get_endorsements_for_endorser(endorser)


def get_all_endorsements_by_endorser(endorser):
    return EndorsementRecord.objects.get_all_endorsements_for_endorser(
        endorser)


def get_endorsements_for_endorsee(endorsee, category_code=None):
    return EndorsementRecord.objects.get_endorsements_for_endorsee(
        endorsee, category_code)


def get_endorsements_for_endorsee_re(endorsee_regex):
    return EndorsementRecord.objects.get_endorsements_for_endorsee_re(
        endorsee_regex)


def get_endorsement_records_for_endorsee_re(endorsee_regex):
    return EndorsementRecord.objects.get_all_endorsements_for_endorsee_re(
        endorsee_regex)


def is_permitted(endorser, endorsee, subscription_codes):
    active = False
    try:

        print("* * * * * ACTIVE SUB {} for {}".format(
            subscription_codes, endorsee.netid))

        active = active_subscriptions_for_netid(
            endorsee.netid, subscription_codes)
    except DataFailureException as ex:
        if getattr(settings, "DEBUG", False) and ex.status == 404:
            active = False
            print("* ** * ** * * * NOPE")
            # weirdness for testing with mock data
            if getattr(settings, "RESTCLIENTS_DAO_CLASS", 'File') == 'File':
                e = EndorsementRecord.objects.filter(
                    endorsee=endorsee, is_deleted__isnull=True)
                active = len(e) < 0
        else:
            raise

    return active
