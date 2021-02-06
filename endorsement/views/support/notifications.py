from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from uw_saml.decorators import group_required
from endorsement.views.support import set_admin_wrapper_template
from endorsement.services import endorsement_services
import logging


logger = logging.getLogger(__name__)


@login_required
@group_required(settings.PROVISION_ADMIN_GROUP)
def endorsee_notifications(request):
    context = {
        'services': dict([(s.service_name, {
            'name': s.category_name
        }) for s in endorsement_services()]),
        'warning_1': endorsement_services()[
            0].endorsement_expiration_warning(1),
        'warning_2': endorsement_services()[
            0].endorsement_expiration_warning(2),
        'warning_3': endorsement_services()[
            0].endorsement_expiration_warning(3),
        'warning_4': endorsement_services()[
            0].endorsement_expiration_warning(4)
    }
    set_admin_wrapper_template(context)

    return render(request, "admin/notifications.html", context)
