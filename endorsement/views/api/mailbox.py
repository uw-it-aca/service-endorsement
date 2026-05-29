# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.access import get_delegates_for_netid
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
            all_delegates = get_delegates_for_netid(netid)
            for supported in get_supported_resources_for_netid(netid):
                if ((supported.is_owner() and (
                            supported.is_shared_netid()
                            or supported.netid_type in [
                                'administrator', 'support']))
                        and is_office_permitted(supported.name)):
                    all_delegates += get_delegates_for_netid(supported.name)

            return self.json_response({
                'delegates': [d.json_data() for d in all_delegates]
            })
        except Exception as ex:
            log_data_error_response(logger, "{}".format(ex))
            return RESTDispatch().error_response(
                543, """
Data not available due to an error.
""")
