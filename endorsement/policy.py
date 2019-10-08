from django.template import loader
from django.utils import timezone
from django.core.mail import mail_managers
from endorsement.models import EndorsementRecord
from endorsement.dao.endorse import clear_endorsement
from datetime import timedelta


# Expiration clock starts on the date of the first warning notice
#
# Expiration clock runs out gracetime days plus 7 days after the fourth notice
#
# Notices must be sent in sequence, at the specified interval
#   Notice #1: 90 days prior to end of lifetime
#   Notice #2: 30 days prior to end of lifetime
#   Notice #3: 7 days prior to end of lifetime
#   Notice #4: on the day of end of lifetime


DEFAULT_ENDORSEMENT_LIFETIME = 365
DEFAULT_ENDORSEMENT_GRACETIME = 90
NOTICE_1_DAYS_PRIOR = 90
NOTICE_2_DAYS_PRIOR = 30
NOTICE_3_DAYS_PRIOR = 7
NOTICE_4_DAYS_PRIOR = 0


def endorsements_to_warn(level, lifetime):
    """
    """
    return _endorsements_to_warn(timezone.now(), level, lifetime)


def _endorsements_to_warn(now, level, lifetime=DEFAULT_ENDORSEMENT_LIFETIME):
    """
    """
    filter = {
        'is_deleted__isnull': True
    }

    if level < 1 or level > 4:
        raise Exception('bad warning level {}'.format(level))

    # not already emailed
    filter['datetime_notice_{}_emailed__isnull'.format(level)] = True

    # and appropriate span between current notice level and previous
    if level == 1:
        filter['datetime_endorsed__lt'] = now - timedelta(
            days=lifetime - NOTICE_1_DAYS_PRIOR)
    elif level == 2:
        filter['datetime_notice_1_emailed__lt'] = now - timedelta(
            days=NOTICE_1_DAYS_PRIOR - NOTICE_2_DAYS_PRIOR)
    elif level == 3:
        filter['datetime_notice_2_emailed__lt'] = now - timedelta(
            days=NOTICE_2_DAYS_PRIOR - NOTICE_3_DAYS_PRIOR)
    else:
        filter['datetime_notice_3_emailed__lt'] = now - timedelta(
            days=NOTICE_3_DAYS_PRIOR - NOTICE_4_DAYS_PRIOR)

    return EndorsementRecord.objects.filter(**filter)


def endorsements_to_expire(gracetime):
    """
    """
    return _endorsements_to_expire(timezone.now(), gracetime)


def _endorsements_to_expire(now, gracetime=DEFAULT_ENDORSEMENT_GRACETIME):
    """
    """
    filter = {
        'is_deleted__isnull': True,
        'datetime_notice_1_emailed__isnull': False,
        'datetime_notice_2_emailed__isnull': False,
        'datetime_notice_3_emailed__isnull': False,
        'datetime_notice_4_emailed__lt':  now - timedelta(days=gracetime)
    }

    return EndorsementRecord.objects.filter(**filter)




def expire_endorsments(gracetime, lifetime):
    """
    """
    endorsements = endorsements_to_expire(gracetime, lifetime)
    if len(endorsements):
        for e in endorsements:
            clear_endorsement(e)
            logger.info('expire: {}'.format(e))
