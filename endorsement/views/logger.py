import logging
from django.http import HttpResponse
from endorsement.views import get_netid_of_current_user


_logger = logging.getLogger(__name__)


def log_interaction(request, interaction_type):
    if interaction_type is not None:
        _logger.info("%s: Interaction: %s" % (get_netid_of_current_user(),
                                              interaction_type))
    return HttpResponse()
