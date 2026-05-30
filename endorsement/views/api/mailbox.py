# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from endorsement.models import Accessee, Accessor, AccessRight, AccessRecord
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.access import (
    get_delegates_for_netid, get_accessee_model, get_accessor_model)
from endorsement.dao.office import is_office_permitted
from endorsement.util.log import log_data_error_response
from endorsement.views.rest_dispatch import RESTDispatch
from endorsement.util.auth import SupportGroupAuthentication
from rest_framework.authentication import TokenAuthentication


logger = logging.getLogger(__name__)


class Mailbox(RESTDispatch):
    """
    Show delegates for given netid's mailboxes
    """
    authentication_classes = [TokenAuthentication, SupportGroupAuthentication]

    def get(self, request, *args, **kwargs):
        netid = self.kwargs.get('netid')
        try:
            all_delegates = [
                self._delegate(netid, d) for d in get_delegates_for_netid(netid)]
            for supported in get_supported_resources_for_netid(netid):
                if self._is_valid_supported(supported):
                    all_delegates += [
                        self._delegate(supported.name, d) for (
                            d) in get_delegates_for_netid(supported.name)]

            return self.json_response({ 'delegates': all_delegates })
        except Exception as ex:
            log_data_error_response(logger, "{}".format(ex))
            return RESTDispatch().error_response(
                543, """
Data not available due to an error.
""")

    def _delegate(self, mailbox, delegate_model):
        json_delegate = delegate_model.json_data()
        try:
            accessee = Accessee.objects.get(netid=mailbox)
            accessor = Accessor.objects.get(name=delegate_model.delegate)
            access = AccessRecord.objects.get(accessee=accessee, accessor=accessor)
            if is_deleted == True:
                json_delegate['delta'] = 'Deleted'
            elif access_right.name != delegate_model.access_right:
                json_delegate['delta'] = 'Access right mismatch'
        except Accessee.DoesNotExist:
            json_delegate['delta'] = 'Missing Accessee'
        except Accessor.DoesNotExist:
            json_delegate['delta'] = 'Missing Accessor'
        except AccessRecord.DoesNotExist:
            json_delegate['delta'] = 'Missing Delegation'

        return json_delegate

    def _is_valid_supported(self, supported):
        return ((supported.is_owner() and (
            supported.is_shared_netid()
            or supported.netid_type in [
                'administrator', 'support']))
            and is_office_permitted(supported.name))
