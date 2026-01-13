# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Endorsement lifecycle module

Basic notions:
  * Endorsement lifespan is defined by each service.
  * Endorsement intial and subsequent warnings are sent prior to expiration.
  * The expiration clock starts on the date of the first warning notice.
  * An expiration grace period is defined by each service
"""
from endorsement.models import EndorsementRecord
from endorsement.policy import PolicyBase
from endorsement.services import endorsement_services
from endorsement.dao.endorse import clear_endorsement


DEFAULT_ENDORSEMENT_GRACEPERIOD = 90


class EndorsementPolicy(PolicyBase):
    @property
    def record_model(self):
        return EndorsementRecord

    @property
    def datetime_provisioned_key(self):
        return "datetime_endorsed"

    @property
    def graceperiod(self):
        return DEFAULT_ENDORSEMENT_GRACEPERIOD

    def additional_warning_terms(self):
        return {
            'category_code__in': [
                s.category_code for s in endorsement_services()]
        }


def expire_endorsments(gracetime, lifetime):
    """
    """
    for e in endorsements_to_expire(gracetime, lifetime):
        clear_endorsement(e)
