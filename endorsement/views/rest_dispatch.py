import logging
import json
import sys
from django.http import HttpResponse
from django.conf import settings
from userservice.user import UserService
from restclients_core.exceptions import DataFailureException,\
    InvalidNetID, InvalidRegID
from endorsement.util.log import log_exception_with_timer,\
    log_data_not_found_response, log_data_error_response,\
    log_invalid_netid_response, log_invalid_endorser_response


class RESTDispatch:
    """
    Handles passing on the request to the correct view
    method based on the request type.
    """
    def run(self, *args, **named_args):
        request = args[0]

        netid = UserService().get_user()
        if not netid:
            return invalid_session()

        if "GET" == request.META['REQUEST_METHOD']:
            if hasattr(self, "GET"):
                return self.GET(*args, **named_args)
            else:
                return invalid_method()
        elif "POST" == request.META['REQUEST_METHOD']:
            if hasattr(self, "POST"):
                return self.POST(*args, **named_args)
            else:
                return invalid_method()
        elif "PUT" == request.META['REQUEST_METHOD']:
            if hasattr(self, "PUT"):
                return self.PUT(*args, **named_args)
            else:
                return invalid_method()
        elif "DELETE" == request.META['REQUEST_METHOD']:
            if hasattr(self, "DELETE"):
                return self.DELETE(*args, **named_args)
            else:
                return invalid_method()

        else:
            return invalid_method()


def handle_exception(logger, timer, stack_trace):
    log_exception_with_timer(logger, timer, stack_trace.format_exc())
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if isinstance(exc_value, InvalidNetID) or\
            isinstance(exc_value, InvalidRegID):
        return invalid_session(logger, timer)
    if isinstance(exc_value, DataFailureException) and\
            exc_value.status == 404:
        return data_not_found(logger, timer)
    return data_error(logger, timer)


def _make_response(status_code, reason_phrase):
    response = HttpResponse(reason_phrase)
    response.status_code = status_code
    response.reason_phrase = reason_phrase
    return response


def invalid_method():
    return _make_response(405, "Method not allowed")


def invalid_session(logger, timer):
    log_invalid_netid_response(logger, timer)
    return _make_response(400, "No valid userid in session")


def invalid_endorser(logger, timer):
    log_invalid_endorser_response(logger, timer)
    return _make_response(401, "Invalid endorser")


def data_not_found(logger, timer):
    log_data_not_found_response(logger, timer)
    return _make_response(404, "Data not found")


def data_error(logger, timer):
    log_data_error_response(logger, timer)
    return _make_response(543, "Data not available due to an error")
