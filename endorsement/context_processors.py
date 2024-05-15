# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
"""
from django.conf import settings
from endorsement.userservice_validation import can_override_user


def supporttools_globals(request):
    return {
        'is_support_admin': can_override_user(request),
        'support_group': getattr(
            settings, "PROVISION_SUPPORT_GROUP", "")
    }


def is_desktop(request):
    return {
        'is_desktop': (not (getattr(
            request, 'is_mobile', False) or getattr(
                request, 'is_tablet', False)))
    }
