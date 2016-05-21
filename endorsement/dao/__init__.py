from django.utils import timezone
from restclients.dao import PWS_DAO
from endorsement.models.user import User
from endorsement.dao.user import get_netid_of_current_user
from endorsement.dao.pws import get_regid


def get_user_model():
    user_netid = get_netid_of_current_user()
    user_regid = get_regid(user_netid)

    user, created = User.objects.get_or_create(
        uwnetid=user_netid,
        uwregid=user_regid,
        defaults={'last_visit': timezone.now()})

    return user


def is_using_file_dao():
    dao = PWS_DAO()._getDAO()
    class_name = dao.__class__.__name__
    return class_name == "File"
