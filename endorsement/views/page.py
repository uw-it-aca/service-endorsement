import logging
import traceback
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.template import RequestContext
from django.conf import settings
from django.views.decorators.cache import cache_control
from restclients.exceptions import DataFailureException
from endorsement.dao.user import get_endorser_model
from endorsement.dao.uwnetid_subscription_60 import is_valid_endorser
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_session, log_success_resp
from endorsement.views import get_netid_of_current_user
from endorsement.views.rest_dispatch import invalid_session,\
    invalid_endorser, handle_exception


LOGOUT_URL = "/user_logout"
logger = logging.getLogger(__name__)


#@login_required
#@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def index(request):
    timer = Timer()
    try:
        netid = get_netid_of_current_user()
        if not netid:
            return invalid_session(logger, timer)

        try:
            if not is_valid_endorser(netid):
                return invalid_endorser(logger, timer)
        except DataFailureException as ex:
            if ex.status == 404:
                return invalid_endorser(logger, timer)
            raise

        session_key = request.session.session_key
        if not HttpRequest.session['netid']:
            HttpRequest.session['netid'] = netid
            log_session(logger, session_key)
            user = get_endorser_model(netid)

        context = {"home_url": "/",
                   "err": None,
                   "user": {'netid': netid},
                   }
        context["user"]["session_key"] = session_key
        log_resp_time(logger, timer, context)
        return render_to_response("index.html",
                                  context,
                                  context_instance=RequestContext(request))
    except Exception:
        handle_exception(logger, timer, traceback)


def logout(request):
    # Expires current session
    django_logout(request)

    # Redirects to weblogin logout page
    return HttpResponseRedirect(LOGOUT_URL)
