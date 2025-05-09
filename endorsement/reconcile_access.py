# Copyright 2025 UW-IT, University of Washington
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
import json
import csv
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
MISSING_DELEGATES_THRESHOLD = 1024


def reconcile_access(commit_changes=False):
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

    for row in csv.reader(delegates, delimiter=","):
        if len(row) != 2:
            logger.error(f"Reconcile: malformed row: {row}")
            continue

        netid = strip_domain(row[0])
        accessee = get_accessee_model(netid)

        for delegate, right in mailbox_delegations(row[1]):
            try:
                record = reconcile_delegation(accessee, delegate, right)
                clear_record_id(record_ids, record.id)
            except NullDelegateException:
                logger.info(
                    f"NULL DELEGATE: mailbox {netid} delegate null "
                    f"with right: {right}")
            except NoAccessRecordException:
                logger.info(f"NO ACCESS RECORD FOR: mailbox {netid} "
                            f"delegate {delegate} right: {right}")
                if commit_changes:
                    new_access_record(accessee, delegate, right_record)
            except DeletedAccessRecordException as ex:
                record = None
                # try "live" query since report may have outdated data
                for d in get_delegates(netid):
                    if d.delegate == delegate:
                        record = ex.record
                        break

                if record:
                    logger.info(f"DELETED ACCESS RECORD: "
                                f"mailbox {netid} delegate {delegate} "
                                f"right: {record.access_right.name} on "
                                f"{record.datetime_expired}")

                    if commit_changes:
                        # right still match? update
                        if record.access_right.name != right:
                            logger.info(
                                "UPDATE DELETED ACCESS RECORD: "
                                f"mailbox {netid} "
                                f"delegate {delegate} "
                                f"({record.access_right.name}) to {right}")
                            right_record = get_access_right(right)
                            assign_access_right(record, right_record)

                        logger.info(
                            f"UNDELETED ACCESS RECORD: mailbox {netid} "
                            f"delegate {delegate} "
                            f"({record.access_right.name})")
                        undelete_access_record(record)

                clear_record_id(record_ids, record.id)
            except EmptyDelegateRightsException as ex:
                record = ex.record
                logger.info(f"NO RIGHTS FOR DELEGATION: "
                            f"mailbox {netid} delegate {delegate} BUT "
                            f"record has right: {record.access_right.name}")
                clear_record_id(record_ids, record.id)
            except TooManyRightsException as ex:
                logger.info(
                    f"CONFLICT: mailbox {netid} delegate {delegate} "
                    f"right: {right}")
                record = ex.record
                if commit_changes:
                    revoke_record(record)
                    save_conflict_record(accessee, record, delegate, right)

                clear_record_id(record_ids, record.id)
            except DelegateRightMismatchException as ex:
                record = ex.record
                logger.info(
                    f"DELEGATION CHANGE: mailbox {netid} delegate {delegate}"
                    f" ({record.access_right.name}) to {right}")

                if commit_changes:
                    right_record = get_access_right(right)
                    assign_access_right(record, right_record)

                clear_record_id(record_ids, record.id)

    # access records for which no delegation was reported
    for record in AccessRecord.objects.filter(id__in=record_ids):
        if commit_changes:
            assign_delegation(accessee, record)
        else:
            logger.info(f"MISSING DELEGATION: mailbox {accessee.netid} "
                        f"delegate {record.accessor.name} "
                        f"({record.access_right.name})"
                        f" on {record.datetime_granted} not "
                        "assigned in Outlook")


def clear_record_id(record_ids, record_id):
    try:
        record_ids.remove(record_id)
    except ValueError:
        pass


def reconcile_delegation(accessee, delegate, right):
    if not delegate or delegate.lower() == 'null':
        raise NullDelegateException()

    try:
        record = AccessRecord.objects.get(
            accessee=accessee, accessor__name=delegate)
    except AccessRecord.DoesNotExist:
        raise NoAccessRecordException()

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
    logger.info(
        f"CREATE RECORD: mailbox {accessee.netid} "
        f"delegate {delegate} ({right.name})")

    logger.info("FAILSAFE HIT")
    return

    try:
        accessor = get_office_accessor(delegate)
        store_access_record(
            accessee, accessor, right, is_reconcile=True)

        logger.info(f"mailbox {accessee.netid} delegation {delegate} "
                    f"({right}) record created")
    except (UnrecognizedUWNetid, UnrecognizedGroupID):
        logger.error(
            "Unknown netid or group: {}".format(delegate))


def assign_delegation(accessee, record):
    logger.info('commit set delegate ')

    logger.info("FAILSAFE HIT")
    return

    try:
        set_delegate(accessee.netid, record.accessor.name,
                     record.access_right.name)
        logger.info(f"SET DELGATION: mailbox {accessee.netid} delegation "
                    f"{record.accessor.name} "
                    f"({record.access_right.name})")
    except Exception as ex:
        logger.error("SET DELEGATE FAILED: {record.accessor.name} "
                     f"({record.access_right.name}) on "
                     f"{accessee.netid} reason: {ex}")


def revoke_record(record):
    logger.info("REVOKING mailbox {record.accessee.netid} "
                f"delegation {record.accessor.name} ({record.access_right})")

    logger.info("FAILSAFE HIT")
    return

    record.revoke()


def undelete_access_record(record):
    logger.info("FAILSAFE HIT")
    return

    record.is_deleted = False
    record.save()


def assign_access_right(record, right):
    logger.info(f"UPDATE CHANGE: mailbox {record.accessee.netid} "
                f"delegate {record.accessor.name} "
                f"({record.access_right.name}) : {right.name}")

    logger.info("FAILSAFE HIT")
    return

    record.access_right = right
    record.save()


def save_conflict_record(accessee, record, delegate, rights):
    accessor = record.accessor if (
        record) else get_office_accessor(delegate)
    logger.info(f"UPDATE CONFLICT: mailbox {accessee.netid} "
                f"delegate {accessor.name}: {rights}")

    logger.info("FAILSAFE HIT")
    return

    # create conflict record
    conflict, c = AccessRecordConflict.objects.get_or_create(
        accessee=accessee, accessor=accessor)
    for right in rights:
        conflict.rights.add(get_access_right(right))

    conflict.save()


def mailbox_delegations(column):
    rights = json.loads(column)
    for right in [rights] if isinstance(rights, dict) else rights:
        user = right["User"]
        if user and user.lower() != 'null':
            yield user, right['AccessRights']
        else:
            logger.debug(
                f"NULL RIGHT: mailbox {netid} delegate {delegate}"
                f" right: {right}")


def access_user(a):
    return strip_domain(a['User'])


def strip_domain(name):
    has_at = name.find('@')
    return (name[:-len(name[has_at:])] if has_at >= 0 else name).lower()
