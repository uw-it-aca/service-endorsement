from django.core.management.base import BaseCommand
from django.core.mail import mail_managers
from django.template import loader
from endorsement.policy import (
    endorsements_to_expire, DEFAULT_ENDORSEMENT_GRACETIME)
from endorsement.dao.endorse import clear_endorsement
import logging
import urllib3


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'expire endorsements and alert managers'

    # actual expiration happens after one year

    def add_arguments(self, parser):
        parser.add_argument(
            '--gracetime', dest='gracetime',
            default=DEFAULT_ENDORSEMENT_GRACETIME, type=int,
            help='expiration grace period in days, default {} days'.format(
                DEFAULT_ENDORSEMENT_GRACETIME))

    def handle(self, *args, **options):
        urllib3.disable_warnings()
        gracetime = options.get('gracetime', DEFAULT_ENDORSEMENT_GRACETIME)
        endorsements = endorsements_to_expire(gracetime)

        if len(endorsements):
            for e in endorsements:
                try:
                    clear_endorsement(e)
                except Exception as ex:
                    logger.error(
                        "Cannot clear endorsement {} for {} by {}: {}".format(
                            e.category_code, e.endorsee.netid,
                            e.endorser.netid, ex))

            body = loader.render_to_string('email/expired_endorsee.txt',
                                           {
                                               'endorsements': endorsements,
                                               'expired_count': len(
                                                   endorsements)
                                           })
            mail_managers(
                'PRT {} services expired'.format(
                    len(endorsements)), body)
