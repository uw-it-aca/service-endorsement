import logging
from endorsement.util.log import log_session


logger = logging.getLogger(__name__)


def log_session_key(request):
    session_key = request.session.session_key
    log_session(logger, session_key)
    return session_key
