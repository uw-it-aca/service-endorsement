# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django import template
from django.conf import settings
from uw_saml.utils import is_member_of_group


def set_admin_wrapper_template(context):
    try:
        extra_template = "userservice/user_override_extra_info.html"
        template.loader.get_template(extra_template)
        context['has_extra_template'] = True
        context['extra_template'] = 'userservice/user_override_extra_info.html'
    except template.TemplateDoesNotExist:
        # This is a fine exception - there doesn't need to be an extra info
        # template
        pass

    try:
        template.loader.get_template("userservice/user_override_wrapper.html")
        context['wrapper_template'] = 'userservice/user_override_wrapper.html'
    except template.TemplateDoesNotExist:
        context['wrapper_template'] = 'support_wrapper.html'
        # This is a fine exception - there doesn't need to be an extra info
        # template
        pass


def can_manage_persistent_messages(request):
    return is_member_of_group(request, settings.PROVISION_ADMIN_GROUP)
