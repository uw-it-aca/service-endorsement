from django.core.management.base import BaseCommand, CommandError
from endorsement.dao.notification import notify_endorsers


class Command(BaseCommand):
    help = 'Send and/or retry failed email notification to endorsers'

    def handle(self, *args, **options):
        try:
            notify_endorsers()
        except Exception as ex:
            raise CommandError('notify endorser: %s' % ex)
