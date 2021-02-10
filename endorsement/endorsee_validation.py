from uw_uwnetid.category import get_netid_categories
from endorsement.models import EndorsementRecord as ER
from endorsement.dao.endorse import clear_endorsement
from endorsement.dao.prt import get_kerberos_inactive_netids
from endorsement.dao.uwnetid_categories import (
    is_active_category, set_former_category)
from endorsement.services import endorsement_categories
import logging


logger = logging.getLogger(__name__)


def validate_endorsees():
    for netid in get_kerberos_inactive_netids():
        # clear all endorsements we know about
        for e in ER.objects.filter(endorsee__netid=netid):
            if e.is_deleted:
                logger.info('kerberos_inactive: already cleared')
            else:
                logger.info('kerberos_inactive: clearing')
                try:
                    clear_endorsement(e)
                except Exception as ex:
                    logger.error("Clearing {} with {}: {}".format(
                        e.endorsee.netid, e.category_code, ex))

        # and then the endorsements we don't, but should
        for cat in get_netid_categories(netid, endorsement_categories()):
            if is_active_category(cat):
                logger.info('kerberos_inactive: category we should know about')
                try:
                    set_former_category(netid, cat.category_code)
                except Exception as ex:
                    logger.error("Clearing {} with {}: {}".format(
                        netid, cat.category_code, ex))
