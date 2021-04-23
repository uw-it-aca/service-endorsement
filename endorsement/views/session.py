# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
import hashlib
import json
import logging
from userservice.user import get_original_user, get_override_user

logger = logging.getLogger(__name__)


def log_session_key(request):
    session_key = request.session.session_key
    if session_key is None:
        session_key = ''
    session_hash = hashlib.md5(session_key.encode('utf-8')).hexdigest()
    log_entry = _get_user(request)
    log_entry['session_key'] = session_hash
    logger.info(json.dumps(log_entry))
    return session_key


def _get_user(request):
    actual_userid = get_original_user(request)
    override_userid = get_override_user(request)
    log_userid = {'user': actual_userid}
    if override_userid:
        log_userid['override-as'] = override_userid
    return log_userid
