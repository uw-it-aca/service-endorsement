# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.core.management.base import BaseCommand
from django.core.management import call_command
from endorsement.dao.shared_drive import (
    load_shared_drives,
    get_google_drive_states,
)


class Command(BaseCommand):
    help = "load shared drive data from MSCA report."

    def handle(self, *args, **options):
        google_drive_states = get_google_drive_states()
        load_shared_drives(google_drive_states)
