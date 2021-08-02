# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from uw_saml.decorators import group_required
from endorsement.views.support import set_admin_wrapper_template
from endorsement.services import endorsement_services


@method_decorator(login_required, name='dispatch')
@method_decorator(group_required(settings.PROVISION_SUPPORT_GROUP),
                  name='dispatch')
class EndorseeNotifications(TemplateView):

    template_name = 'support/notifications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = dict([(s.service_name, {
            'name': s.category_name
        }) for s in endorsement_services()])
        context['warning_1'] = endorsement_services()[
            0].endorsement_expiration_warning(1)
        context['warning_2'] = endorsement_services()[
            0].endorsement_expiration_warning(2)
        context['warning_3'] = endorsement_services()[
            0].endorsement_expiration_warning(3)
        context['warning_4'] = endorsement_services()[
            0].endorsement_expiration_warning(4)

        set_admin_wrapper_template(context)
        return context
