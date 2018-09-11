from django.core.urlresolvers import reverse
from django.test import TransactionTestCase, Client
from django.test.client import RequestFactory
from django.test.utils import override_settings
from userservice.user import UserServiceMiddleware
from endorsement.test import (
    get_user, get_user_pass,
    fdao_gws_override, fdao_pws_override, fdao_uwnetid_override)


VALIDATE = "endorsement.userservice_validation.validate"
OVERRIDE = "endorsement.userservice_validation.can_override_user"

Session = 'django.contrib.sessions.middleware.SessionMiddleware'
Common = 'django.middleware.common.CommonMiddleware'
CsrfView = 'django.middleware.csrf.CsrfViewMiddleware'
Auth = 'django.contrib.auth.middleware.AuthenticationMiddleware'
RemoteUser = 'django.contrib.auth.middleware.RemoteUserMiddleware'
Message = 'django.contrib.messages.middleware.MessageMiddleware'
XFrame = 'django.middleware.clickjacking.XFrameOptionsMiddleware'
UserService = 'userservice.user.UserServiceMiddleware'
AUTH_BACKEND = 'django.contrib.auth.backends.ModelBackend'
standard_test_override = override_settings(
    MIDDLEWARE_CLASSES=(Session,
                        Common,
                        CsrfView,
                        Auth,
                        RemoteUser,
                        Message,
                        XFrame,
                        UserService,),
    AUTHENTICATION_BACKENDS=(AUTH_BACKEND,))


@standard_test_override
class EndorsementApiTest(TransactionTestCase):

    def setUp(self):
        """
        By default enforce_csrf_checks is False
        """
        self.client = Client()
        self.request = RequestFactory().get("/")
        self.middleware = UserServiceMiddleware()

    def set_user(self, username):
        self.request.user = get_user(username)
        self.client.login(username=username,
                          password=get_user_pass(username))
        self.process_request()

    def process_request(self):
        self.request.session = self.client.session
        self.middleware.process_request(self.request)

    def set_userservice_override(self, username):
        with self.settings(DEBUG=False,
                           USERSERVICE_VALIDATION_MODULE=VALIDATE,
                           USERSERVICE_OVERRIDE_AUTH_MODULE=OVERRIDE):

            resp = self.client.post(reverse("userservice_override"),
                                    {"override_as": username})
            self.assertEquals(resp.status_code, 200)
            self.process_request()