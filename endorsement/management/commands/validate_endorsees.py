from django.core.management.base import BaseCommand
from django.core.mail import mail_managers
from django.template import loader
from endorsement.models import Endorsee, EndorsementRecord as ER
from uw_uwnetid.models import Category
from endorsement.dao.prt import get_kerberos_inactive_netids_for_category


class Command(BaseCommand):
    help = 'Identify and act on provisionees who are no longer valid'

    def handle(self, *args, **options):
        inactive = []

        for category in [
                Category.GOOGLE_SUITE_ENDORSEE, Category.OFFICE_365_ENDORSEE]:
            for netid in get_kerberos_inactive_netids_for_category(category):
                try:
                    endorsee = Endorsee.objects.get(netid=netid)
                    for e in ER.objects.get_endorsements_for_endorsee(
                            endorsee, category_code=category):
                        inactive.append(e)
                except Endorsee.DoesNotExist:
                    pass

        if len(inactive):
            body = loader.render_to_string('email/ineligible_endorsee.txt',
                                           {
                                               'endorsements': inactive
                                           })
            mail_managers(
                'PRT discovered {} inactive kerberos '.format(
                    len(inactive)), body)
