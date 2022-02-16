# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand
from endorsement.dao.notification import warn_endorsers
import urllib3


class Command(BaseCommand):
    help = 'alert endorsers to expiring endorsements'

    def add_arguments(self, parser):
        parser.add_argument('notice_level', type=int)

    def handle(self, *args, **options):
        urllib3.disable_warnings()
        warn_endorsers(options.get('notice_level'))
