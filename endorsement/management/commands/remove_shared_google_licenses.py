# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging

from django.core.management.base import BaseCommand
from uw_uwnetid.category import get_netid_categories
from uw_uwnetid.models import Category

from endorsement.dao.endorse import clear_endorsement
from endorsement.models import EndorsementRecord


class Command(BaseCommand):
    help = 'Set non-admin shared netids google category to FORMER_STATUS_CODE'

    def add_arguments(self, parser):
        parser.add_argument(
            '--commit',
            action='store_true',
            default=False,
            help='Actually Former GOOGLE_SUITE_ENDORSEE category',
        )

    def handle(self, *args, **options):
        logging.getLogger().setLevel(logging.INFO)
        commit_former = options['commit']

        endorsements = EndorsementRecord.objects.filter(
            is_deleted__isnull=True,
            endorsee__is_person=False,
            category_code=Category.GOOGLE_SUITE_ENDORSEE)

        print("owner netid,shared netid,status")
        print("-----------,------------,------")
        for e in endorsements:
            if not self.is_admin_netid(e.endorsee.netid):
                status = f"{e.endorser.netid},{e.endorsee.netid}"
                if commit_former:
                    status += ',former'
                    clear_endorsement(e)
                else:
                    status += ',active'

                print(status)

    def is_admin_netid(self, netid):
        for cat in get_netid_categories(
                netid, [Category.ALTID_ADMIN_ADMINISTRATOR_EADM_WADM]):
            if (cat.status_code != Category.STATUS_FORMER
                and (cat.category_code ==
                     Category.ALTID_ADMIN_ADMINISTRATOR_EADM_WADM)):
                return True

        return False
