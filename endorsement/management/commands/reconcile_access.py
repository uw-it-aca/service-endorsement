# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand
from endorsement.models import AccessRecord
from endorsement.dao.access import get_accessee_model, store_access_record
from endorsement.dao.office import get_office_accessor
import argparse
import json
import sys
import csv
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Given Office365 mailbox access delegate list, reconcile local data"

    def add_arguments(self, parser):
        parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                            default=sys.stdin)
        parser.add_argument(
            '-c',
            '--commit',
            action='store_true',
            dest='commit_changes',
            default=False,
            help='Commit to removal of category from netid',
        )

    def handle(self, *args, **options):
        commit_changes = options['commit_changes']
        first_line = True
        for row in csv.reader(options['infile'], delimiter=","):
            if first_line:
                first_line = False
                continue

            netid = self.strip_domain(row[0])
            accessee = get_accessee_model(netid)
            access = json.loads(row[1])
            if isinstance(access, dict):
                access = [access]

            records = list(
                AccessRecord.objects.get_access_for_accessee(accessee))
            stale = []
            for i, record in enumerate(records):
                current = self.has_access(record, access)
                if current:
                    access.remove(current)
                else:
                    stale.append(i)

            # access now only contains unknown delegates
            for a in access:
                # User may be null for expired or unknown valid netids
                if a['User']:
                    name = self.strip_domain(a['User'])
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

    def has_access(self, record, access):
        for a in access:
            if (a['User']
                    and record.accessor.name == self.strip_domain(a['User'])
                    and record.right_id == a['AccessRights']):
                return a

        return None

    def strip_domain(self, name):
        has_at = name.find('@')
        return (name[:-len(name[has_at:])] if has_at >= 0 else name).lower()
