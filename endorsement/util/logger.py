import logging
import json
import hashlib
from restclients.util.log import log_info, log_err
from endorsement.dao.uwnetid_subscription_60 import get_user_affiliations


def log_session(logger, session_key):
    if session_key is None:
        session_key = ''

    session_hash = hashlib.md5(session_key).hexdigest()
    log_entry = get_user_affiliations()
    log_entry['session_key'] = session_hash
    logger.info(json.dumps(log_entry))


def add_user_info(message):
    try:
        return "%s - %s" % (get_user_affiliations(), message)
    except Exception:
        return message


def log_exception(logger, message, exc_info):
    """
    exc_info is a string containing
    the full stack trace, the exception type and value
    """
    logger.error("%s => %s",
                 add_user_info(message), exc_info.splitlines())


def log_exception_with_timer(logger, timer, exc_info):
    log_err(logger, add_user_info(exc_info.splitlines()), timer)


def log_resp_time(logger, message, timer):
    log_info(logger, add_user_info(message), timer)


def log_success_resp(logger, timer):
    log_resp_time(logger, 'fulfilled', timer)


def log_data_not_found_response(logger, timer):
    log_resp_time(logger, 'Data not found', timer)


def log_invalid_netid_response(logger, timer):
    log_resp_time(logger, 'Invalid netid, abort', timer)


def log_invalid_identity_response(logger, timer):
    log_resp_time(logger, 'Not qualified, abort', timer)


def log_invalid_regid_response(logger, timer):
    log_resp_time(logger, 'Invalid regid, abort', timer)
