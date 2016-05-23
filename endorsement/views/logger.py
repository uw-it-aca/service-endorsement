from django.http import HttpResponse
import logging
from endorsement.dao import get_netid_of_current_user


logger = logging.getLogger(__name__)


def log_interaction(request, interaction_type):
    if interaction_type is not None:
        logger.info("%s: Interaction: %s" % (get_netid_of_current_user(),
                                             interaction_type))
    return HttpResponse()
