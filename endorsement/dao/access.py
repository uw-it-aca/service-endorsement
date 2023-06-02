# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from django.utils import timezone
from uw_msca.delegate import set_delegate, update_delegate, remove_delegate
from endorsement.models import Accessee, Accessor, AccessRecord
from endorsement.dao.pws import get_endorsee_data
from endorsement.exceptions import NoEndorsementException


logger = logging.getLogger(__name__)


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


def get_accessor_model(name, validator):
    """
    return an Accessor object: netid, shared netid or group name
    @exception: DataFailureException
    """
    try:
        accessor = Accessor.objects.get(name=name)
    except Accessor.DoesNotExist:
        try:
            display_name, is_shared, is_group = validator(name)
            accessor, created = Accessor.objects.update_or_create(
                name=name,
                defaults={'display_name': display_name,
                          'is_shared_netid': is_shared,
                          'is_group': is_group,
                          'is_valid': True})
            logger.info("{} accessee: {}".format(
                'Created' if created else "Updated", name))
        except Exception as ex:
            logger.error("accessor model: {}: {}".format(name, ex))
            raise

    return accessor


def store_access(accessee, accessor, right_id, acted_as=None):
    set_delegate(accessee.netid, accessor.name, right_id)
    return store_access_record(accessee, accessor, right_id, acted_as)


def update_access(accessee, accessor, old_right_id, right_id, acted_as=None):
    update_delegate(accessee.netid, accessor.name, old_right_id, right_id)
    return store_access_record(accessee, accessor, right_id, acted_as)


def store_access_record(
        accessee, accessor, right_id, acted_as=None, is_reconcile=None):
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
            is_reconcile=is_reconcile,
            is_deleted=None)

    return ar


def revoke_access(accessee, accessor, right_id, acted_as=None):
    remove_delegate(accessee.netid, accessor.name, right_id)
    return _revoke_access_model(accessee, accessor, right_id, acted_as)


def _revoke_access_model(accessee, accessor, right_id, acted_as=None):
    try:
        ar = AccessRecord.objects.get(
            accessee=accessee, accessor=accessor, right_id=right_id)
    except (AccessRecord.DoesNotExist):
        raise NoEndorsementException()

    logger.info("Revoking {} access to {} for {}".format(
        ar.right_id, ar.accessee.netid, ar.accessor.name,
        " (by {})".format(acted_as) if acted_as else ""))
    ar.revoke()

    return ar
