import logging
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils import timezone
from uw_saml.decorators import group_required
from endorsement.models import Endorser, Endorsee, EndorsementRecord
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time, log_data_error_response
from endorsement.views.rest_dispatch import RESTDispatch
from datetime import date, time, datetime, timedelta
import re


logger = logging.getLogger(__name__)


@method_decorator(
    group_required(settings.PROVISION_ADMIN_GROUP), name='dispatch')
class Statistics(RESTDispatch):
    """
    Show endorsements for endorsee
    """
    def get(self, request, *args, **kwargs):
        timer = Timer()

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
            elif re.match(r'^rate\/([0-9]+)$', self.kwargs['type']):
                m = re.match(r'^rate\/([0-9]+)$', self.kwargs['type'])
                days = int(m.group(1))
                now = timezone.now()
                span = now - timedelta(days=days)
                endorsements = EndorsementRecord.objects.filter(
                    is_deleted__isnull=True, datetime_created__gt=span)

                data = []
                while span <= now:
                    dt = date(year=span.year, month=span.month, day=span.day)
                    range_start = timezone.make_aware(datetime.combine(
                        dt, time(hour=0, minute=0, second=0)))
                    range_end = timezone.make_aware(datetime.combine(
                        dt, time(hour=23, minute=59, second=59)))

                    data.append([
                        dt.strftime('%D'),
                        endorsements.filter(
                            datetime_created__range=(
                                range_start, range_end)).count()
                    ])

                    span += timedelta(days=1)

                stats = {
                    'total': len(data),
                    'data': data
                }
            else:
                raise Exception('Unrecognized statistic type')

        except Exception:
            log_data_error_response(logger, timer)
            return RESTDispatch().error_response(
                543, "Data not available due to an error.")

        log_resp_time(logger, "statistics", timer)
        return self.json_response(stats)
