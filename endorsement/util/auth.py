# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.conf import settings
from django.contrib.auth.models import User
from uw_saml.utils import is_member_of_group, get_user
from rest_framework import authentication, exceptions


class AdminGroupAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if is_member_of_group(request, settings.PROVISION_ADMIN_GROUP):
            try:
                user = User.objects.get(username=get_user(request))
                return (user, None)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed('No such user')

        raise exceptions.AuthenticationFailed('Insufficent privilege')
