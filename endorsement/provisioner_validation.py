# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from endorsement.models import EndorsementRecord as ER
from endorsement.services import get_endorsement_service
from endorsement.dao.notification import notify_invalid_endorser
import logging


logger = logging.getLogger(__name__)


def validate_endorsers():
    endorsements = ER.objects.filter(
        datetime_endorsed__isnull=False,
        is_deleted__isnull=True,
        endorsee__is_person=True,
        endorser__datetime_emailed__isnull=True)

    for endorser_id in list(set([e.endorser.id for e in endorsements])):
        invalid_endorsements = []
        for endorsement in endorsements.filter(
                endorser__id=endorser_id, endorsee__is_person=True):
            service = get_endorsement_service(endorsement.category_code)
            try:
                if not service.valid_endorser(endorsement.endorser.netid):
                    invalid_endorsements.append(endorsement)
            except Exception as ex:
                logger.error('Validation of {} failed: {}'.format(
                    endorsement.endorser.netid, ex))

        if len(invalid_endorsements):
            notify_invalid_endorser(endorsements[0].endorser,
                                    invalid_endorsements)
