# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from uw_saml.decorators import group_required
from persistent_message.models import TagGroup, Tag
from endorsement.services import endorsement_services


@method_decorator(login_required, name='dispatch')
@method_decorator(group_required(settings.PROVISION_ADMIN_GROUP),
                  name='dispatch')
class PersistentMessages(TemplateView):
    def get(self, request):
        # ensure tags are set up
        tag_group_name = "Provisioned Service"

        tag_group, created = TagGroup.objects.update_or_create(
            name=tag_group_name)

        tags = list(Tag.objects.all().values_list('name', flat=True))

        for service in endorsement_services():
            tag, created = Tag.objects.update_or_create(
                name=service.service_name, group=tag_group)
            try:
                tags.remove(tag.name)
            except ValueError:
                pass

        for tag in tags:
            Tag.objects.get(name=tag).delete()

        return redirect(reverse('manage_persistent_messages'))
