from django.core.management.base import BaseCommand
from endorsement.dao.endorse import clear_endorsement, is_endorsed
from endorsement.dao.prt import get_kerberos_inactive_netids_for_category
from endorsement.models import EndorsementRecord as ER
from uw_uwnetid.models import Category
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

        for e in ER.objects.filter(
                endorsee__netid__in=netids,
                category_code__in=categories):
            if e.is_deleted:
                if is_endorsed(e):
                    logger.info(
                        ('Ineligible endorsee reported {} with {} by {} but' +
                         ' is active').format(e.endorsee.netid,
                                              e.category_code,
                                              e.endorser.netid))
                else:
                    continue

            logger.info(
                'Ineligible endorsee: {} with {} by {} revoked'.format(
                    e.endorsee.netid, e.category_code, e.endorser.netid))
            try:
                clear_endorsement(e)
            except Exception as ex:
                logger.error("Clearing {} with {}: {}".format(
                    e.endorsee.netid, e.category_code, ex))
