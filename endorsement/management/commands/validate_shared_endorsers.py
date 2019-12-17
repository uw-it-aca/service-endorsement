from django.core.management.base import BaseCommand, CommandError
from endorsement.shared_validation import validate_shared_endorsers


class Command(BaseCommand):
    help = 'Identify and act on shared netid owners'

    def handle(self, *args, **options):
        try:
            validate_shared_endorsers()
        except Exception as ex:
            raise CommandError('validate shared endorsers: {0}'.format(ex))
