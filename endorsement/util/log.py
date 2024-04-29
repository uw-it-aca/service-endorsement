# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

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


def log_invalid_netid_response(logger):
    logger.error("{}".format('Invalid netid, abort'))


def log_err_with_netid(logger, message):
    logger.error("{}".format(add_user_info(message)))


def log_invalid_endorser_response(logger):
    log_err_with_netid(logger, 'Invalid endorser, abort')


def log_data_error_response(logger, ex):
    log_err_with_netid(logger,
                       ('Data not available due to'
                        ' a backend error "{}", abort').format(ex))


def log_data_not_found_response(logger):
    log_err_with_netid(logger, 'Data not found')


def log_bad_request_response(logger):
    log_err_with_netid(logger, 'Data not found')
