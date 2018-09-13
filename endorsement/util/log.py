import json
from logging import getLogger
from userservice.user import UserService


logger = getLogger


def _get_user():
    user_svc = UserService()
    override_userid = user_svc.get_override_user()
    actual_userid = user_svc.get_original_user()
    log_userid = {'user': actual_userid}
    if override_userid:
        log_userid['override-as'] = override_userid
    return log_userid


def add_user_info(message):
    try:
        return "{0} - {1}".format(json.dumps(_get_user()), message)
    except Exception:
        return message


def log_exception(logger, message, exc_info):
    """
    exc_info is a string containing the full stack trace,
    including the exception type and value
    """
    logger.error("{0} => {1}".format(
        add_user_info(message), exc_info.splitlines()))


def log_invalid_netid_response(logger, timer):
    logger.error("{0} {1}".format('Invalid netid, abort', timer))


def log_err_with_netid(logger, timer, message):
    logger.error("{0} {1}".format(add_user_info(message), timer))


def log_exception_with_timer(logger, timer, exc_info):
    log_err_with_netid(logger, timer, exc_info.splitlines())


def log_invalid_endorser_response(logger, timer):
    log_err_with_netid(logger, timer, 'Invalid endorser, abort')


def log_data_error_response(logger, timer):
    log_err_with_netid(logger, timer,
                       'Data not available due to a backend error, abort')


def log_resp_time(logger, message, timer):
    logger.info("{0} {1}".format(add_user_info(message), timer))


def log_data_not_found_response(logger, timer):
    log_resp_time(logger, 'Data not found', timer)
