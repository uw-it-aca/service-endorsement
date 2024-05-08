# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Office Mailbox Access lifecycle policy

Basic notions:
  * Intial and subsequent warnings are sent prior to expiration.
  * The expiration clock starts on the date of the first warning notice.
"""
from django.utils import timezone
from django.db.models import Q
from endorsement.models import AccessRecord
from endorsement.dao.access import revoke_access
from datetime import timedelta


# Default lifecycle day counts
DEFAULT_ACCESS_LIFETIME = 365
DEFAULT_ACCESS_GRACETIME = 90
PRIOR_DAYS_NOTICE_WARNING_1 = 90
PRIOR_DAYS_NOTICE_WARNING_2 = 30
PRIOR_DAYS_NOTICE_WARNING_3 = 7
PRIOR_DAYS_NOTICE_WARNING_4 = 0


def accessees_to_warn(level):
    """
    """
    return _accessees_to_warn(timezone.now(), level)


def _accessees_to_warn(now, level):
    """
    Gather records to receive expiration warning messages where
    level is the index of the warning message: first, second and so forth

    The expiration clock starts on the date of the first warning notice
    """
    if level < 1 or level > 4:
        raise Exception('bad warning level {}'.format(level))

    q = Q()

    # select on appropriate time span for warning notice index (level)
    days_prior = _expiration_warning(level)
    if days_prior is None:
        return

    if level == 1:
        granted = now - timedelta(
            days=DEFAULT_ACCESS_LIFETIME - days_prior)
        q = q | Q(datetime_granted__lt=granted,
                  datetime_notice_1_emailed__isnull=True,
                  is_deleted__isnull=True)
    else:
        prev_days_prior = _expiration_warning(level - 1)
        prev_warning_date = now - timedelta(
            days=prev_days_prior - days_prior)

        if level == 2:
            q = q | Q(datetime_notice_1_emailed__lt=prev_warning_date,
                      datetime_notice_2_emailed__isnull=True,
                      is_deleted__isnull=True)
        elif level == 3:
            q = q | Q(datetime_notice_2_emailed__lt=prev_warning_date,
                      datetime_notice_3_emailed__isnull=True,
                      is_deleted__isnull=True)
        else:
            q = q | Q(datetime_notice_3_emailed__lt=prev_warning_date,
                      datetime_notice_4_emailed__isnull=True,
                      is_deleted__isnull=True)

    return AccessRecord.objects.filter(q)


def access_to_expire():
    """
    Return query set of access records to expire
    """
    return _access_to_expire(timezone.now())


def _access_to_expire(now):
    """
    Return query set of accees to expire for each service
    """
    q = Q()

    expiration_date = now - timedelta(days=DEFAULT_ACCESS_GRACETIME)
    q = q | Q(datetime_notice_4_emailed__lt=expiration_date,
              datetime_notice_3_emailed__isnull=False,
              datetime_notice_2_emailed__isnull=False,
              datetime_notice_1_emailed__isnull=False,
              is_deleted__isnull=True)

    return AccessRecord.objects.filter(q)


def expire_office_access(gracetime, lifetime):
    """
    """
    access = access_to_expire(gracetime, lifetime)
    if len(access):
        for a in acccess:
            revoke_access(a)


def _expiration_warning(self, level=1):
    """
    for the given warning message level, return days prior to
    expiration that a warning should be sent.
    
    level 1 is the first warning, level 2 the second and so on
    to final warning at 0 days before expiration
    """
    try:
        return [
            PRIOR_DAYS_NOTICE_WARNING_1,
            PRIOR_DAYS_NOTICE_WARNING_2,
            PRIOR_DAYS_NOTICE_WARNING_3,
            PRIOR_DAYS_NOTICE_WARNING_4
        ][level - 1]
    except IndexError:
        return None
