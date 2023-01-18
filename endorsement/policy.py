# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Endorsement lifecycle module

Basic notions:
  * Endorsement lifespan is defined by each service.
  * Endorsement intial and subsequent warnings are sent prior to expiration.
  * The expiration clock starts on the date of the first warning notice.
  * An expiration grace period is defined by each service
"""
from django.utils import timezone
from django.db.models import Q
from endorsement.services import endorsement_services
from endorsement.models import EndorsementRecord
from endorsement.dao.endorse import clear_endorsement
from datetime import timedelta


def endorsements_to_warn(level):
    """
    """
    return _endorsements_to_warn(timezone.now(), level)


def _endorsements_to_warn(now, level):
    """
    Gather endorsement records to receive expiration warning messages where
    level is the index of the warning message: first, second and so forth

    The expiration clock starts on the date of the first warning notice
    """
    if level < 1 or level > 4:
        raise Exception('bad warning level {}'.format(level))

    q = Q()

    # select on appropriate time span for warning notice index (level)
    for service in endorsement_services():
        days_prior = service.endorsement_expiration_warning(level)
        if days_prior is None:
            continue

        if level == 1:
            endorsed = now - timedelta(
                days=service.endorsement_lifetime - days_prior)
            q = q | Q(datetime_endorsed__lt=endorsed,
                      datetime_notice_1_emailed__isnull=True,
                      category_code=service.category_code,
                      is_deleted__isnull=True)
        else:
            prev_days_prior = service.endorsement_expiration_warning(level - 1)
            prev_warning_date = now - timedelta(
                days=prev_days_prior - days_prior)

            if level == 2:
                q = q | Q(datetime_notice_1_emailed__lt=prev_warning_date,
                          datetime_notice_2_emailed__isnull=True,
                          category_code=service.category_code,
                          is_deleted__isnull=True)
            elif level == 3:
                q = q | Q(datetime_notice_2_emailed__lt=prev_warning_date,
                          datetime_notice_3_emailed__isnull=True,
                          category_code=service.category_code,
                          is_deleted__isnull=True)
            else:
                q = q | Q(datetime_notice_3_emailed__lt=prev_warning_date,
                          datetime_notice_4_emailed__isnull=True,
                          category_code=service.category_code,
                          is_deleted__isnull=True)

    return EndorsementRecord.objects.filter(q)


def endorsements_to_expire():
    """
    Return query set of endorsement records to expire
    """
    return _endorsements_to_expire(timezone.now())


def _endorsements_to_expire(now):
    """
    Return query set of endorsements to expire for each service
    """
    q = Q()

    for service in endorsement_services():
        expiration_date = now - timedelta(days=service.endorsement_graceperiod)
        q = q | Q(datetime_notice_4_emailed__lt=expiration_date,
                  datetime_notice_3_emailed__isnull=False,
                  datetime_notice_2_emailed__isnull=False,
                  datetime_notice_1_emailed__isnull=False,
                  category_code=service.category_code,
                  is_deleted__isnull=True)

    return EndorsementRecord.objects.filter(q)


def expire_endorsments(gracetime, lifetime):
    """
    """
    endorsements = endorsements_to_expire(gracetime, lifetime)
    if len(endorsements):
        for e in endorsements:
            clear_endorsement(e)
