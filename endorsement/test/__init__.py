from django.contrib.auth.models import User
from uw_gws.utilities import fdao_gws_override
from uw_pws.util import fdao_pws_override
from uw_uwnetid.util import fdao_uwnetid_override


def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except Exception as ex:
        user = User.objects.create_user(username, password='pass')
        return user


def get_user_pass(username):
    return 'pass'
