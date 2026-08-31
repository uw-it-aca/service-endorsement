# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import sys

from django.utils.timezone import get_default_timezone, is_naive, localtime, make_aware
from restclients_core.exceptions import DataFailureException, InvalidNetID

from endorsement.util.log import log_exception


def handel_err(logger, message, stacktrace):
    log_exception(logger, message, stacktrace)
    exc_type, exc_value, _exc_traceback = sys.exc_info()
    if isinstance(exc_value, InvalidNetID):
        return False
    if isinstance(exc_value, DataFailureException) and\
            exc_value.status in [404, 409]:
        return False
    raise exc_type(exc_value).with_traceback(_exc_traceback)


def display_datetime(dt):
    if is_naive(dt):
        dt = make_aware(dt, get_default_timezone())
    else:
        dt = localtime(dt)
    return dt.strftime("%B %d at %l:%M %p %Z")
