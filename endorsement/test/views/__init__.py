# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest2 import skipIf
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from userservice.user import UserServiceMiddleware


def _missing_url(name, kwargs=None):
    try:
        reverse(name, kwargs=kwargs)
    except Exception as ex:
        print("Ex: {0}".format(ex))
        return True

    return False


def require_url(url, message, kwargs=None):
    return skipIf(_missing_url(url, kwargs), message)


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


AUTH_BACKEND = 'django.contrib.auth.backends.ModelBackend'
AUTH_GROUP = 'authz_group.authz_implementation.all_ok.AllOK'


view_test_override = override_settings(
    AUTHENTICATION_BACKENDS=(AUTH_BACKEND,),
    AUTHZ_GROUP_BACKEND=AUTH_GROUP,
    USERSERVICE_ADMIN_GROUP="x",
    MIDDLEWARE_CLASSES=(
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.PersistentRemoteUserMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django_mobileesp.middleware.UserAgentDetectionMiddleware',
        'userservice.user.UserServiceMiddleware',
        ),
)


@view_test_override
class TestViewApi(TestCase):

    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')

    def _set_user(self, netid):
        get_user(netid)
        self.client.login(username=netid,
                          password=get_user_pass(netid))

    def get_request(self, url, netid):
        self._set_user(netid)
        request = RequestFactory().get(url)
        request.user = get_user(netid)
        SessionMiddleware().process_request(request)
        request.session = self.client.session
        request.session['samlUserdata'] = settings.MOCK_SAML_ATTRIBUTES if (
            netid == 'jstaff') else {
                'uwnetid': netid,
                'affiliations': ['student', 'staff', 'employee'],
                'isMemberOf': ['u_test_group', 'u_test_another_group']}
        UserServiceMiddleware().process_request(request)
        request.session.save()

        return request

    def get_response(self, url_name, **kwargs):
        url = reverse(url_name)
        return self.client.get(url, **kwargs)

    def post_response(self, url_name, body, **kwargs):
        url = reverse(url_name, **kwargs)
        return self.client.post(
            url, data=body, content_type="application/json")
