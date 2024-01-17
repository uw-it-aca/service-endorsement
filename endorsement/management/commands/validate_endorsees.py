# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand, CommandError
from endorsement.endorsee_validation import validate_endorsees


class Command(BaseCommand):
    help = 'Identify and act on provisionees who are no longer valid'

    def handle(self, *args, **options):
        try:
            validate_endorsees()
        except Exception as ex:
            raise CommandError('validate endorsees: {0}'.format(ex))
