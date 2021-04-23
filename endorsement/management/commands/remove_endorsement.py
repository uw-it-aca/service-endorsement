# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.core.management.base import BaseCommand
from endorsement.dao.endorse import clear_endorsement
from endorsement.models import EndorsementRecord
import logging
import argparse


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Remove endorsement from netids for given category code'

    def add_arguments(self, parser):
        parser.add_argument('category_code', type=int, nargs='?', default=None)
        parser.add_argument('netids', type=str, nargs='*', default=[])
        parser.add_argument(
            '-f',
            '--file',
            type=argparse.FileType('r'),
            dest='netid_file',
            default=None,
            help='Read netids to unendorse from file',
        )
        parser.add_argument(
            '-l',
            '--list',
            action='store_true',
            dest='list_category_codes',
            default=False,
            help='List category codes',
        )
        parser.add_argument(
            '-c',
            '--commit',
            action='store_true',
            dest='actually_remove_category',
            default=False,
            help='Commit to removal of category from netid',
        )

    def handle(self, *args, **options):
        category_code = options['category_code']
        netids = options['netids']
        netid_file = options['netid_file']
        list_category_codes = options['list_category_codes']
        actually_remove_category = options['actually_remove_category']

        if list_category_codes or not category_code:
            for c in EndorsementRecord.CATEGORY_CODE_CHOICES:
                print("{}: {}".format(c[0], c[1]))
            exit(0)

        choices = dict(EndorsementRecord.CATEGORY_CODE_CHOICES)
        for netid in netids if netids else netid_file:
            netid = netid.strip()

            for er in EndorsementRecord.objects.filter(
                    category_code=category_code,
                    endorsee__netid=netid,
                    is_deleted__isnull=True):
                msg = "{} endorsement of {} by {} from {} ({})".format(
                    "Removing" if actually_remove_category else "WILL remove",
                    netid, er.endorser.netid, er.category_code,
                    choices[er.category_code])
                print(msg)
                if actually_remove_category:
                    logger.info("Manually {}".format(msg))
                    clear_endorsement(er)
