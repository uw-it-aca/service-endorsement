# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from endorsement.models import AccessRecord
from endorsement.dao.access import get_accessee_model, store_access_record
from endorsement.dao.office import get_office_accessor
from uw_msca.delegate import get_all_delegates
import json
import csv
import logging

logger = logging.getLogger(__name__)


def reconcile_access(commit_changes=False):
    delegates = get_all_delegates()[1:]

    if len(delegates) < 2:
        logger.error("Reconcile: possible malformed delegates response")
        return

    for row in csv.reader(delegates, delimiter=","):
        if len(row) != 2:
            logger.error("Reconcile: malformed row: {}".format(row))
            continue

        netid = strip_domain(row[0])
        accessee = get_accessee_model(netid)
        access = json.loads(row[1])
        if isinstance(access, dict):
            access = [access]

        dupe_rights = catch_duplicate_access(access)
        records = list(
            AccessRecord.objects.get_access_for_accessee(accessee))
        stale = []
        for i, record in enumerate(records):
            current = has_access(record, access)

            if record.accessor.name in dupe_rights:
                if current:
                    # update current as having multple rights so user
                    # can be offerred opportunity to choose
                    pass

                continue

            if current:
                access.remove(current)
            else:
                stale.append(i)

        # access now only contains unknown delegates
        for a in access:
            # User may be null for expired or unknown valid netids
            if a['User']:
                name = access_user(a)
                if name == 'null':
                    logger.error(
                        "Reconcile: mailbox {} has 'null' accessee".format(
                            netid))
                    continue

                if name in dupe_rights:
                    logger.error(
                        ("Reconcile: mailbox {} with delegate {} "
                         "has MULTIPLE rights: {}").format(
                             netid, name, access))

                    continue

                try:
                    accessor = get_office_accessor(name)
                    logger.info(("Reconcile: ADD {} " +
                                 "gives {} with {}").format(
                                     accessee.netid, accessor.name,
                                     a['AccessRights']))
                    if commit_changes:
                        ar = store_access_record(
                            accessee, accessor, a['AccessRights'])
                except Exception as ex:
                    logger.error(
                        "Reconcile: ERROR: ADD {}: {}".format(name, ex))
            else:
                logger.info(
                    ("Reconcile: ERROR: ADD: Null accessor for  " +
                     "{} granting {} access").format(
                         accessee.netid, a['AccessRights']))

        # records now only contains stale access records
        for i in stale:
            ar = records[i]
            logger.info("Reconcile: REMOVE: {} gave {} with {}".format(
                ar.accessee.netid, ar.accessor.name, ar.right_id))
            if commit_changes:
                ar.revoke()


def has_access(record, access):
    for a in access:
        if (a['User']
                and record.accessor.name == access_user(a)
                and record.right_id == a['AccessRights']):
            return a

    return None


def access_user(a):
    return strip_domain(a['User'])


def strip_domain(name):
    has_at = name.find('@')
    return (name[:-len(name[has_at:])] if has_at >= 0 else name).lower()


def catch_duplicate_access(access):
    dupes = {}
    for i, a in enumerate(access):
        user = access_user(a)
        if user in dupes:
            dupes[user].append(a['AccessRights'])
        else:
            dupes[user] = [a['AccessRights']]
    return {k: v for k, v in dupes.items() if len(v) > 1}
