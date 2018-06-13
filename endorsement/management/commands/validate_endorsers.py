from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import mail_managers
from django.template import loader
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorser_model
from endorsement.dao.gws import is_valid_endorser
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Alert management to invalid endorsers'

    def handle(self, *args, **options):
        endorsers = EndorsementRecord.objects.filter(
            datetime_endorsed__isnull=False).values_list(
                'endorser__netid', flat=True).distinct()

        for netid in endorsers:
            if not is_valid_endorser(netid):
                endorser = get_endorser_model(netid)
                endorsements = EndorsementRecord.objects.filter(
                    endorser=endorser)
                body = loader.render_to_string('email/invalid_endorser.txt',
                                               {'endorser': endorser,
                                                'endorsements': endorsements})
                mail_managers(
                    'Provsioner %s no longer valid' % endorser, body)

                logger.info('no longer valid endorser %s of %s endorsments', (
                    netid, len(endorsements)))
