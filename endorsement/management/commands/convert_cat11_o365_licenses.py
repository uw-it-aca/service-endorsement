# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging

from django.core.management.base import BaseCommand
from uw_uwnetid.category import get_netid_categories
from uw_uwnetid.models import Category

from endorsement.dao.uwnetid_categories import (
    set_active_category,
    set_former_category,
)
from endorsement.models import EndorsementRecord

OFFICE_365_STUDENT_ENDORSEE = Category.OFFICE_365_STUDENT_ENDORSEE


class Command(BaseCommand):
    help = 'Convert category 11 shared netids o365 to o365 student license'

    def handle(self, *args, **options):
        logging.getLogger().setLevel(logging.INFO)

        endorsements = EndorsementRecord.objects.filter(
            is_deleted__isnull=True,
            endorsee__is_person=False,
            category_code=Category.OFFICE_365_ENDORSEE)

        print("owner netid,shared netid")
        print("-----------,------------")
        for e in endorsements:
            if not self.is_admin_netid(e.endorsee.netid):
                print(f"{e.endorser.netid},{e.endorsee.netid}")

                # former Category.OFFICE_365_ENDORSEE
                set_former_category(
                    e.endorsee.netid, Category.OFFICE_365_ENDORSEE)

                # activate Category.OFFICE_365_STUDENT_ENDORSEE
                set_active_category(
                    e.endorsee.netid, OFFICE_365_STUDENT_ENDORSEE)

                # update EndorsementRecord
                e.category_code = OFFICE_365_STUDENT_ENDORSEE
                e.save()

    def is_admin_netid(self, netid):
        for cat in get_netid_categories(
                netid, [Category.ALTID_ADMIN_ADMINISTRATOR_EADM_WADM]):
            if (cat.status_code != Category.STATUS_FORMER
                and (cat.category_code ==
                     Category.ALTID_ADMIN_ADMINISTRATOR_EADM_WADM)):
                return True

        return False
