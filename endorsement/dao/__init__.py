from restclients.dao import PWS_DAO
from endorsement.models.user import User
from endorsement.dao.user import get_netid_of_current_user


def get_user_model():
    user_netid = get_netid_of_current_user()

    user, created = User.objects.get_or_create(uwnetid=user_netid)

    return user


def is_using_file_dao():
    dao = PWS_DAO()._getDAO()
    class_name = dao.__class__.__name__
    return class_name == "File"
