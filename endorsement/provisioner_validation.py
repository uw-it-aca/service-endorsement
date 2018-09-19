from endorsement.models import EndorsementRecord as ER
from endorsement.dao.user import get_endorser_model
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.notification import notify_invalid_endorser


def validate_endorsers():
    endorsements = ER.objects.filter(
        datetime_endorsed__isnull=False,
        is_deleted__isnull=True,
        endorsee__is_person=True,
        endorser__datetime_emailed__isnull=True)

    for netid in list(set([e.endorser.netid for e in endorsements])):
        if not is_valid_endorser(netid):
            endorser = get_endorser_model(netid)
            endorsements = ER.objects.get_endorsements_for_endorser(
                endorser).filter(endorsee__is_person=True)
            notify_invalid_endorser(endorser, endorsements)
