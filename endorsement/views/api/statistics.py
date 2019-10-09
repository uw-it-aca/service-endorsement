import logging
from django.conf import settings
from django.utils.decorators import method_decorator
from uw_saml.decorators import group_required
from endorsement.models import Endorser, Endorsee, EndorsementRecord
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time, log_data_error_response
from endorsement.views.rest_dispatch import RESTDispatch


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
                for code in EndorsementRecord.CATEGORY_CODE_CHOICES:
                    stats[code[1]] = EndorsementRecord.objects.filter(
                        is_deleted__isnull=True,
                        category_code=code[0]).count()
            elif self.kwargs['type'] == 'shared':
                stats['Shared'] = EndorsementRecord.objects.filter(
                        is_deleted__isnull=True,
                        endorsee__is_person__isnull=True).count()
                stats['Personal'] = EndorsementRecord.objects.filter(
                        is_deleted__isnull=True,
                        endorsee__is_person__isnull=False).count()
            else:
                raise Exception('Unrecognized statistic type')

        except Exception:
            log_data_error_response(logger, timer)
            return RESTDispatch().error_response(
                543, "Data not available due to an error.")

        log_resp_time(logger, "statistics", timer)
        return self.json_response(stats)
