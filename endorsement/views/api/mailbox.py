# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from endorsement.models import AccessRecord
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.access import (
    get_delegates_for_netid, get_accessee_model, get_accessor_model)
from endorsement.dao.office import is_office_permitted
from endorsement.util.log import log_data_error_response
from endorsement.views.rest_dispatch import RESTDispatch
from endorsement.util.auth import SupportGroupAuthentication
from endorsement.reconcile_access import (
    new_access_record, undelete_access_record,
    get_access_right, assign_access_right)
from endorsement.exceptions import UnrecognizedUWNetid
from rest_framework.authentication import TokenAuthentication
from restclients_core.exceptions import DataFailureException
import re


logger = logging.getLogger(__name__)


class Mailbox(RESTDispatch):
    """
    Show delegates for given netid's mailboxes
    """
    authentication_classes = [TokenAuthentication, SupportGroupAuthentication]

    def get(self, request, *args, **kwargs):
        netid = self.kwargs.get('netid')
        sync = request.GET.get('sync', 'false').lower() == 'true'
        try:
            delegations = self._get_all_delegations_for_netid(netid)
            if sync:
                delegations = self._sync_delegations(delegations)

            return self.json_response({
                'delegates': delegations
            })
        except Exception as ex:
            log_data_error_response(logger, f"{ex}")
            return RESTDispatch().error_response(
                543, f"Data not available due to an error: {ex}")

    def _get_all_delegations_for_netid(self, netid):
        delegations = self._delegations_for_netid(netid)
        for supported in self._get_supported_resources_for_netid(netid):
            if self._is_valid_supported(supported):
                delegations += self._delegations_for_netid(supported.name)

        return delegations

    def _sync_delegations(self, delegations):
        synchronized_delegations = []

        for delegation in delegations:
            if delegation['is_missing_record']:
                synchronized_delegations.append(
                    self._create_access_record(delegation))

                delegation['is_missing_record'] = False
            elif delegation['is_deleted_record']:
                synchronized_delegations.append(
                    self._undelete_access_record(delegation))

                delegation['is_deleted_record'] = False
            elif delegation['is_right_mismatch']:
                synchronized_delegations.append(
                    self._update_access_record_right(delegation))

                delegation['is_right_mismatch'] = False
            elif delegation['is_stale_record']:
                self._remove_stale_access_record(delegation)

                delegation['is_stale_record'] = False

        return synchronized_delegations

    def _create_access_record(self, delegation):
        accessee = get_accessee_model(delegation['user'])
        new_access_record(
            accessee, self._delegate(delegation), delegation['access_right'])
        return delegation

    def _undelete_access_record(self, delegation):
        record = self._get_record_from_delegation(delegation)
        undelete_access_record(record)
        if record.access_right != delegation['access_right']:
            assign_access_right(record, delegation['access_right'])

        return delegation

    def _update_access_record_right(self, delegation):
        record = self._get_record_from_delegation(delegation)
        assign_access_right(record, delegation['access_right'])
        return delegation

    def _remove_stale_access_record(self, delegation):
        record = self._get_record_from_delegation(delegation)
        if record:
            record.is_deleted = True
            record.datetime_expired = None
            record.save()

        return delegation

    def _get_record_from_delegation(self, delegation):
        try:
            record = AccessRecord.objects.get(
                accessee__netid=delegation['user'],
                accessor__name=self._delegate(delegation))
            return record
        except AccessRecord.DoesNotExist:
            logger.error(f"Stale record not found for {delegation}")

        return None

    def _delegations_for_netid(self, netid):
        try:
            delegates = get_delegates_for_netid(netid)
        except DataFailureException as ex:
            if ex.status == 404:
                delegates = []
            else:
                raise ex

        delegations = []

        accessee = get_accessee_model(netid)
        access_records = AccessRecord.objects.get_access_for_accessee(accessee)
        record_ids = set([record.pk for record in access_records])
        for delegate in delegates:
            delegate_name = self._delegate(delegate.json_data())
            try:
                access_right = get_access_right(delegate.access_right)
                record = access_records.get(
                    accessee__netid=netid, accessor__name=delegate_name,
                    access_right=access_right)
                record_ids.remove(record.pk)
            except AccessRecord.DoesNotExist:
                record = None

            delegations.append({
                'user': netid,
                'delegate': delegate_name,
                'access_right': delegate.access_right,
                'is_missing_record': (record is None),
                'is_stale_record': False,
                'is_deleted_record': (record is not None and (
                    record.is_deleted)),
                'is_right_mismatch': (record is not None and (
                    record.access_right.name != delegate.access_right)),
            })

        for id in record_ids:
            record = access_records.get(pk=id)
            delegations.append({
                'user': netid,
                'delegate': record.accessor.name,
                'access_right': record.access_right.name,
                'is_missing_record': False,
                'is_stale_record': True,
                'is_deleted_record': False,
                'is_right_mismatch': False,
            })

        return delegations

    def _get_supported_resources_for_netid(self, netid):
        try:
            return get_supported_resources_for_netid(netid)
        except DataFailureException as ex:
            if ex.status == 404:
                delegates = []
            else:
                raise ex

    def _is_valid_supported(self, supported):
        try:
            return ((supported.is_owner()
                     and (supported.is_shared_netid()
                          or supported.netid_type in [
                              'administrator', 'support']))
                    and is_office_permitted(supported.name))
        except UnrecognizedUWNetid:
            return False

    def _delegate(self, delegation):
        try:
            delegate = delegation['delegate']
            local, domain = delegate.split('@')
            if re.match(r"(uw|washington|u\.washington)\.edu", domain):
                return local

            raise InvalidNetID(f"{delegate}: Not a UW email")
        except ValueError:
            return delegate
