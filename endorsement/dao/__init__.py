from django.utils import timezone
from restclients.dao import PWS_DAO
from userservice.user import UserService


def is_using_file_dao():
    dao = PWS_DAO()._getDAO()
    class_name = dao.__class__.__name__
    return class_name == "File"


def get_netid_of_current_user():
    return UserService().get_user()


def get_override_user():
    return UserService().get_override_user()


def get_original_user():
    return UserService().get_original_user()
