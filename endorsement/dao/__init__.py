from django.utils import timezone
from restclients.dao import PWS_DAO


def is_using_file_dao():
    dao = PWS_DAO()._getDAO()
    class_name = dao.__class__.__name__
    return class_name == "File"
