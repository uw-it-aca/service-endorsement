from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.dao.gws import is_valid_endorser
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time
from endorsement.views.session import log_session_key
from endorsement.views.rest_dispatch import invalid_session, handle_exception
import logging
import traceback
import json


logger = logging.getLogger(__name__)
LOGOUT_URL = "/user_logout"


@login_required
def index(request):
    timer = Timer()
    try:
        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger, timer)

        session_key = log_session_key(request)
        context = {
            "home_url": "/",
            "err": None,
            "user": {
                "netid": netid,
                "session_key": session_key,
            }
        }

        choices = dict(EndorsementRecord.CATEGORY_CODE_CHOICES)
        context['services'] = json.dumps({
            'o365': {
                'category': EndorsementRecord.OFFICE_365_ENDORSEE,
                'name': choices[EndorsementRecord.OFFICE_365_ENDORSEE]
            },
            'google': {
                'category': EndorsementRecord.GOOGLE_SUITE_ENDORSEE,
                'name': choices[EndorsementRecord.GOOGLE_SUITE_ENDORSEE]
            },
            'canvas': {
                'category': EndorsementRecord.CANVAS_PROVISIONEE,
                'name': choices[EndorsementRecord.CANVAS_PROVISIONEE]
            }
        })

        if not is_valid_endorser(netid):
            context["auth_failure"] = "provisioner"
            return render(request, "401.html", context, status=401)

        try:
            log_resp_time(logger, "index.html", timer)
            return render(request, "index.html", context)
        except Exception as ex:
            logger.error("{0}".format(ex))
    except Exception:
        handle_exception(logger, timer, traceback)


def logout(request):
    timer = Timer()
    # Expires current session
    django_logout(request)

    # Redirects to weblogin logout page
    log_resp_time(logger, "logout", timer)
    return HttpResponseRedirect(LOGOUT_URL)
