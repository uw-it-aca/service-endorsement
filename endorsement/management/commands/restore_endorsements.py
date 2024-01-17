# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand
from django.utils import timezone
from endorsement.models import Endorser, EndorsementRecord
from endorsement.dao.endorse import set_active_category, activate_subscriptions
from endorsement.services import get_endorsement_service
from datetime import timedelta
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Go behind the curtain to restore previously cleared endorsements"

    def add_arguments(self, parser):
        parser.add_argument('endorser', type=str)
        parser.add_argument(
            '-l',
            '--list',
            action='store_true',
            dest='list_endorsements',
            default=False,
            help='List endorsed netids with category codes',
        )
        parser.add_argument(
            '-c',
            '--commit',
            action='store_true',
            dest='restore_all',
            default=False,
            help='Restore all endorsements without confirmation',
        )

    def handle(self, *args, **options):
        endorser_netid = options['endorser']
        list_endorsements = options['list_endorsements']
        restore_all = options['restore_all']

        now = timezone.now()
        endorser = Endorser.objects.get(netid=endorser_netid)
        for er in EndorsementRecord.objects.filter(endorser=endorser):
            service = get_endorsement_service(er.category_code)
            # deleted and previously endorsed with lifespan remaining
            if (er.is_deleted
                and er.datetime_endorsed
                and er.datetime_endorsed > (now - timedelta(
                    days=service.endorsement_lifetime))
                and not (
                    er.datetime_notice_1_emailed
                    and er.datetime_notice_2_emailed
                    and er.datetime_notice_3_emailed
                    and er.datetime_notice_4_emailed)):

                if list_endorsements:
                    print("{} {}".format(er.category_code, er.endorsee.netid))
                    continue

                if not restore_all:
                    prompt = "Restore {} for {} by {}? (y/N): ".format(
                        er.category_code, er.endorsee.netid, er.endorser.netid)
                    response = input(prompt).strip().lower()
                    if response != 'y':
                        continue

                self._restore(er, service)

    def _restore(self, er, service):
        print("Activate category {} for {}".format(
            service.category_code, er.endorsee.netid))
        set_active_category(er.endorsee.netid, service.category_code)

        print("Subscribe codes {} for {}".format(
            service.subscription_codes, er.endorsee.netid))
        activate_subscriptions(
            er.endorsee.netid, er.endorser.netid, service.subscription_codes)

        print("Restore endorsement record of {} for {} by {}".format(
            er.category_code, er.endorsee.netid, er.endorser.netid))
        er.is_deleted = None
        er.datetime_expired = None
        er.save()
