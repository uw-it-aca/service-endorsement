import logging
from endorsement.models.user import Endorser, Endorsee
from endorsement.dao.pws import get_regid
from endorsement.dao.uwnetid_subscription_60 import is_current_staff,\
    is_current_faculty


logger = logging.getLogger(__name__)


def get_endorser_model(uwnetid):
    """
    return an Endorser object
    @exception: DataFailureException
    """
    user, created = Endorser.objects.get_or_create(
        netid=uwnetid,
        regid=get_regid(uwnetid),
        is_staff=is_current_staff(uwnetid),
        is_faculty=is_current_faculty(uwnetid),
        defaults={'last_visit': timezone.now()},
        )

    return user


def get_endorsee_model(uwnetid):
    """
    return an Endorsee object
    @exception: DataFailureException
    """
    user, created = Endorsee.objects.get_or_create(
        netid=user_netid,
        regid=get_regid(uwnetid),
        )

    return user
