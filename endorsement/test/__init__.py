from django.contrib.auth.models import User
from django.test.client import RequestFactory
from userservice.user import UserServiceMiddleware
from uw_gws.utilities import fdao_gws_override
from uw_pws.util import fdao_pws_override
from uw_uwnetid.util import fdao_uwnetid_override


def get_request():
    """
    mock request with UserServiceMiddleware initialization
    """
    now_request = RequestFactory().get("/")
    now_request.session = {}
    UserServiceMiddleware().process_request(now_request)
    return now_request


def get_request_with_user(username, now_request=None):
    if now_request is None:
        now_request = get_request()
    now_request.user = get_user(username)
    UserServiceMiddleware().process_request(now_request)
    return now_request


def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except Exception as ex:
        user = User.objects.create_user(username, password='pass')
        return user


def get_user_pass(username):
    return 'pass'
