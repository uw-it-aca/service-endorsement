from django.conf import settings
from uw_pws import PWS
from uw_saml.utils import is_member_of_group


def validate(username):
    if len(username) == 0:
        return "No override user supplied"

    if not (PWS().valid_uwnetid(username) and len(username) <= 64):
        return "Invalid UWNetID"

    return None


def can_override_user(request):
    """
    Return True if the original user has impersonate permission
    """
    return is_member_of_group(request,
                              getattr(settings, "PROVISION_ADMIN_GROUP",
                                      'u_acadev_provision_support'))
