import re
import logging
import traceback
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.template import RequestContext
from django.conf import settings
from django.views.decorators.cache import cache_control
from userservice.user import UserService
from myuw.util.time_helper import Timer
from myuw.util.log import log_exception,\
    log_exception_with_timer, log_success_resp,\
    log_invalid_netid_response, log_session
from myuw.views.rest_dispatch import invalid_session


logger = logging.getLogger(__name__)
LOGOUT_URL = "/user_logout"


@login_required
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def index(request):
    timer = Timer()
    netid = UserService().get_user()
    if not netid:
        log_invalid_netid_response(logger, timer)
        return invalid_session()
    session_key = request.session.session_key
    log_session(logger, session_key)

    context = {
        "home_url": "/",
        "err": None,
        "user": {
            "netid": netid,
            "session_key": session_key
        },
    }
    log_resp_time(logger, timer, "/")
    return render_to_response("index.html",
                              context,
                              context_instance=RequestContext(request))


def logout(request):
    # Expires current session
    django_logout(request)

    # Redirects to weblogin logout page
    return HttpResponseRedirect(LOGOUT_URL)
