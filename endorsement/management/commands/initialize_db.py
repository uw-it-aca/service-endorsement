# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.core.management.base import BaseCommand
from django.core.management import call_command
from endorsement.models import SharedDriveRecord, ITBillQuantity
from datetime import datetime, timezone, timedelta


class Command(BaseCommand):

    def handle(self, *args, **options):
        # reset quantities
        ITBillQuantity.objects.all().delete()

        call_command('loaddata', 'test_data/accessright.json')
        call_command('loaddata', 'test_data/accessee.json')
        call_command('loaddata', 'test_data/accessor.json')
        call_command('loaddata', 'test_data/accessrecordconflict.json')

        call_command('loaddata', 'test_data/member.json')
        call_command('loaddata', 'test_data/role.json')
        call_command('loaddata', 'test_data/itbill_subscription.json')
        call_command('loaddata', 'test_data/itbill_provision.json')
        call_command('loaddata', 'test_data/itbill_quantity.json')
        call_command('loaddata', 'test_data/shared_drive_member.json')
        call_command('loaddata', 'test_data/shared_drive_quota.json')
        call_command('loaddata', 'test_data/shared_drive.json')
        call_command('loaddata', 'test_data/shared_drive_record.json')

        # adjust dates relative to today
        now = datetime.now(timezone.utc)
        sdr = SharedDriveRecord.objects.get(pk=1)
        sdr.datetime_created = now - timedelta(days=80)
        sdr.datetime_accepted = now - timedelta(days=60)
        sdr.save()

        sdr = SharedDriveRecord.objects.get(pk=2)
        sdr.datetime_created = now - timedelta(days=365)
        sdr.datetime_accepted = now - timedelta(days=330)
        sdr.save()

        sdr = SharedDriveRecord.objects.get(pk=3)
        sdr.datetime_accepted = now - timedelta(days=360)
        sdr.save()

        sdr = SharedDriveRecord.objects.get(pk=4)
        sdr.datetime_created = now - timedelta(days=27)
        sdr.datetime_accepted = None
        sdr.save()

        sdr = SharedDriveRecord.objects.get(pk=5)
        sdr.datetime_accepted = now - timedelta(days=88)
        sdr.save()
