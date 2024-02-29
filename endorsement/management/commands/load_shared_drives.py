# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.core.management.base import BaseCommand
from django.core.management import call_command
from endorsement.dao.shared_drive import load_shared_drives_from_csv


class Command(BaseCommand):
    help = "load shared drive data from csv file." 

    def add_arguments(self, parser):
        parser.add_argument('csv_file')

    def handle(self, *args, **options):
        load_shared_drives_from_csv(options['csv_file'])
