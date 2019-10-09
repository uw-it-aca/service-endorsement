from django.core.management.base import BaseCommand
from endorsement.dao.notification import warn_endorsers
from endorsement.policy import DEFAULT_ENDORSEMENT_LIFETIME
import urllib3


class Command(BaseCommand):
    help = 'alert endorsers to expiring endorsements'

    def add_arguments(self, parser):
        parser.add_argument('notice_level', type=int)
        parser.add_argument(
            '--lifetime', dest='lifetime',
            default=DEFAULT_ENDORSEMENT_LIFETIME, type=int,
            help='provisioning lifetime in days, default {} days'.format(
                DEFAULT_ENDORSEMENT_LIFETIME))

    def handle(self, *args, **options):
        urllib3.disable_warnings()
        lifetime = options.get('lifetime', DEFAULT_ENDORSEMENT_LIFETIME)
        warn_endorsers(options.get('notice_level'), lifetime)
