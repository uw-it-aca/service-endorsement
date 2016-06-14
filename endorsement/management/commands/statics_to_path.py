from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
# from django.contrib.staticfiles import coll
from django.core import management

class Command(BaseCommand):
    help = 'Collects app\'s static files to a specified path'
    args = "<statics path>"

    def handle(self, *args, **options):
        try:
            statics_path = args[0]
            settings.STATIC_ROOT = statics_path
            management.call_command('collectstatic', interactive=False, verbosity=0)
        except IndexError:
            raise CommandError("You must specify a statics path")
        except Exception as ex:
            raise CommandError(ex)