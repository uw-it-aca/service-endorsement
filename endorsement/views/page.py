# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import traceback

from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from userservice.user import UserService

from endorsement.provisioner_validation import can_view_endorsements
from endorsement.services import is_valid_endorser, service_contexts
from endorsement.util.auth import is_support_user
from endorsement.views.rest_dispatch import handle_exception, invalid_session
from endorsement.views.session import log_session_key

logger = logging.getLogger(__name__)
LOGOUT_URL = "/user_logout"


@login_required
def index(request):
    try:
        user_service = UserService()
        netid = user_service.get_user()
        if not netid:
            return invalid_session(logger)

        session_key = log_session_key(request)
        context = {
            "home_url": "/",
            "err": None,
            "user": {
                "netid": netid,
                "session_key": session_key,
            },
            'services': json.dumps(service_contexts()),
            'override_user': user_service.get_override_user(),
            'support_override_user': is_support_user(request),
            'provisioning': getattr(
                settings, 'ENDORSEMENT_PROVISIONING', ['*'])
        }

        if not (is_valid_endorser(netid) and can_view_endorsements(request)):
            context["auth_failure"] = "provisioner"
            return render(request, "401.html", context, status=401)

        try:
            return render(request, "index.html", context)
        except Exception as ex:
            logger.error(f"{ex}")
    except Exception as ex:
        handle_exception(logger, f"{ex}", traceback)


def logout(request):
    # Expires current session
    django_logout(request)

    # Redirects to weblogin logout page
    return HttpResponseRedirect(LOGOUT_URL)
