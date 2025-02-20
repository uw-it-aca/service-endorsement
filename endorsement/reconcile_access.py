# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.models import AccessRecord, AccessRight, AccessRecordConflict
from endorsement.dao.access import (
    get_accessee_model, store_access_record, set_delegate)
from endorsement.dao.office import get_office_accessor
from endorsement.exceptions import UnrecognizedUWNetid, UnrecognizedGroupID
from uw_msca.delegate import get_all_delegates
import json
import csv
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def reconcile_access(commit_changes=False):
    delegates = get_all_delegates()[1:]
    delegate_count = len(delegates)
    # make sure an empty response (likely an MSCA error condition) doesn't
    # cause all delegations to be deleted
    if delegate_count < 1024:
        logger.error(
            "Possible malformed delegates response: {}".format(delegates))
        return

    logger.info("Reconcile: {} delegates reported".format(delegate_count))

    accessee_mailboxes = list(AccessRecord.objects.filter(
        is_deleted__isnull=True).values(
            'accessee__netid').distinct().values_list(
                'accessee__netid', flat=True))

    for row in csv.reader(delegates, delimiter=","):
        if len(row) != 2:
            logger.error("Reconcile: malformed row: {}".format(row))
            continue

        netid = strip_domain(row[0])
        accessee = get_accessee_model(netid)
        records = list(
            AccessRecord.objects.get_access_for_accessee(accessee))

        try:
            accessee_mailboxes.remove(netid)
        except ValueError:
            pass

        for delegate, rights in get_delegates(row[1]).items():
            #  loop thru office mailbox delegates
            #    1) catch dupes and record them
            #    2) add records for delegations without one
            #    3) delete records without a matching delegation
            if not delegate or delegate.lower() == 'null':
                logger.info(
                    "mailbox {} with null delegate has rights: {}".format(
                        netid, rights))
                continue

            record, i = get_accessor_record(records, delegate)
            if len(rights) > 1:
                logger.info(
                    "mailbox {} delegate {} has multiple rights: {}".format(
                        netid, delegate, rights))

                if record:
                    if commit_changes:
                        # stash existing access record
                        revoke_record(record)

                    records.remove(record)

                if commit_changes:
                    save_conflict_record(accessee, record, delegate, rights)
            elif len(rights) == 1:
                right = next(iter(rights))
                if record:
                    if record.access_right.name != right:
                        logger.info(
                            ("mailbox {} delegation {} ({})"
                             " on {} updated to {}").format(
                                 netid, delegate, record.access_right.name,
                                 record.datetime_granted, right))
                        if commit_changes:
                            assign_access_right(
                                record, get_access_right(right))
                    # else delegate right and record match

                    records.remove(record)
                else:
                    # create record for unrecognized delegate right
                    logger.info(("mailbox {} delegation {} ({}) "
                                 "not in PRT").format(
                                     accessee.netid, delegate, right))
                    if commit_changes:
                        new_access_record(accessee, delegate, right)
            else:
                logger.info("mailbox {} empty rights for {}".format(
                    netid, delegate))

        # at this point, records only contains stale delegations
        for record in records:
            logger.info(("mailbox {} delegation {} ({}) on {}"
                         "record not in delegate list").format(
                             record.accessee.netid, record.accessor.name,
                             record.access_right.name,
                             record.datetime_granted))
            if commit_changes:
                assign_delegation(accessee, record)

    # after examining all reported delegated mailboxes, acccessee_mailboxes
    # is a list of mailboxes for which prt expected at least one delegation,
    # but none were reported
    for mailbox in accessee_mailboxes:
        accessee = get_accessee_model(mailbox)
        for record in AccessRecord.objects.get_access_for_accessee(accessee):
            logger.info(("mailbox {} delegation {} ({})"
                         " on {} not assigned in Outlook").format(
                             accessee.netid, record.accessor.name,
                             record.access_right.name,
                             record.datetime_granted))
            if commit_changes:
                assign_delegation(accessee, record)


def get_access_right(right):
    ar, c = AccessRight.objects.get_or_create(name=right)
    return ar


def new_access_record(accessee, delegate, right):
    logger.info('commit store access record')
    return

    try:
        accessor = get_office_accessor(delegate)
        store_access_record(
            accessee, accessor, right, is_reconcile=True)

        logger.info("mailbox {} delegation {} ({}) record created".format(
            accessee.netid, delegate, right))
    except (UnrecognizedUWNetid, UnrecognizedGroupID):
        logger.error(
            "Unknown netid or group: {}".format(delegate))


def assign_delegation(accessee, record):

    logger.info('commit set delegate ')
    return

    try:
        set_delegate(accessee.netid, record.accessor.name,
                     record.access_right.name)
        logger.info("mailbox {} delegation {} ({}) assigned".format(
            accessee.netid, record.accessor.name, record.access_right.name))
    except Exception as ex:
        logger.error("set delegate {} ({}) on {} failed: {}".format(
            record.accessor.name, record.access_right.name,
            accessee.netid, ex))


def revoke_record(record):
    logger.info("mailbox {} delegation {} ({}) revoked".format(
        record.accessee.netid, record.accessor.name,
        record.access_right))

    logger.info('commit save record.revoke')
    return

    record.revoke()


def assign_access_right(record, right):
    logger.info('commit save access right')
    return

    record.access_right = right
    record.save()


def save_conflict_record(accessee, record, delegate, rights):

    logger.info('commit save conflict')
    return

    # create conflict record
    conflict, c = AccessRecordConflict.objects.get_or_create(
        accessee=accessee, accessor=record.accessor if (
            record) else get_office_accessor(delegate))
    for right in rights:
        conflict.rights.add(get_access_right(right))

    conflict.save()


def get_accessor_record(records, delegate):
    for i, record in enumerate(records):
        if record.accessor.name == delegate:
            return record, i

    return None, -1


def get_delegates(raw):
    delegates = {}
    cooked = json.loads(raw)
    for right in [cooked] if isinstance(cooked, dict) else cooked:
        try:
            delegates[right["User"]].append(right['AccessRights'])
        except KeyError:
            delegates[right["User"]] = [right['AccessRights']]

    return delegates


def access_user(a):
    return strip_domain(a['User'])


def strip_domain(name):
    has_at = name.find('@')
    return (name[:-len(name[has_at:])] if has_at >= 0 else name).lower()
