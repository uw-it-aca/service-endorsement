# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from rest_framework.views import APIView
from django.http import HttpResponse
from userservice.user import UserService
from endorsement.exceptions import UnrecognizedUWNetid, InvalidNetID
from endorsement.util.auth import is_admin_user
import json
import sys
from restclients_core.exceptions import DataFailureException,\
    InvalidNetID, InvalidRegID
from endorsement.util.log import (
    log_exception, log_data_not_found_response, log_data_error_response,
    log_invalid_netid_response, log_invalid_endorser_response,
    log_bad_request_response)


class RESTDispatch(APIView):
    def error_response(self, status, message='', content={}):
        content['error'] = '{0}'.format(message)
        return HttpResponse(json.dumps(content),
                            status=status,
                            content_type='application/json')

    def json_response(self, content='', status=200):
        return HttpResponse(json.dumps(content, sort_keys=True),
                            status=status,
                            content_type='application/json')

    def _validate_user(
            self, request, valid_act_as=is_admin_user, logger=None):
        user_service = UserService()
        netid = user_service.get_user()
        if not netid:
            raise UnrecognizedUWNetid()

        original_user = user_service.get_original_user()
        acted_as = None if (netid == original_user) else original_user
        if acted_as:
            if valid_act_as(request):
                if logger:
                    logger.info(f"User: {netid}, Acted as: {acted_as}")
            else:
                raise InvalidNetID()

        return netid, acted_as


def handle_exception(logger, message, stack_trace):
    log_exception(logger, message, stack_trace.format_exc())
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if (isinstance(exc_value, InvalidNetID) or
            isinstance(exc_value, InvalidRegID)):
        return invalid_session(logger)
    if (isinstance(exc_value, DataFailureException) and
            exc_value.status == 404):
        return data_not_found(logger)
    return data_error(logger)


def invalid_method():
    return RESTDispatch().error_response(405, "Method not allowed")


def invalid_session(logger):
    log_invalid_netid_response(logger)
    return RESTDispatch().error_response(400, "No valid userid in session")


def invalid_endorser(logger):
    log_invalid_endorser_response(logger)
    return RESTDispatch().error_response(401, "Invalid endorser")


def data_not_found(logger):
    log_data_not_found_response(logger)
    return RESTDispatch().error_response(404, "Data not found")


def bad_request(logger, msg="Bad request"):

    import pdb; pdb.set_trace()

    log_bad_request_response(logger)
    return RESTDispatch().error_response(400, msg)


def data_error(logger, msg):
    log_data_error_response(logger, msg)
    return RESTDispatch().error_response(
        543, "Data not available due to an error")
