import logging
import sys
from django.utils import timezone
from restclients.dao import PWS_DAO
from restclients.exceptions import InvalidNetID
from restclients.exceptions import DataFailureException
from endorsement.util.log import log_exception


def is_using_file_dao():
    dao = PWS_DAO()._getDAO()
    class_name = dao.__class__.__name__
    return class_name == "File"


def handel_err(logger, message, stacktrace):
    log_exception(logger, message, stacktrace)
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if isinstance(exc_value, InvalidNetID):
        return False
    if isinstance(exc_value, DataFailureException) and\
            exc_value.status == 404:
        return False
    raise
