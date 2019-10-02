from django.core.management.base import BaseCommand
from django.core.mail import mail_managers
from django.template import loader
from endorsement.models import EndorsementRecord
from datetime import datetime, timedelta
import pytz
import logging
import urllib3


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'alert menagement to expired endorsements'

    # actual expiration happens after one year plus 90 days grace period
    default_lifetime = 455

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
        endorsements = EndorsementRecord.objects.filter(
            datetime_endorsed__lt=now-timedelta(days=lifetime),
            is_deleted__isnull=True)

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

            for e in endorsements:
                logger.info('expiring: {}'.format(e))
