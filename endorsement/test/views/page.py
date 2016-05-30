from unittest2 import skipIf
from django.conf import settings
from django.test import Client
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from endorsement.util.log import log_session
from endorsement.test.views import missing_url, get_user, get_user_pass
from userservice.user import get_original_user


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


@override_settings(
    AUTHENTICATION_BACKENDS = (AUTH_BACKEND,),
    USERSERVICE_ADMIN_GROUP = "x",
    AUTHZ_GROUP_BACKEND = AUTH_GROUP,
    MIDDLEWARE_CLASSES = (Session,
                          Common,
                          CsrfView,
                          Auth,
                          RemoteUser,
                          Message,
                          XFrame,
                          UserService,
                          ),
    )
class TestPage(TestCase):

    @skipIf(missing_url("home"), "home urls not configured")
    def test_err_cases(self):
        c = Client()

        user = get_user('jnone')
        c.login(username='jnone',
                password=get_user_pass('jnone'))

        request = RequestFactory().get("/")
        request.session = c.session
        request.user = user
        self.assertEquals(get_original_user(request), 'jnone')

        response = c.get(reverse("home"),
                         HTTP_USER_AGENT='Fake Android Agent')
        self.assertEquals(response.status_code, 401)

    @skipIf(missing_url("home"), "home urls not configured")
    def test_normal_cases(self):
        c = Client()

        user = get_user('jstaff')
        c.login(username='jstaff',
                password=get_user_pass('jstaff'))

        request = RequestFactory().get("/")
        request.session = c.session
        request.user = user
        self.assertEquals(get_original_user(request), 'jstaff')

        response = c.get(reverse("home"),
                         HTTP_USER_AGENT='Fake Android Agent')
        self.assertEquals(response.status_code, 200)
