# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.http import StreamingHttpResponse
from endorsement.models import EndorsementRecord
from endorsement.views.rest_dispatch import RESTDispatch
from endorsement.util.auth import SupportGroupAuthentication
from rest_framework.authentication import TokenAuthentication
from io import StringIO
import csv
import logging


logger = logging.getLogger(__name__)


CHUNKING_LINES = 250


class Endorsements(RESTDispatch):
    """
    Return CSV of all endorsers and their endorsements (for reporting)

     Provisioner   Provisioned  Service  "Pending boolean"  "Date provisioned"

    """
    authentication_classes = [TokenAuthentication, SupportGroupAuthentication]

    def get(self, request, *args, **kwargs):
        self.csvfile = StringIO()
        self.csvwriter = csv.writer(self.csvfile)

        response = StreamingHttpResponse(
            self.get_endorsers(),
            content_type='text/csv')
        response[
            'Content-Disposition'] = 'attachment; filename="endorsements.csv"'
        return response

    def read_and_flush(self):
        self.csvfile.seek(0)
        data = self.csvfile.read()
        self.csvfile.seek(0)
        self.csvfile.truncate()
        return data

    def get_endorsers(self):
        line = 1
        endorsements = EndorsementRecord.objects.filter(
            is_deleted__isnull=True)

        self.csvwriter.writerow([
            "Provisioner", "Provisionee", "Service",
            "Pending", "Provision Date"])

        for endorser_id in list(set([e.endorser.id for e in endorsements])):
            for endorsement in endorsements.filter(endorser__id=endorser_id):
                line += 1
                self.csvwriter.writerow([
                    endorsement.endorser.netid,
                    endorsement.endorsee.netid,
                    endorsement.get_category_code_display(),
                    'true' if (
                        endorsement.datetime_endorsed is None) else 'false',
                    endorsement.datetime_endorsed.strftime(
                        "%Y-%m-%d %H:%M:%S") if (
                            endorsement.datetime_endorsed) else ""])

                if line >= CHUNKING_LINES:
                    data = self.read_and_flush()
                    line = 0
                    yield data

        if line > 0:
            data = self.read_and_flush()
            yield data
