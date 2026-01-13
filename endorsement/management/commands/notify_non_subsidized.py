# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand
from django.utils import timezone
from endorsement.models import SharedDriveRecord
from endorsement.dao.notification import send_notification
from endorsement.util.email import uw_email_address
from endorsement.exceptions import EmailFailureException
from endorsement.notifications.shared_drive import (
    _create_notification_over_quota_non_subsidized)
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send email notifications to reduced-quota shared drive members'

    def add_arguments(self, parser):
        parser.add_argument('shared_drive_ids', type=str)
        parser.add_argument(
            '--commit',
            action='store_true',
            default=False,
            help='Actually send the email notifications',
        )

    def handle(self, *args, **options):
        send_email = options['commit']
        shared_drive_ids = [d.strip() for d in options[
            'shared_drive_ids'].split(',')]

        for drive_id in shared_drive_ids:
            drive = SharedDriveRecord.objects.get(
                shared_drive__drive_id=drive_id)

            if "PENDING_DELETE_" in drive.shared_drive.drive_name:
                logger.info("skip notification: drive name "
                            f"{drive.shared_drive.drive_name}")
                continue

            try:
                members = [uw_email_address(netid) for (
                    netid) in drive.shared_drive.get_member_netids()]
                (subject,
                 text_body,
                 html_body) = _create_notification_over_quota_non_subsidized(
                     drive)
                if send_email:
                    logger.info("over quota email: DriveId: "
                                f"{drive.shared_drive.drive_id} -- "
                                f"To: {', '.join(members)}")
                    send_notification(
                        members, subject, text_body, html_body,
                        "OverSubsidizedQuota")

                    setattr(
                        drive, 'datetime_over_quota_emailed', timezone.now())
                    drive.save()
            except EmailFailureException as ex:
                sys.exit(f"Email failure: {ex}")
