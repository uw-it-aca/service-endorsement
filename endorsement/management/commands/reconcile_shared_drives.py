# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
import logging

from django.core.management.base import BaseCommand

from endorsement.dao.shared_drive import Reconciler


class Command(BaseCommand):
    help = "Loop over all shared drives verifying lifecycle and subscriptions"

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-move-drive',
            action='store_true',
            default=False,
            help="If provided no drives will be moved.",
        )
        parser.add_argument(
            '--missing-drive-threshold',
            type=int,
            default=50,
            help="Skip missing drive deletion if missing drive count greater.",
        )

    def handle(self, *args, **options):
        logging.getLogger().setLevel(logging.INFO)
        params = {
            'no_move_drive': options['no_move_drive'],
            'missing_drive_threshold': options['missing_drive_threshold'],
        }

        Reconciler(**params).reconcile()
