# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from django.utils import timezone
from endorsement.models import (
    Accessee, Accessor, AccessRecord, EndorsementRecord)
from endorsement.services import get_endorsement_service
from endorsement.dao.pws import get_endorsee_data
from endorsement.dao.user import get_endorsee_model
from endorsement.dao.uwnetid_subscriptions import (
    active_subscriptions_for_netid)
from endorsement.exceptions import NoEndorsementException


logger = logging.getLogger(__name__)


def is_office_permitted(netid):
    """
    test for office mailbox availability
    """
    o365 = get_endorsement_service('o365');
    endorsee = get_endorsee_model(netid)
    for er in EndorsementRecord.objects.get_endorsements_for_endorsee(
            endorsee, o365.category_code):
        if er.datetime_endorsed and not er.datetime_expired:
            return True

    # if no endorsement record, check subscription_codes
    try:
        return active_subscriptions_for_netid(netid, o365.subscription_codes)
    except Exception as ex:
        logger.error("is_office_permitted: {}: {}".format(netid, ex))
        pass

    return False


def get_accessee_model(netid):
    """
    return an Accessee object accounting for netid, typically shared, changes
    @exception: DataFailureException
    """
    try:
        accessee = Accessee.objects.get(netid=netid)
    except Accessee.DoesNotExist:
        uwregid, display_name, email, is_person = get_endorsee_data(netid)
        accessee, created = Accessee.objects.update_or_create(
            regid=uwregid,
            defaults={'netid': netid, 'display_name': display_name})

        logger.info("{} accessee: {}".format(
            'Created' if created else "Updated", accessee))

    return accessee


def get_accessor_model(name):
    """
    return an Accessor object: netid, shared netid or group name
    @exception: DataFailureException
    """
    try:
        accessor = Accessor.objects.get(name=name)
    except Accessor.DoesNotExist:
        try:
            uwregid, display_name, email, is_person = get_endorsee_data(name)
            accessor, created = Accessor.objects.update_or_create(
                name=name,
                defaults={'display_name': display_name,
                          'is_shared_netid': (not is_person)})

            logger.info("{} accessee: {}".format(
                'Created' if created else "Updated", name))
        except Exception as ex:
            logger.error("accessor model: {}: {}".format(name, ex))
            raise

    return accessor


def store_access(accessee, accessor, right_id, acted_as=None):
    now = timezone.now()
    try:
        ar = AccessRecord.objects.get(accessee=accessee, accessor=accessor)
        ar.right_id = right_id
        ar.datetime_granted = now
        ar.acted_as = acted_as
        ar.datetime_emailed = None
        ar.datetime_notice_1_emailed = None
        ar.datetime_notice_2_emailed = None
        ar.datetime_notice_3_emailed = None
        ar.datetime_notice_4_emailed = None
        ar.datetime_renewed = now if ar.is_deleted else None
        ar.datetime_expired = None
        ar.is_deleted = None
        ar.save()
    except AccessRecord.DoesNotExist:
        ar = AccessRecord.objects.create(
            accessee=accessee,
            accessor=accessor,
            right_id=right_id,
            datetime_granted=now,
            acted_as=acted_as,
            datetime_emailed=None,
            datetime_notice_1_emailed=None,
            datetime_notice_2_emailed=None,
            datetime_notice_3_emailed=None,
            datetime_notice_4_emailed=None,
            datetime_renewed=None,
            datetime_expired=None,
            is_deleted=None)

    return ar


def revoke_access(accessee, accessor, acted_as=None):
    now = timezone.now()
    try:
        ar = AccessRecord.objects.get(accessee=accessee, accessor=accessor)
    except AccessRecord.DoesNotExist:
        raise NoEndorsementException()

    logger.info("Revoking {} access to {} for {}".format(
        ar.right_id, ar.accessee.netid, ar.accessor.name))
    ar.revoke()

    return ar
