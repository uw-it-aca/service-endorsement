import logging
from django.http import HttpResponse
from endorsement.util.log import add_user_info


_logger = logging.getLogger(__name__)


def log_interaction(request, interaction_type):
    if interaction_type is not None:
        _logger.info(add_user_info(": Interaction: %s" % interaction_type))
    return HttpResponse()
