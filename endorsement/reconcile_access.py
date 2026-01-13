# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.models import AccessRecord, AccessRight, AccessRecordConflict
from endorsement.dao.access import (
    get_accessee_model, store_access_record, set_delegate)
from endorsement.dao.office import get_office_accessor
from endorsement.exceptions import (
    UnrecognizedUWNetid, UnrecognizedGroupID, NoAccessRecordException,
    NullDelegateException, AccessRecordException, DeletedAccessRecordException,
    TooManyRightsException, EmptyDelegateRightsException,
    DelegateRightMismatchException)
from uw_msca.delegate import get_delegates, get_all_delegates
from django.utils import timezone
from datetime import timedelta
import json
import csv
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
MISSING_DELEGATES_THRESHOLD = 1024
DELETED_SYNC_GRACE_PERIOD = 14
record_ids = []


def reconcile_access(commit_changes=False):
    global record_ids

    delegates = get_all_delegates()[1:]
    delegate_count = len(delegates)
    # make sure an empty response (likely an MSCA error condition) doesn't
    # cause all delegations to be deleted
    if delegate_count < MISSING_DELEGATES_THRESHOLD:
        logger.error(
            "Possible malformed delegates response: {}".format(delegates))
        return

    # all active record ids
    record_ids = list(AccessRecord.objects.filter(
        is_deleted__isnull=True).values_list('id', flat=True))

    expiration_threshold = timezone.now() - timedelta(
        days=DELETED_SYNC_GRACE_PERIOD)

    for row in csv.reader(delegates, delimiter=","):
        if len(row) != 2:
            logger.error(f"Reconcile: malformed row: {row}")
            continue

        netid = strip_domain(row[0])
        accessee = get_accessee_model(netid)

        logger.debug(f"CSV ROW: {netid} -- {row[1]}")

        for delegate, right in mailbox_delegations(netid, row[1]):
            try:
                record = reconcile_delegation(accessee, delegate, right)
            except NullDelegateException:
                logger.info(
                    f"NULL DELEGATE: mailbox {netid} delegate null "
                    f"with right: {right}")
            except NoAccessRecordException:
                logger.info(f"NO ACCESS RECORD FOR: mailbox {netid} "
                            f"delegate {delegate} right: {right}")
                if commit_changes:
                    new_access_record(accessee, delegate, right)
            except DeletedAccessRecordException as ex:
                record = ex.record

                # validate with "live" delegate
                # query after grace period timeout
                if record.datetime_expired > expiration_threshold:
                    logger.info(
                        f"SKIP DELETED ACCESS RECORD IN GRACE "
                        f"({DELETED_SYNC_GRACE_PERIOD} days): mailbox {netid} "
                        f"delegate {delegate} right: {right}")
                    continue

                logger.info(
                    f"DELETED ACCESS RECORD: mailbox {netid} "
                    f"delegate {delegate} right: {right}")

                # reactivate deleted record
                if commit_changes:
                    if record.access_right.name != right:
                        logger.info(
                            "UPDATE DELETED ACCESS RECORD: "
                            f"mailbox {netid} "
                            f"delegate {delegate} "
                            f"({record.access_right.name}) "
                            f"to {right}")
                        assign_access_right(record, right)

                    if record.is_deleted:
                        logger.info(
                            f"UNDELETED ACCESS RECORD: mailbox {netid} "
                            f"delegate {delegate} "
                            f"({record.access_right.name})")
                        undelete_access_record(record)
            except EmptyDelegateRightsException as ex:
                record = ex.record

                logger.info(f"NO RIGHTS FOR DELEGATION: "
                            f"mailbox {netid} delegate {delegate} BUT "
                            f"record has right: {record.access_right.name}")

            except TooManyRightsException as ex:
                record = ex.record

                logger.info(
                    f"CONFLICT: mailbox {netid} delegate {delegate} "
                    f"right: {right}")

                if commit_changes:
                    revoke_record(record)
                    save_conflict_record(accessee, record, delegate, right)
            except DelegateRightMismatchException as ex:
                record = ex.record

                logger.info(
                    f"DELEGATION CHANGE: mailbox {netid} delegate {delegate} "
                    f"({record.access_right.name}) to {right}")

                if commit_changes:
                    assign_access_right(record, right)

    # access records for which no delegation was reported
    # policy is to remove the record (soft delete) since the delegation
    # was likely removed outside of prt's actions
    for record in AccessRecord.objects.filter(id__in=record_ids):
        logger.info(f"UNREPORTED DELEGATION: mailbox {record.accessee.netid} "
                    f"delegate {record.accessor.name} "
                    f"({record.access_right.name}) "
                    f"on {record.datetime_granted} not "
                    "assigned in Outlook")

        if commit_changes:
            revoke_record(record)


def reconcile_delegation(accessee, delegate, right):
    global record_ids

    if not delegate or delegate.lower() == 'null':
        raise NullDelegateException()

    try:
        record = AccessRecord.objects.get(
            accessee=accessee, accessor__name=delegate)
    except AccessRecord.DoesNotExist:
        raise NoAccessRecordException()

    try:
        record_ids.remove(record.id)
    except ValueError:
        pass

    if record.is_deleted:
        raise DeletedAccessRecordException(record=record)

    if isinstance(right, str):
        if not right:
            raise EmptyDelegateRightsException(record=record)
    elif isinstance(right, list):
        if len(right) == 0:
            raise EmptyDelegateRightsException(record=record)
        elif len(rights) > 1:
            raise TooManyRightsException(record=record)

        right = right[0]

    if record.access_right.name != right:
        raise DelegateRightMismatchException(record=record)

    return record


def get_access_right(right):
    ar, c = AccessRight.objects.get_or_create(name=right)
    return ar


def new_access_record(accessee, delegate, right):
    try:
        accessor = get_office_accessor(delegate)
        store_access_record(
            accessee, accessor, right, is_reconcile=True)

        logger.info(
            f"CREATED RECORD: mailbox {accessee.netid} "
            f"delegate {delegate} ({right.name})")
    except (UnrecognizedUWNetid, UnrecognizedGroupID):
        logger.error(
            "CREATE RECORD: Unknown netid or group: {}".format(delegate))


def revoke_record(record):
    logger.info("REVOKING mailbox {record.accessee.netid} "
                f"delegation {record.accessor.name} ({record.access_right})")
    record.revoke()


def undelete_access_record(record):
    record.is_deleted = False
    record.datetime_expired = None
    record.save()


def assign_access_right(record, right):
    logger.info(f"UPDATE CHANGE: mailbox {record.accessee.netid} "
                f"delegate {record.accessor.name} "
                f"({record.access_right.name}) : {right.name}")
    right_record = get_access_right(right)
    record.access_right = right_record
    record.save()


def save_conflict_record(accessee, record, delegate, rights):
    logger.info(f"CONFLICT RECORD: mailbox {accessee.netid} "
                f"delegate {accessor.name}: {rights}")

    accessor = record.accessor if (
        record) else get_office_accessor(delegate)
    conflict, c = AccessRecordConflict.objects.get_or_create(
        accessee=accessee, accessor=accessor)
    for right in rights:
        conflict.rights.add(get_access_right(right))

    conflict.save()


def mailbox_delegations(netid, column):
    delegations = json.loads(column)
    for i, delegation in enumerate(
            [delegations] if isinstance(delegations, dict) else delegations):
        logger.debug(f"mailbox_delegations: {netid}: {i}) "
                     f"{delegation['User']} -- {delegation['AccessRights']}")
        yield delegation["User"], delegation['AccessRights']


def access_user(a):
    return strip_domain(a['User'])


def strip_domain(name):
    has_at = name.find('@')
    return (name[:-len(name[has_at:])] if has_at >= 0 else name).lower()
