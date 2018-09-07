from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import mail_managers
from django.template import loader
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorsee_model
from datetime import datetime, timedelta
import pytz
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'alert menagement to expired endorsements'

    default_lifetime = 360

    def add_arguments(self, parser):
        parser.add_argument(
            '--lifetime', dest='lifetime', default=self.default_lifetime,
            type=int,
            help='provisioning lifetime in days, default {0}'.format(
                self.default_lifetime))

    def handle(self, *args, **options):
        lifetime = options.get('lifetime', self.default_lifetime)
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        endorsements = EndorsementRecord.objects.filter(
            datetime_endorsed__lt=now-timedelta(days=lifetime),
            is_deleted__isnull=True)
        endorsees = list(set([e.endorsee.netid for e in endorsements]))
        for netid in endorsees:
            endorsee = get_endorsee_model(netid)
            body = loader.render_to_string('email/expired_endorsee.txt',
                                           {
                                               'lifetime': lifetime,
                                               'endorsee': endorsee,
                                               'endorsements': endorsements
                                           })
            mail_managers(
                'Provisioned services for {0} expiring'.format(endorsee), body)

            logger.info('expired endorsments ({0}) for {1}'.format(
                len(endorsements), netid))
