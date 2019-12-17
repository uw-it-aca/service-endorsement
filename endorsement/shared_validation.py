from endorsement.models import Endorser, EndorsementRecord
from endorsement.dao.uwnetid_supported import get_shared_netids_for_netid
from endorsement.dao.user import get_endorser_model
from endorsement.dao.uwnetid_admin import get_owner_for_shared_netid
from endorsement.dao.notification import warn_new_shared_netid_owner


def validate_shared_endorsers():
    orphans = []
    new_owners = {}

    for endorser in Endorser.objects.all():
        endorsements = EndorsementRecord.objects.filter(
            is_deleted__isnull=True,
            endorser__netid=endorser.netid,
            endorsee__is_person=False)

        if len(endorsements):
            owned = [
                n.name for n in get_shared_netids_for_netid(endorser.netid)]
            for e in endorsements:
                if e.endorsee.netid not in owned:
                    orphans.append(e)

    for orphan in orphans:
        owner = get_owner_for_shared_netid(orphan.endorsee.netid)
        if owner in new_owners:
            new_owners[owner].append(orphan)
        else:
            new_owners[owner] = [orphan]

    for owner in new_owners:
        try:
            new_owner = get_endorser_model(owner)
            warn_new_shared_netid_owner(new_owner, new_owners[owner])
            # mail sent, clone endorsment record with new owner
            for er in new_owners[owner]:
                # no longer endorsed by previous owner
                er.revoke()
                # create record for new owner, preserving warning date
                er.pk = None
                er.endorser = new_owner
                er.accept_id = None
                er.datetime_expired = None
                er.is_deleted = None
                er.save()
        except Exception as ex:
            None