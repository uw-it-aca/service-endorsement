import logging
import traceback
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth import logout as django_logout
from django.template import RequestContext
from django.contrib.auth.models import User
from restclients.exceptions import DataFailureException
from userservice.user import UserService
from endorsement.dao.user import get_endorser_model
from endorsement.dao.gws import is_valid_endorser
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time
from endorsement.views.session import log_session_key
from endorsement.views.rest_dispatch import invalid_session,\
    invalid_endorser, handle_exception


logger = logging.getLogger(__name__)
OGOUT_URL = "/user_logout"


@login_required
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def index(request):
    timer = Timer()
    try:
        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger, timer)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger, timer)
        session_key = log_session_key(request)

        user, created = get_endorser_model(netid)

        context = {
            "home_url": "/",
            "err": None,
            "user": {
                "netid": netid,
                "session_key": session_key,
                },
            }
        log_resp_time(logger, "index.html", timer)
        return render(request, "index.html", context)
    except Exception:
        handle_exception(logger, timer, traceback)


def logout(request):
    timer = Timer()
    # Expires current session
    django_logout(request)

    # Redirects to weblogin logout page
    log_resp_time(logger, "logout", timer)
    return HttpResponseRedirect(LOGOUT_URL)
