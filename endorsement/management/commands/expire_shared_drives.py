# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand
from restclients_core.exceptions import DataFailureException
from endorsement.policy.shared_drive import SharedDrivePolicy
from endorsement.dao.shared_drive import (
    shared_drive_lifecycle_expired, expire_shared_drive)
import csv
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'mark shared drives past their renewal date for deletion'

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--commit',
            action='store_true',
            dest='actually_mark_for_deletion',
            default=False,
            help='Commit shared drive for deletion (default: log only)',
        )
        parser.add_argument(
            '-d',
            '--dump_drive_csv',
            action='store_true',
            dest='dump_drive_csv',
            default=False,
            help='Dump CSV of shared drives that would be marked for deletion',
        )

    def handle(self, *args, **options):
        actually_mark_for_deletion = options['actually_mark_for_deletion']
        dump_drive_csv = options['dump_drive_csv']

        if dump_drive_csv:
            self.drive_writer = csv.writer(self.stdout)
            self.drive_writer.writerow(
                ["Drive ID", "Drive Name", "Manager NetIDs"])

        for record in SharedDrivePolicy().records_to_expire():
            if dump_drive_csv:
                self._record_csv(record)
                continue

            logger.info(f'Expiring: {record.shared_drive.drive_id} '
                        f'"{record.shared_drive.drive_name}"')

            if actually_mark_for_deletion:
                expire_shared_drive(record)

    def _record_csv(self, record):
        self.drive_writer.writerow([
            record.shared_drive.drive_id,
            record.shared_drive.drive_name,
            ",".join([n.member.netid for (
                n) in record.shared_drive.get_members()])])
