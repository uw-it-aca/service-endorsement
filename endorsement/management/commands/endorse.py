# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand, CommandError
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.services import get_endorsement_service
from endorsement.exceptions import NoEndorsementException
import getpass
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Go behind the curtain to endorse service"

    def add_arguments(self, parser):
        parser.add_argument('endorser', type=str)
        parser.add_argument('service', type=str)
        parser.add_argument('endorsees', nargs='+', type=str)
        parser.add_argument('--reason',
                            default=None,
                            help="Reason for the endorsement")
        parser.add_argument('--actas',
                            default=None,
                            help="Netid for act_as netid (default {})".format(
                                getpass.getuser()))
        parser.add_argument(
            '--commit',
            action='store_true',
            default=False,
            help='Store endorsemnt record',
        )
        parser.add_argument(
            '--create',
            action='store_true',
            default=False,
            help='Create endorsement for previously unendorsed',
        )

    def handle(self, *args, **options):
        endorser_netid = options['endorser']
        service = get_endorsement_service(options['service'])

        if not service.valid_endorser(endorser_netid):
            raise CommandError("Invalid Endorser: {}".format(endorser_netid))

        endorser = get_endorser_model(endorser_netid)

        reason = options['reason']
        commit_endorsement = options['commit']
        act_as = options['actas'] if options['actas'] else getpass.getuser()

        for endorsee_netid in options['endorsees']:
            endorsee = get_endorsee_model(endorsee_netid)
            try:
                er = EndorsementRecord.objects.get(
                    endorser=endorser, endorsee=endorsee, 
                    category_code=service.category_code)
                if not er.is_deleted and er.datetime_endorsed:
                    print(("Currently endorsed {} "
                           "by {} for {} created on {}").format(
                               service.service_name, endorser.netid,
                               endorsee.netid, er.datetime_endorsed))
                    continue

                print("{}Endorse {} (act_as {}) for {} with reason: {}".format(
                    "" if commit_endorsement else "WOULD ",
                    endorsee.netid, act_as,
                    service.service_name, 
                    er.reason if er.reason else reason if (
                        reason) else "Restored Service"))

                if commit_endorsement:
                    service.store_endorsement(
                        endorser, endorsee, act_as,
                        er.reason if er.reason else reason if (
                            reason) else "Restored Service")
            except EndorsementRecord.DoesNotExist:
                if options['create']:
                    print(("{} CREATE endorsement {} (act_as {}) for {}"
                           " with reason: {}").format(
                               "" if commit_endorsement else "WOULD ",
                               endorsee.netid, act_as,
                               service.service_name, 
                               reason if reason else "Restored Service"))
    
                    if commit_endorsement:
                        service.store_endorsement(
                            endorser, endorsee, act_as,
                            reason if reason else "Restored Service")
                else:
                    print("Skip create {} endoresement for {}".format(
                        service.service_name, endorsee.netid))
 

