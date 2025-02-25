# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from userservice.user import UserService
from endorsement.models import AccessRecordConflict
from endorsement.dao.access import (
    get_accessee_model, store_access_record, revoke_access)
from endorsement.dao.office import is_office_permitted, get_office_accessor
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import (
    UnrecognizedUWNetid, InvalidNetID, NoEndorsementException)
from endorsement.util.auth import is_support_user
from restclients_core.exceptions import DataFailureException
import logging


logger = logging.getLogger(__name__)


class ResolveRightsConflict(RESTDispatch):
    """
    For the supplied mailbox and delegate, create access record
    with selected access right and remove access record conflict
    """
    def post(self, request, *args, **kwargs):
        try:
            netid, acted_as = self._validate_user(request, logger=logger)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        mailbox = request.data.get('mailbox', None)
        delegate = request.data.get('delegate', None)
        access_type = request.data.get('access_type', None)

        if not is_office_permitted(mailbox):
            return invalid_endorser(logger)

        accessee = get_accessee_model(mailbox)
        accessor = get_office_accessor(delegate)

        try:
            conflict = AccessRecordConflict.objects.get(
                accessor=accessor, accessee=accessee)

            if not conflict.rights.filter(name=access_type).exists():
                return self.error_response(
                    404, message="Unknown Access Conflict")

            # record delegation and remove up unselected rights
            for right in conflict.rights.all():
                if right.name == access_type:
                    access = store_access_record(
                        accessee, accessor, right.name,
                        acted_as, is_reconcile=True)
                else:
                    try:
                        revoke_access(accessee, accessor, right.name)
                    except NoEndorsementException:
                        pass
                    except DataFailureException as ex:
                        return self.error_response(
                            ex.status,
                            message="Revoke access: {}".format(ex.status))

            conflict.delete()

        except AccessRecordConflict.DoesNotExist:
            return self.error_response(
                404, message="Unknown Access Conflict")
        except DataFailureException as ex:
            return self.error_response(ex.status, message=ex.msg)

        return self.json_response(access.json_data())
