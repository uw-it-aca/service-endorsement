# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from userservice.user import UserService
from endorsement.services import service_contexts
from endorsement.dao.gws import is_valid_endorser
from endorsement.views.session import log_session_key
from endorsement.views.rest_dispatch import invalid_session, handle_exception
import logging
import traceback
import json


logger = logging.getLogger(__name__)
LOGOUT_URL = "/user_logout"


@login_required
def index(request):
    try:
        netid = UserService().get_user()
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
            'services': json.dumps(service_contexts())
        }

        if not is_valid_endorser(netid):
            context["auth_failure"] = "provisioner"
            return render(request, "401.html", context, status=401)

        try:
            return render(request, "index.html", context)
        except Exception as ex:
            logger.error("{0}".format(ex))
    except Exception as ex:
        handle_exception(logger, "{}".format(ex), traceback)


def logout(request):
    # Expires current session
    django_logout(request)

    # Redirects to weblogin logout page
    return HttpResponseRedirect(LOGOUT_URL)
