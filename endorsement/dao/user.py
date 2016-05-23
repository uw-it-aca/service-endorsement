import logging
from endorsement.models.user import Endorser, Endorsee
from endorsement.dao import get_netid_of_current_user
from endorsement.dao.pws import get_regid
from endorsement.dao.uwnetid_subscription_60 import is_staff, is_faculty


logger = logging.getLogger(__name__)


def get_endorser_model():
    user_netid = get_netid_of_current_user()

    user, created = Endorser.objects.get_or_create(
        uwnetid=user_netid,
        uwregid=get_regid(user_netid),
        is_staff=is_staff(user_netid),
        is_faculty=is_faculty(user_netid),
        defaults={'last_visit': timezone.now()}
        )

    return user


def get_endorsee_model(user_netid):
    user_regid = get_regid(user_netid)

    user, created = Endorsee.objects.get_or_create(
        uwnetid=user_netid,
        uwregid=user_regid
        )

    return user
