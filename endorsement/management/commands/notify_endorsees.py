from django.core.management.base import BaseCommand, CommandError
from endorsement.dao.notification import notify_endorsees


class Command(BaseCommand):
    help = 'Send and/or retry failed email notification'

    def handle(self, *args, **options):
        try:
            notify_endorsees()
        except Exception as ex:
            raise CommandError('notify: {0}'.format(ex))
