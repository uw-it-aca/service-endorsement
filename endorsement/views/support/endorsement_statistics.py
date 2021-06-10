# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from uw_saml.decorators import group_required
from endorsement.views.support import set_admin_wrapper_template
from endorsement.models import EndorsementRecord as ER
from datetime import timedelta
from string import ascii_uppercase


@method_decorator(login_required, name='dispatch')
@method_decorator(group_required(settings.PROVISION_SUPPORT_GROUP),
                  name='dispatch')
class EndorsementStatistics(TemplateView):

    template_name = 'support/stats.html'

    def get_context_data(self, **kwargs):
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        expiring_start = now - timedelta(days=365)
        expiring_end = now - timedelta(days=358)

        context = super().get_context_data(**kwargs)
        context['alphabet_string'] = ascii_uppercase
        context['endorsement_count'] = ER.objects.all().count()
        context['active_endorsement_count'] = ER.objects.filter(
            is_deleted__isnull=True).count()
        context['new_endorsement_count'] = ER.objects.filter(
            is_deleted__isnull=True,
            datetime_endorsed__gte=week_ago).count()
        context['expiring_endorsement_count'] = ER.objects.filter(
            is_deleted__isnull=True,
            datetime_endorsed__gte=expiring_start,
            datetime_endorsed__lte=expiring_end).count()
        set_admin_wrapper_template(context)
        return context
