import logging
from django.utils import timezone
from django.db import IntegrityError, transaction
from endorsement.models.user import Endorser, Endorsee
from endorsement.dao.pws import get_regid
from endorsement.dao.gws import is_valid_endorser


logger = logging.getLogger(__name__)


def get_endorser_model(uwnetid):
    """
    return an Endorser object
    @exception: DataFailureException
    """
    uwregid = get_regid(uwnetid)
    updated_values = {'netid': uwnetid,
                      'is_valid': is_valid_endorser(uwnetid),
                      'last_visit': timezone.now()
                      }
    user, created = Endorser.objects.update_or_create(
        regid=uwregid,
        defaults=updated_values)

    return user


def get_endorsee_model(uwnetid):
    """
    return an Endorsee object
    @exception: DataFailureException
    """
    uwregid = get_regid(uwnetid)
    user, created = Endorsee.objects.get_or_create(
        regid=uwregid,
        defaults={'netid': uwnetid},
        )

    return user
