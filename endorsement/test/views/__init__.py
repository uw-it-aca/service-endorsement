from unittest2 import skipIf
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import Client
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings


def _missing_url(name):
    try:
        url = reverse(name)
    except Exception as ex:
        print "Ex: ", ex
        return True

    return False


def require_url(url, message):
    return skipIf(_missing_url(url), message)


def get_user(netid):
    try:
        user = User.objects.get(username=netid)
        return user
    except Exception as ex:
        user = User.objects.create_user(
            netid, password=get_user_pass(netid))
        return user


def get_user_pass(netid):
    return 'pass'


Session = 'django.contrib.sessions.middleware.SessionMiddleware'
Common = 'django.middleware.common.CommonMiddleware'
CsrfView = 'django.middleware.csrf.CsrfViewMiddleware'
Auth = 'django.contrib.auth.middleware.AuthenticationMiddleware'
RemoteUser = 'django.contrib.auth.middleware.RemoteUserMiddleware'
Message = 'django.contrib.messages.middleware.MessageMiddleware'
XFrame = 'django.middleware.clickjacking.XFrameOptionsMiddleware'
UserService = 'userservice.user.UserServiceMiddleware'
AUTH_BACKEND = 'django.contrib.auth.backends.ModelBackend'
AUTH_GROUP = 'authz_group.authz_implementation.all_ok.AllOK'


view_test_override = override_settings(
    AUTHENTICATION_BACKENDS=(AUTH_BACKEND,),
    AUTHZ_GROUP_BACKEND=AUTH_GROUP,
    USERSERVICE_ADMIN_GROUP="x",
    MIDDLEWARE_CLASSES=(Session,
                        Common,
                        CsrfView,
                        Auth,
                        RemoteUser,
                        Message,
                        XFrame,
                        UserService,
                        ),
    )


@view_test_override
class TestViewApi(TestCase):

    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')

    def set_user(self, netid):
        get_user(netid)
        self.client.login(username=netid,
                          password=get_user_pass(netid))

    def get_request(self, url, netid):
        self.set_user(netid)
        request = RequestFactory().get(url)
        request.user = get_user(netid)
        request.session = self.client.session
        return request

    def get_response(self, url_name, **kwargs):
        url = reverse(url_name)
        return self.client.get(url, **kwargs)
