# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging

import urllib3
from django.core.mail import mail_managers
from django.core.management.base import BaseCommand
from django.template import loader

from endorsement.dao.endorse import clear_endorsement
from endorsement.policy.endorsement import EndorsementPolicy

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'expire endorsements and alert managers'

    # actual expiration happens after one year
    def handle(self, *args, **options):
        urllib3.disable_warnings()
        endorsements = EndorsementPolicy().records_to_expire()

        if len(endorsements):
            for e in endorsements:
                try:
                    logger.info(
                        f"Expired endorsement {e.category_code} for {e.endorsee.netid} by {e.endorser.netid}")

                    clear_endorsement(e)
                except Exception as ex:
                    logger.error(
                        f"Cannot clear endorsement {e.category_code} for {e.endorsee.netid} by {e.endorser.netid}: {ex}")

            body = loader.render_to_string('email/expired_endorsee.txt',
                                           {
                                               'endorsements': endorsements,
                                               'expired_count': len(
                                                   endorsements)
                                           })
            mail_managers(
                f'PRT {len(endorsements)} services expired', body)
