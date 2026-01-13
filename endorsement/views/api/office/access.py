# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from userservice.user import UserService
from endorsement.models import AccessRecord, AccessRecordConflict, AccessRight
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.persistent_messages import get_persistent_messages
from endorsement.dao.access import (
    get_accessee_model, store_access, update_access,
    revoke_access, renew_access)
from endorsement.dao.office import is_office_permitted, get_office_accessor
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser, data_error)
from endorsement.exceptions import (
    UnrecognizedUWNetid, InvalidNetID, DelegateParameterException)
from endorsement.util.auth import is_support_user
from uw_msca.access_rights import get_access_rights
from restclients_core.exceptions import DataFailureException
import json
import logging


logger = logging.getLogger(__name__)


class Access(RESTDispatch):
    """
    Return maiboxes and access associated with netid
    """
    def get(self, request, *args, **kwargs):
        try:
            netid, acted_as = self._validate_user(
                request, valid_act_as=is_support_user, logger=logger)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        netids = {}

        if is_office_permitted(netid):
            accessee = get_accessee_model(netid)
            netids[netid] = {
                'name': accessee.display_name,
                'access': self._load_access_for_accessee(accessee),
                'conflict': self._load_access_conflict_for_accessee(accessee)
            }

        for supported in get_supported_resources_for_netid(netid):
            if self._is_valid_accessor(supported):
                if is_office_permitted(supported.name):
                    accessee = get_accessee_model(supported.name)
                    netids[supported.name] = {
                        'name': accessee.display_name,
                        'access': self._load_access_for_accessee(accessee),
                        'conflict': self._load_access_conflict_for_accessee(
                            accessee)
                    }

        return self.json_response({
            'netids': netids,
            'messages': get_persistent_messages()
        })

    def post(self, request, *args, **kwargs):
        try:
            netid, acted_as = self._validate_user(request, logger=logger)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        try:
            mailbox = self._validate_param(request.data, 'mailbox')
            delegate = self._validate_param(request.data, 'delegate')
            access_type = self._validate_param(request.data, 'access_type')
            previous_access_type = self._validate_param(
                request.data, 'previous_access_type', True)
        except DelegateParameterException as ex:
            message = f"Access.post parameter: {ex}"
            logger.error(message)
            return self.error_response(400, message=message)

        if not is_office_permitted(mailbox):
            return invalid_endorser(logger)

        accessee = get_accessee_model(mailbox)
        accessor = get_office_accessor(delegate)

        try:
            # remove previous access type before setting updated type
            if previous_access_type and previous_access_type != access_type:
                revoke_access(
                    accessee, accessor, previous_access_type, acted_as)

            access = store_access(
                accessee, accessor, access_type, acted_as)
        except DataFailureException as ex:
            return self._msca_dfe_response('Access.post', request.data, ex)

        return self.json_response(access.json_data())

    def patch(self, request, *args, **kwargs):
        try:
            netid, acted_as = self._validate_user(request, logger=logger)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        try:
            action = self._validate_param(request.data, 'action', True)
            mailbox = self._validate_param(request.data, 'mailbox')
            delegate = self._validate_param(request.data, 'delegate')
            access_type = self._validate_param(
                request.data, 'access_type', action == 'renew')
            previous_access_type = self._validate_param(
                request.data, 'previous_access_type', True)
        except DelegateParameterException as ex:
            logger.error(f"Access.patch parameter: {ex}")
            return self.error_response(400, message=str(ex))

        if not is_office_permitted(mailbox):
            return invalid_endorser(logger)

        accessee = get_accessee_model(mailbox)
        accessor = get_office_accessor(delegate)

        try:
            if action == 'renew':
                access = renew_access(accessee, accessor, acted_as)
                return self.json_response(access.json_data())
            elif previous_access_type and access_type:
                access = update_access(
                    accessee, accessor, previous_access_type,
                    access_type, acted_as)
            else:
                logger.error(
                    f"Access.patch missing parameter: {request.data}")
                return self.error_response(400, message="Insufficient Data")
        except AccessRecord.DoesNotExist:
            logger.error(
                f"Access.patch missing access record: {request.data}")
            return self.error_response(400, message="Unknown Access Record")
        except DataFailureException as ex:
            return self._msca_dfe_response('Access.patch', request.data, ex)

        return self.json_response(access.json_data())

    def delete(self, request, *args, **kwargs):
        try:
            netid, acted_as = self._validate_user(request, logger=logger)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        mailbox = request.GET.get('mailbox')
        delegate = request.GET.get('delegate')
        access_type = request.GET.get('access_type')

        accessee = get_accessee_model(mailbox)
        accessor = get_office_accessor(delegate)

        try:
            access = revoke_access(accessee, accessor, access_type, acted_as)
        except DataFailureException as ex:
            return self._msca_dfe_response('Access.delete', request.data, ex)

        return self.json_response(access.json_data())

    def _validate_param(self, data, field, nullable=False):
        try:
            value = data[field].strip()
            if not value and not nullable:
                raise DelegateParameterException(f"Empty {field} field")

            return value
        except AttributeError as ex:
            if nullable:
                return None

            raise DelegateParameterException(f"Null {field} field")
        except KeyError as ex:
            if nullable:
                return None

            raise DelegateParameterException(f"Missing {field} field")

    def _load_access_for_accessee(self, accessee):
        access = AccessRecord.objects.get_access_for_accessee(accessee)
        return [ar.json_data() for ar in access]

    def _load_access_conflict_for_accessee(self, accessee):
        conflict = AccessRecordConflict.objects.filter(accessee=accessee)
        return [arc.json_data() for arc in conflict]

    def _is_valid_accessor(self, supported):
        return (supported.is_owner() and (
            supported.is_shared_netid()
            or supported.netid_type in ['administrator', 'support']))

    def _msca_dfe_response(self, method, request_data, ex):
        logger.error(
            f"{method} {ex.url} FAILURE data: {request_data} "
            f"response: {ex.msg} ({ex.status})")

        message = ex.msg
        if type(message) == bytes:
            try:
                json_content = json.loads(message.decode('utf-8'))
                message = json_content.get('msg', 'Server Error')
            except Exception as e:
                pass

        return self.error_response(ex.status, message)


class AccessRights(RESTDispatch):
    """
    Return Office mailbox access right list
    """
    def get(self, request, *args, **kwargs):
        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger)

        try:
            access_rights = []

            for t in get_access_rights():
                r, created = AccessRight.objects.update_or_create(
                    name=t.right_id, defaults={'display_name': t.displayname})
                access_rights.append(t.json_data())

            return self.json_response(access_rights)
        except Exception as ex:
            return data_error(logger, "{}".format(ex))
