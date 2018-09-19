from django.core.management.base import BaseCommand, CommandError
from endorsement.provisioner_validation import validate_endorsers


class Command(BaseCommand):
    help = 'Identify and act on provisioners who are no longer valid'

    def handle(self, *args, **options):
        try:
            validate_endorsers()
        except Exception as ex:
            raise CommandError('notify endorser: {0}'.format(ex))
