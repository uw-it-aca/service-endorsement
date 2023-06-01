# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand, CommandError
from endorsement.dao.notification import notify_endorsees, notify_accessors


class Command(BaseCommand):
    help = 'Send and/or retry failed email notification'

    def handle(self, *args, **options):
        try:
            notify_endorsees()
            notify_accessors()
        except Exception as ex:
            raise CommandError('notify: {0}'.format(ex))
