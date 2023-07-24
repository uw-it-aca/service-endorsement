# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand
from endorsement.reconcile_access import reconcile_access
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reconcile Office365 mailbox access with local data"

    def handle(self, *args, **options):
        try:
            reconcile_access(commit_changes=True)
        except Exception as ex:
            logger.error("reconcile_access: Exception: {}".format(ex))
