# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from userservice.user import UserService
from endorsement.services import service_name_list
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorsee_model
from endorsement.views.rest_dispatch import invalid_session, handle_exception
import traceback
import logging
import json


logger = logging.getLogger(__name__)


@login_required
def accept(request, accept_id):
    try:
        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger)

        context = {
            "user": {
                "netid": netid
            }
        }

        records = EndorsementRecord.objects.get_accept_endorsement(
            accept_id, endorsed=False)
        if len(records) != 1:
            endorsee = get_endorsee_model(netid)
            er = EndorsementRecord.objects.get_endorsements_for_endorsee(
                endorsee)
            for record in er:
                if accept_id == record.get_accept_id(netid):
                    context['services'] = service_name_list()
                    return render(request, "accepted.html", context)

            context["err"] = "Invalid Endorser"
            return render(request, "404.html", context, status=404)

        record = records[0]
        if not record.valid_endorsee(netid):
            context["auth_failure"] = "provisionee"
            return render(request, "401.html", context, status=401)

        context['endorsement_record'] = json.dumps(record.json_data())

        return render(request, "accept.html", context)

    except Exception as ex:
        handle_exception(logger, "{}".format(ex), traceback)
