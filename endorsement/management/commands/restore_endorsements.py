# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

#
# Management Command restore_endorsements - Given an endorser
# netid or endorsement-defining tuple, restore revoked endorsement while
# preserving original endorsement date.
#
# Arguments: (<endorser> | <endorser>,<endorsee>,<category>) [-l] [-c]
#
#     -l: list, but do not change, revoked endorsement[s]
#     -c: commit change of revoked endorsement to active without
#         any confirmation prompt
#

from django.core.management.base import BaseCommand
from django.utils import timezone
from endorsement.models import Endorser, Endorsee, EndorsementRecord
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
        self.list_endorsements = options['list_endorsements']
        self.restore_all = options['restore_all']

        self.now = timezone.now()
        if ',' in endorser_netid:
            ern, een, cat_code = tuple(endorser_netid.split(','))
            endorser = Endorser.objects.get(netid=ern)
            endorsee = Endorsee.objects.get(netid=een)
            category_code = int(cat_code)
            er = EndorsementRecord.objects.get(
                endorser=endorser, endorsee=endorsee,
                category_code=category_code)
            service = get_endorsement_service(category_code)
            self._verify_restore(er, service)
        else:
            endorser = Endorser.objects.get(netid=endorser_netid)
            for er in EndorsementRecord.objects.filter(endorser=endorser):
                service = get_endorsement_service(er.category_code)
                self._verify_restore(er, service)

    def _verify_restore(self, er, service):
            # deleted and previously endorsed with lifespan remaining
            if (er.is_deleted
                and er.datetime_endorsed
                and er.datetime_endorsed > (self.now - timedelta(
                    days=service.endorsement_lifetime))
                and not (
                    er.datetime_notice_1_emailed
                    and er.datetime_notice_2_emailed
                    and er.datetime_notice_3_emailed
                    and er.datetime_notice_4_emailed)):

                if self.list_endorsements:
                    print("{} {}".format(er.category_code, er.endorsee.netid))
                    return

                if not self.restore_all:
                    prompt = "Restore {} for {} by {}? (y/N): ".format(
                        er.category_code, er.endorsee.netid, er.endorser.netid)
                    response = input(prompt).strip().lower()
                    if response != 'y':
                        return

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
