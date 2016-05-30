import hashlib
import json
import logging
from restclients.util.log import log_err, log_info
from userservice.user import UserService
from endorsement.dao.uwnetid_subscription_60 import is_current_staff,\
    is_current_faculty


def _get_user_affiliations():
    uwnetid = UserService().get_user()
    return {'netid': uwnetid,
            'is_staff': is_current_staff(uwnetid),
            'is_faculty': is_current_faculty(uwnetid)
            }


def log_session(logger, session_key):
    if session_key is None:
        session_key = ''
    session_hash = hashlib.md5(session_key).hexdigest()
    log_entry = _get_user_affiliations()
    log_entry['session_key'] = session_hash
    logger.info(json.dumps(log_entry))


def _add_user_netid(message):
    try:
        return "%s - %s" % (UserService().get_user(), message)
    except Exception:
        return message


def log_exception(logger, message, exc_info):
    """
    exc_info is a string containing the full stack trace,
    including the exception type and value
    """
    logger.error("%s => %s",
                 _add_user_netid(message), exc_info.splitlines())


def log_invalid_netid_response(logger, timer):
    log_err(logger, 'Invalid netid, abort', timer)


def log_err_with_netid(logger, timer, message):
    log_err(logger, _add_user_netid(message), timer)


def log_exception_with_timer(logger, timer, exc_info):
    log_err_with_netid(logger, timer, exc_info.splitlines())


def log_invalid_identity_response(logger, timer):
    log_err_with_netid(logger, timer, 'Not qualified, abort')


def log_invalid_regid_response(logger, timer):
    log_err_with_netid(logger, timer, 'Invalid regid, abort')


def log_data_error_response(logger, timer):
    log_err_with_netid(logger, timer,
                       'Data not available due to a backend error, abort')


def _add_user_info(message):
    try:
        return "%s - %s" % (json.dumps(_get_user_affiliations()), message)
    except Exception:
        return message


def log_resp_time(logger, message, timer):
    log_info(logger, _add_user_info(message), timer)


def log_success_resp(logger, timer):
    log_resp_time(logger, 'fulfilled', timer)


def log_data_not_found_response(logger, timer):
    log_resp_time(logger, 'Data not found', timer)
