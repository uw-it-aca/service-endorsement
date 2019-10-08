from django.core.management.base import BaseCommand
from endorsement.policy import (
    expire_endorsers, ENDORSEMENT_LIFETIME, ENDORSEMENT_GRACETIME)
import urllib3


class Command(BaseCommand):
    help = 'alert endorsers to expiring endorsements'

    # actual expiration happens after one year

    def add_arguments(self, parser):
        parser.add_argument(
            '--gracetime', dest='gracetime',
            default=ENDORSEMENT_GRACETIME, type=int,
            help='expiration grace period in days, default {} days'.format(
                ENDORSEMENT_GRACETIME))
        parser.add_argument(
            '--lifetime', dest='lifetime',
            default=ENDORSEMENT_LIFETIME, type=int,
            help='provisioning lifetime in days, default {} days'.format(
                ENDORSEMENT_LIFETIME))

    def handle(self, *args, **options):
        urllib3.disable_warnings()
        gracetime = options.get('gracetime', ENDORSEMENT_GRACETIME)
        lifetime = options.get('lifetime', ENDORSEMENT_LIFETIME)
        expire_endorsments(gracetime, lifetime)



from django.core.management.base import BaseCommand
from django.core.mail import mail_managers
from django.template import loader
from endorsement.models import EndorsementRecord
from endorsement.dao.endorse import clear_endorsement
from datetime import datetime, timedelta
import pytz
import logging
import urllib3


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'alert menagement to expired endorsements'

    # actual expiration happens after one year plus 90 days grace period
    default_lifetime = 365

    def add_arguments(self, parser):
        parser.add_argument(
            '--lifetime', dest='lifetime', default=self.default_lifetime,
            type=int,
            help='provisioning lifetime in days, default {0}'.format(
                self.default_lifetime))

    def handle(self, *args, **options):
        urllib3.disable_warnings()
        lifetime = options.get('lifetime', self.default_lifetime)
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        revoke_filter = {
            'datetime_endorsed__lt': now - timedelta(days=lifetime),
            'datetime_reminder_4_emailed__isnull': False,
            'is_deleted__isnull': True
        }

        endorsements = EndorsementRecord.objects.filter(**revoke_filter)

        if len(endorsements):
            body = loader.render_to_string('email/expired_endorsee.txt',
                                           {
                                               'lifetime': lifetime,
                                               'endorsements': endorsements,
                                               'expired_count': len(
                                                   endorsements)
                                           })
            mail_managers(
                'PRT {} services expired'.format(
                    len(endorsements)), body)

            # clear endorsment
            for e in endorsements:
                logger.info('expiring: {}'.format(e))
