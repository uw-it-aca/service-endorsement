# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.models import AccessRecord, AccessRight, AccessRecordConflict
from endorsement.dao.access import get_accessee_model, store_access_record
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
    # make sure an empty response (likely an MSCA error condition) doesn't
    # cause all delegations to be deleted
    if len(delegates) < 1024:
        logger.error(
            "Possible malformed delegates response: {}".format(delegates))
        return

    for row in csv.reader(delegates, delimiter=","):
        if len(row) != 2:
            logger.error("Reconcile: malformed row: {}".format(row))
            continue

        netid = strip_domain(row[0])
        accessee = get_accessee_model(netid)
        records = list(
            AccessRecord.objects.get_access_for_accessee(accessee))

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
                        record.revoke()

                    records.remove(record)

                if commit_changes:
                    # create conflict record
                    conflict, c = AccessRecordConflict.objects.get_or_create(
                        accessee=accessee, accessor=record.accessor if (
                            record) else get_office_accessor(delegate))
                    for right in rights:
                        conflict.rights.add(get_access_right(right))

                    conflict.save()
            elif len(rights) == 1:
                right = next(iter(rights))
                if record:
                    if record.access_right.name != right:
                        logger.info(
                            "mailbox {} with {} to {} updated to {}".format(
                                netid, record.access_right.name,
                                delegate, right))

                        if commit_changes:
                            record.access_right = get_access_right(right)
                            record.save()

                    # else delegate right with corresponding record
                    records.remove(record)
                else:
                    # create record for unrecognized delegate right
                    logger.info(
                        "mailbox {} with {} to {} created".format(
                            netid, right, delegate))
                    if commit_changes:
                        try:
                            accessor = get_office_accessor(delegate)
                            store_access_record(
                                accessee, accessor, right, is_reconcile=True)
                        except (UnrecognizedUWNetid, UnrecognizedGroupID):
                            logger.error(
                                "Unknown netid or group: {}".format(delegate))
            else:
                logger.info("mailbox {} empty rights for {}".format(
                    netid, delegate))

        # at this point, records only contains stale delegations
        for record in records:
            logger.info("mailbox {} stale delegation to {} with {}".format(
                record.accessee.netid, record.accessor.name,
                record.access_right.name))
            if commit_changes:
                record.revoke()


def get_access_right(right):
    ar, c = AccessRight.objects.get_or_create(name=right)
    return ar


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
