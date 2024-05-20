# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
import logging

from django.core.management.base import BaseCommand

from endorsement.dao.shared_drive import Reconciler


class Command(BaseCommand):
    help = "Loop over all shared drives verifying lifecycle and subscriptions"

    def handle(self, *args, **options):
        logging.getLogger().setLevel(logging.INFO)
        Reconciler().reconcile()
