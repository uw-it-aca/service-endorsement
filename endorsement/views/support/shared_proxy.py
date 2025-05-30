# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from uw_saml.decorators import group_required
from endorsement.views.support import set_admin_wrapper_template
from string import ascii_uppercase


@method_decorator(login_required, name='dispatch')
@method_decorator(group_required(settings.PROVISION_ADMIN_GROUP),
                  name='dispatch')
class SharedProxy(TemplateView):

    template_name = 'support/shared_proxy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['alphabet_string'] = ascii_uppercase
        context['shared_netid'] = self.request.GET.get('shared_netid', '')
        set_admin_wrapper_template(context)
        return context
