import logging
import traceback
from endorsement.util.log import log_exception
from endorsement.dao.gws import get_endorser_endorsees
from endorsement.dao.user import get_endorsee_model, get_endorser_model
from endorsement.dao.endorse import store_office365_endorsement


logger = logging.getLogger(__name__)


def migrate_msca_endorsements():
    """
    Migrate existing MSCA endorsements from UW Groups into this app,
    store in the database
    """
    total_migrated_endorser = 0
    total_migrated_endorsements = 0

    endorser_endorsees_list = get_endorser_endorsees()
    for item in endorser_endorsees_list:
        endorser_netid = item.get("endorser")
        endorsee_list = item.get("endorsees")
        try:
            endorser = get_endorser_model(endorser_netid)
            total_migrated_endorser = total_migrated_endorser + 1
        except Exception:
            log_exception(
                logger,
                "get_endorser_model for %s FAILED, Skip it!" % endorser_netid,
                traceback.format_exc())
            continue

        if len(endorsee_list) == 0:
            logger.error("endorser: %s has no endorsee!" % endorser)
            continue

        for netid in endorsee_list:
            try:
                endorsee = get_endorsee_model(netid)
            except Exception:
                log_exception(
                    logger,
                    "get_endorsee_model for %s FAILED, Skip it!" % netid,
                    traceback.format_exc())
                continue

            store_office365_endorsement(endorser, endorsee)
            total_migrated_endorsements = total_migrated_endorsements + 1

    return total_migrated_endorser, total_migrated_endorsements
