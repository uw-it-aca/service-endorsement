from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from uw_saml.decorators import group_required
from endorsement.views.support import set_admin_wrapper_template
from string import ascii_uppercase
import logging


logger = logging.getLogger(__name__)


@login_required
@group_required(settings.PROVISION_ADMIN_GROUP)
def endorsement_statistics(request):
    context = {
        'alphabet_string': ascii_uppercase
    }
    set_admin_wrapper_template(context)

    return render(request, "admin/stats.html", context)
