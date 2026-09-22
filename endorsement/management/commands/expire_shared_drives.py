# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import csv
import logging

from django.core.management.base import BaseCommand

from endorsement.policy.shared_drive import SharedDrivePolicy

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
        parser.add_argument(
            '-l',
            '--limit-expiration-count',
            type=int,
            default=None,
            help=('Limit expiration to this many '
                  'shared drives (default: no limit)'),
        )

    def handle(self, *args, **options):
        actually_mark_for_deletion = options['actually_mark_for_deletion']
        dump_drive_csv = options['dump_drive_csv']
        limit_expiration_count = options['limit_expiration_count']

        if dump_drive_csv:
            self.drive_writer = csv.writer(self.stdout)
            self.drive_writer.writerow(
                ["Drive ID", "Drive Name", "Manager NetIDs"])

        records = SharedDrivePolicy().records_to_expire()
        if limit_expiration_count:
            # if chunking by limit count, get the oldest records first
            records = records.order_by(
                'datetime_notice_4_emailed')[:limit_expiration_count]

        for record in records:
            if dump_drive_csv:
                self._record_csv(record)
                continue

            logger.info(f'Expiring: {record.shared_drive.drive_id} '
                        f'"{record.shared_drive.drive_name}"')

            if actually_mark_for_deletion:
                record.expire()

    def _record_csv(self, record):
        self.drive_writer.writerow([
            record.shared_drive.drive_id,
            record.shared_drive.drive_name,
            ",".join([n.member.netid for (
                n) in record.shared_drive.get_members()])])
