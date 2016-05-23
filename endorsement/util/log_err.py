import logging
import json
import hashlib
from restclients.util.log import log_err
from endorsement.dao import get_netid_of_current_user


def _add_user_netid(message):
    try:
        return "%s - %s" % (get_netid_of_current_user(), message)
    except Exception:
        return message


def log_exception(logger, message, exc_info):
    """
    exc_info is a string containing
    the full stack trace, the exception type and value
    """
    logger.error("%s => %s",
                 _add_user_netid(message), exc_info.splitlines())


def log_exception_with_timer(logger, timer, exc_info):
    log_err(logger, _add_user_info(exc_info.splitlines()), timer)
