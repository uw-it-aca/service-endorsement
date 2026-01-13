# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand
from endorsement.models import AccessRecord, AccessRight, AccessRecordConflict
from endorsement.dao.access import (
    get_accessee_model, store_access_record, set_delegate)
from endorsement.dao.office import get_office_accessor
from endorsement.exceptions import UnrecognizedUWNetid, UnrecognizedGroupID
from uw_msca.delegate import get_all_delegates, _msca_get_delegate_url
from uw_msca import get_resource
import json
import csv
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = "Restore Office365 mailbox access from MSCA"

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            default=False,
            help='Store access record changes',
        )
        parser.add_argument(
            '--netid',
            type=str,
            help='Netid to restore rights for')
        parser.add_argument(
            '--csv',
            type=str,
            help='CSV of accessor netid, accessor name, access right')

    def handle(self, *args, **options):
        self.commit_changes = options['commit']
        netid = options['netid']
        csv_file = options['csv']
        try:
            if netid:
                self.restore_netid_access(netid)
            elif csv_file:
                self.restore_csv_access(csv_file)
        except Exception as ex:
            logger.error("restore_access_rights: Exception: {}".format(ex))

    def restore_netid_access(self, netid):
        accessee = get_accessee_model(netid)
        for delegate, right in self.get_delegates_for_netid(netid).items():
            try:
                self.fix_access_record(accessee, delegate, right)
            except Exception as ex:
                logger.info(f"ERROR: assign delegate {delegate}: {ex}")
                continue

    def get_delegates_for_netid(self, netid):
        url = _msca_get_delegate_url(netid)
        response = get_resource(url)
        json_response = json.loads(response)
        delegates = {}
        for delegation in json_response:
            if netid != delegation['netid']:
                raise Exception("netid mismatch")
            netid = delegation['netid']
            delegations = delegation['delegates']
            if isinstance(delegations, dict):
                user = delegations['User']
                if not user:
                    continue

                rights = delegations['AccessRights']
                delegates[user] = rights
            elif isinstance(delegations, list):
                for d in delegations:
                    user = d['User']
                    if not user:
                        continue

                    rights = d['AccessRights']
                    if isinstance(rights, list):
                        if len(rights) == 1:
                            delegates[user] = rights[0]
                        else:
                            raise Exception(f"multiple rights for "
                                            f"{user}: {rights}")
                    elif isinstance(rights, str):
                        delegates[user] = rights
                    else:
                        raise Exception(f"unknown right type for {user}")
        return delegates

    def fix_access_record(self, accessee, delegate, right):
        try:
            accessor = get_office_accessor(delegate)
        except Exception as ex:
            raise Exception(f"ERROR: get accessor {delegate}: {ex}")

        try:
            ar = AccessRecord.objects.get(
                accessee=accessee, accessor=accessor)
        except AccessRecord.DoesNotExist:
            raise Exception(f"ERROR: no record: mailbox {netid} "
                            f"delegate {delegate}")
        try:
            rr = AccessRight.objects.get(name=right)
        except AccessRight.DoesNotExist:
            raise Exception(f"ERROR: unknown right {right} ")

        if ar.access_right != rr:
            if self.commit_changes:
                ar.access_right = rr
                ar.save()

            logger.info(
                f"{'' if self.commit_changes else 'WOULD '}ASSIGN: "
                f"mailbox {ar.accessee.netid} "
                f"delegate {ar.accessor.name} "
                f"right '{ar.access_right.display_name if (
                     self.commit_changes) else rr.display_name}'")

    def reconcile_csv_access(self, csv_file):
        delegations = {}
        with open(csv_file, 'r') as f:
            blank_reader = csv.reader(f)
            for i, line in enumerate(blank_reader):
                delegates = json.loads(line[1])
                if not delegates or delegates == 'null':
                    continue

                netid = line[0]
                if netid not in delegations:
                    delegations[netid] = {}

                if isinstance(delegates, dict):
                    user = delegates['User']
                    right = delegates['AccessRights']
                    delegations[netid][user] = right
                else:
                    for d in delegates:
                        user = d['User']
                        right = d['AccessRights']
                        delegations[netid][user] = right

        with open('/tmp/blanks_remaining.csv', 'r') as f:
            blank_reader = csv.reader(f)
            for i, line in enumerate(blank_reader):
                netid = line[0]
                if netid not in delegations:
                    logger.info(f"mailbox {netid} has no delegates")
                    continue

                try:
                    accessee = get_accessee_model(netid)
                except UnrecognizedUWNetid:
                    logger.info(f"ERROR: get accessee {netid}: unrecognized")
                    continue
                except Exception as ex:
                    logger.info(f"ERROR: get accessee {netid}: {ex}")
                    continue

                for delegate, right in delegations[netid].items():
                    try:
                        fix_access_record(accessee, delegate, right)
                    except Exception as ex:
                        logger.info(f"ERROR: assign delegate {delegate}: {ex}")
                        continue
