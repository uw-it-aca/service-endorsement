# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand, CommandError
from endorsement.notifications.endorsement import notify_endorsers


class Command(BaseCommand):
    help = 'Send and/or retry failed email notification to endorsers'

    def handle(self, *args, **options):
        try:
            notify_endorsers()
        except Exception as ex:
            raise CommandError('notify endorser: {0}'.format(ex))
