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
