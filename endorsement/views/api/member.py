# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from endorsement.dao.shared_drive import get_shared_drives_for_member
from endorsement.util.log import log_data_error_response
from endorsement.views.rest_dispatch import RESTDispatch
from endorsement.util.auth import SupportGroupAuthentication
from rest_framework.authentication import TokenAuthentication


logger = logging.getLogger(__name__)


class Member(RESTDispatch):
    """
    Show shared drives for member
    """
    authentication_classes = [TokenAuthentication, SupportGroupAuthentication]

    def get(self, request, *args, **kwargs):
        member = self.kwargs.get('member')
        try:
            drives = get_shared_drives_for_member(member)
            return self.json_response({
                'drives': [d.json_data() for d in drives]
            })
        except Exception as ex:
            log_data_error_response(logger, "{}".format(ex))
            return RESTDispatch().error_response(
                543, """
Data not available due to an error.
""")
