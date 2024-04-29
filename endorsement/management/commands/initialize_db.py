# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):

    def handle(self, *args, **options):
        call_command('loaddata', 'test_data/accessright.json')
        call_command('loaddata', 'test_data/accessee.json')
        call_command('loaddata', 'test_data/accessor.json')
        call_command('loaddata', 'test_data/accessrecordconflict.json')

        call_command('loaddata', 'test_data/member.json')
        call_command('loaddata', 'test_data/role.json')
        call_command('loaddata', 'test_data/itbill_subscription.json')
        call_command('loaddata', 'test_data/shared_drive_member.json')
        call_command('loaddata', 'test_data/shared_drive_quota.json')
        call_command('loaddata', 'test_data/shared_drive.json')
        call_command('loaddata', 'test_data/shared_drive_record.json')
