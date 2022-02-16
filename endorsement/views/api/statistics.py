# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
import logging
from django.utils import timezone
from endorsement.models import EndorsementRecord
from endorsement.util.log import log_data_error_response
from endorsement.views.rest_dispatch import RESTDispatch
from datetime import date, time, datetime, timedelta
from endorsement.util.auth import SupportGroupAuthentication
import re


logger = logging.getLogger(__name__)


class Statistics(RESTDispatch):
    """
    Show endorsements for endorsee
    """
    authentication_classes = [SupportGroupAuthentication]

    def get(self, request, *args, **kwargs):
        stats = {}
        try:
            if self.kwargs['type'] == 'service':
                stats = {
                    'total': 0,
                    'data': {}
                }

                for code in EndorsementRecord.CATEGORY_CODE_CHOICES:
                    n = EndorsementRecord.objects.filter(
                        is_deleted__isnull=True,
                        category_code=code[0]).count()
                    stats['data'][code[1]] = n
                    stats['total'] += n
            elif self.kwargs['type'] == 'shared':
                s = stats['Shared'] = EndorsementRecord.objects.filter(
                    is_deleted__isnull=True,
                    endorsee__is_person=False).count()
                p = stats['Personal'] = EndorsementRecord.objects.filter(
                    is_deleted__isnull=True,
                    endorsee__is_person=True).count()

                stats = {
                    'total': s + p,
                    'data': {
                        'Shared': s,
                        'Personal': p
                    }
                }
            elif self.kwargs['type'] == 'pending':
                a = EndorsementRecord.objects.filter(
                    is_deleted__isnull=True,
                    datetime_emailed__isnull=False,
                    datetime_endorsed__isnull=True).count()
                b = EndorsementRecord.objects.filter(
                    is_deleted__isnull=True,
                    datetime_emailed__isnull=False,
                    datetime_endorsed__isnull=False).count()
                c = EndorsementRecord.objects.filter(
                    is_deleted__isnull=True,
                    datetime_emailed__isnull=True,
                    datetime_endorsed__isnull=True).count()

                stats = {
                    'total': a + b + c,
                    'data': {
                        'Pending': a,
                        'Provisioned': b,
                        'Yet to Email': c
                    }
                }
            elif self.kwargs['type'] == 'endorsers':
                endorsers = {}
                for e in EndorsementRecord.objects.filter(
                        is_deleted__isnull=True):
                    if e.endorser.netid in endorsers:
                        endorsers[e.endorser.netid] += 1
                    else:
                        endorsers[e.endorser.netid] = 1

                data = sorted(
                    endorsers.items(), key=lambda kv: kv[1], reverse=True)

                stats = {
                    'total': len(data),
                    'data': data
                }
            elif self.kwargs['type'] == 'reasons':
                reasons = {}
                for e in EndorsementRecord.objects.filter(
                        is_deleted__isnull=True):
                    if e.reason in reasons:
                        reasons[e.reason] += 1
                    else:
                        reasons[e.reason] = 1

                data = sorted(
                    reasons.items(), key=lambda kv: kv[1], reverse=True)

                stats = {
                    'total': len(data),
                    'data': data
                }
            else:
                m = re.match(r'^rate\/([0-9]+)$', self.kwargs['type'])
                if not m:
                    raise Exception('Unrecognized statistic type')

                m = re.match(r'^rate\/([0-9]+)$', self.kwargs['type'])
                days = int(m.group(1))
                now = timezone.now()
                span = now - timedelta(days=days)
                shared_endorsements = EndorsementRecord.objects.filter(
                    endorsee__is_person=False,
                    datetime_endorsed__gte=span,
                    datetime_created__isnull=True)
                personal_endorsements = EndorsementRecord.objects.filter(
                    endorsee__is_person=True,
                    datetime_created__gte=span)

                data = []
                time_start = time(hour=0, minute=0, second=0)
                time_end = time(hour=23, minute=59, second=59)
                while span <= now:
                    dt = date(year=span.year, month=span.month, day=span.day)
                    range_start = timezone.make_aware(
                        datetime.combine(dt, time_start))
                    range_end = timezone.make_aware(
                        datetime.combine(dt, time_end))
                    shared_range = shared_endorsements.filter(
                        datetime_endorsed__range=(range_start, range_end))
                    personal_range = personal_endorsements.filter(
                        datetime_created__range=(range_start, range_end))

                    n = [[], []]
                    for code in EndorsementRecord.CATEGORY_CODE_CHOICES:
                        n[0].append(
                            shared_range.filter(
                                category_code=code[0],
                                is_deleted__isnull=True).count())
                        n[0].append(
                            personal_range.filter(
                                category_code=code[0],
                                is_deleted__isnull=True).count())
                        n[1].append(
                            shared_range.filter(
                                category_code=code[0],
                                is_deleted__isnull=False).count())
                        n[1].append(
                            personal_range.filter(
                                category_code=code[0],
                                is_deleted__isnull=False).count())

                    data.append([dt.strftime('%D'), n[0], n[1]])
                    span += timedelta(days=1)

                fields = []
                for code in EndorsementRecord.CATEGORY_CODE_CHOICES:
                    fields.append('Shared {}'.format(code[1]))
                    fields.append('Personal {}'.format(code[1]))

                stats = {
                    'fields': fields,
                    'data': data
                }

        except Exception as ex:
            log_data_error_response(logger, "{}".format(ex))
            return RESTDispatch().error_response(
                543, "Data not available due to an error.")

        return self.json_response(stats)
