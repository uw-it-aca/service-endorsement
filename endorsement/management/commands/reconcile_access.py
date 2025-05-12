# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand
from endorsement.reconcile_access import reconcile_access
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reconcile Office365 mailbox access with local data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            default=False,
            help='Store access record changes',
        )

    def handle(self, *args, **options):
        commit_changes = options['commit']
        try:
            reconcile_access(commit_changes=commit_changes)
        except Exception as ex:
            logger.exception(
                "reconcile_access: Exception: {}".format(ex), stack_info=True)
