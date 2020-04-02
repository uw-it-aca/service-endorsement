from django.conf import settings
from uw_saml.utils import is_member_of_group
from rest_framework import authentication


class AdminGroupAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        return (request.user, None) if is_member_of_group(
            request, settings.PROVISION_ADMIN_GROUP) else None
