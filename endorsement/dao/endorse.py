import logging
from django.utils import timezone
from endorsement.models.core import EndorsementRecord


logger = logging.getLogger(__name__)


def store_endorsement(endorser, endorsee):
    en, created = EndorsementRecord.objects.update_or_create(
        endorser=endorser,
        subscription_code=EndorsementRecord.OFFICE_365,
        endorsee=endorsee,
        defaults={'datetime_endorsed': timezone.now()
                  }
        )
    return en, created


def get_office_365_endorsements_endorsed_by(endorser):
    return EndorsementRecord.objects.filter(
        endorser=endorser,
        subscription_code=EndorsementRecord.OFFICE_365)
