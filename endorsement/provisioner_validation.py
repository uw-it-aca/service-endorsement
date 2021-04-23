# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from endorsement.models import EndorsementRecord as ER
from endorsement.dao.user import get_endorser_model
from endorsement.dao.gws import endorser_group_member
from endorsement.dao.notification import notify_invalid_endorser
import logging


logger = logging.getLogger(__name__)


def validate_endorsers():
    endorsements = ER.objects.filter(
        datetime_endorsed__isnull=False,
        is_deleted__isnull=True,
        endorsee__is_person=True,
        endorser__datetime_emailed__isnull=True)

    for netid in list(set([e.endorser.netid for e in endorsements])):
        try:
            if not endorser_group_member(netid):
                endorser = get_endorser_model(netid)
                endorsements = ER.objects.get_endorsements_for_endorser(
                    endorser).filter(endorsee__is_person=True)
                notify_invalid_endorser(endorser, endorsements)
        except Exception as ex:
            logger.error('Validation of {} failed: {}'.format(netid, ex))
