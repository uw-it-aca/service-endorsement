# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.contrib.auth.models import User
from uw_gws.utilities import fdao_gws_override  # noqa: F401
from uw_pws.util import fdao_pws_override  # noqa: F401
from uw_uwnetid.util import fdao_uwnetid_override  # noqa: F401


def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except Exception:
        user = User.objects.create_user(username, password='pass')
        return user


def get_user_pass(username):
    return 'pass'
