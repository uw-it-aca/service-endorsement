# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging

from uw_uwnetid.category import get_netid_categories

from endorsement.dao.endorse import clear_endorsement
from endorsement.dao.prt import get_kerberos_inactive_netids
from endorsement.dao.uwnetid_categories import is_active_category, set_former_category
from endorsement.models import EndorsementRecord as ER
from endorsement.services import endorsement_categories

logger = logging.getLogger(__name__)


def validate_endorsees():
    for netid in get_kerberos_inactive_netids():
        # clear all endorsements we know about
        for e in ER.objects.filter(endorsee__netid=netid):
            if e.is_deleted:
                logger.info(
                    f"Invalid Provisionee: already cleared {e.category_code} for {netid}")
            else:
                logger.info(
                    f"Invalid Provisionee: clearing {e.category_code} for {netid}")
                try:
                    clear_endorsement(e)
                except Exception as ex:
                    logger.error(f"Error clearing {netid} with {e.category_code}: {ex}")

        # then any categories we don't have a record of setting (but should)
        for cat in get_netid_categories(netid, endorsement_categories()):
            if is_active_category(cat):
                logger.info(
                    f"Invalid Provisionee: clearing unstored {cat.category_code} for {netid}")
                try:
                    set_former_category(netid, cat.category_code)
                except Exception as ex:
                    logger.error(f"Clearing {netid} with {cat.category_code}: {ex}")
