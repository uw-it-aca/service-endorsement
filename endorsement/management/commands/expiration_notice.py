from django.core.management.base import BaseCommand
from endorsement.dao.notification import warn_endorsers
import urllib3


class Command(BaseCommand):
    help = 'alert endorsers to expiring endorsements'

    def handle(self, *args, **options):
        urllib3.disable_warnings()
        warn_endorsers(options.get('notice_level'))
