from endorsement.views.decorators import admin_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from endorsement.views import set_admin_wrapper_template
import logging


logger = logging.getLogger(__name__)


@login_required
@admin_required('PROVISION_ADMIN_GROUP')
def endorsee_search(request):
    context = {}
    set_admin_wrapper_template(context)

    return render(request, "admin/endorsee.html", context)
