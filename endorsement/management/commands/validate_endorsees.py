from django.core.management.base import BaseCommand
from django.core.mail import mail_managers
from django.template import loader
from endorsement.models import EndorsementRecord as ER
from uw_uwnetid.models import Category
from endorsement.dao.prt import get_kerberos_inactive_netids_for_category
import logging
import urllib3


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Identify and act on provisionees who are no longer valid'

    def handle(self, *args, **options):
        urllib3.disable_warnings()

        categories = [
            Category.GOOGLE_SUITE_ENDORSEE, Category.OFFICE_365_ENDORSEE
        ]
        netids = []

        for category in categories:
            netids += list(
                set(get_kerberos_inactive_netids_for_category(
                    category)) - set(netids))

        endorsements = ER.objects.filter(
            endorsee__netid__in=netids, category_code__in=categories)

        if len(endorsements):
            body = loader.render_to_string('email/ineligible_endorsee.txt',
                                           {
                                               'endorsements': endorsements
                                           })
            mail_managers(
                'PRT discovered {} inactive kerberos '.format(
                    len(endorsements)), body)

            for e in endorsements:
                logger.info('invalid endorsee: {}'.format(e))
