from rest_framework.views import APIView
from django.http import HttpResponse
import json
import sys
from restclients_core.exceptions import DataFailureException,\
    InvalidNetID, InvalidRegID


from endorsement.util.log import log_exception,\
    log_data_not_found_response, log_data_error_response,\
    log_invalid_netid_response, log_invalid_endorser_response


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


def handle_exception(logger, stack_trace):
    log_exception(logger, stack_trace.format_exc())
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


def data_error(logger):
    log_data_error_response(logger)
    return RESTDispatch().error_response(
        543, "Data not available due to an error")
