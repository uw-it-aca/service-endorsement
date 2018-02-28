import sys
from uw_pws.dao import PWS_DAO
from restclients_core.exceptions import (
    DataFailureException, InvalidNetID)
from endorsement.util.log import log_exception
from django.utils.timezone import (
    get_default_timezone, localtime, is_naive, make_aware)


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


def display_datetime(dt):
    if is_naive(dt):
        dt = make_aware(dt, get_default_timezone())
    else:
        dt = localtime(dt)
    return dt.strftime("%B %d at %l:%M %p %Z")
