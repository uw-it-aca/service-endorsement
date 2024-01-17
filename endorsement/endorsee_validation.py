# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

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
                logger.info(
                    "Invalid Provisionee: already cleared {} for {}".format(
                        e.category_code, netid))
            else:
                logger.info(
                    "Invalid Provisionee: clearing {} for {}".format(
                        e.category_code, netid))
                try:
                    clear_endorsement(e)
                except Exception as ex:
                    logger.error("Error clearing {} with {}: {}".format(
                        netid, e.category_code, ex))

        # then any categories we don't have a record of setting (but should)
        for cat in get_netid_categories(netid, endorsement_categories()):
            if is_active_category(cat):
                logger.info(
                    "Invalid Provisionee: clearing unstored {} for {}".format(
                        e.category_code, netid))
                try:
                    set_former_category(netid, cat.category_code)
                except Exception as ex:
                    logger.error("Clearing {} with {}: {}".format(
                        netid, cat.category_code, ex))
