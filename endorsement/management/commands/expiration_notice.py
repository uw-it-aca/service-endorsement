# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand
from endorsement.notifications.endorsement import (
    endorser_lifecycle_warning)
from endorsement.notifications.access import (
    accessee_lifecycle_warning)
from endorsement.notifications.shared_drive import (
    drive_member_lifecycle_warning)
import urllib3


class Command(BaseCommand):
    help = 'alert endorsers to expiring endorsements'

    def add_arguments(self, parser):
        parser.add_argument('notice_level', type=int)

    def handle(self, *args, **options):
        level = options.get('notice_level')

        urllib3.disable_warnings()

        endorser_lifecycle_warning(level)
        accessee_lifecycle_warning(level)
        drive_member_lifecycle_warning(level)
