# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging

from endorsement.dao.endorse import clear_endorsement
from endorsement.dao.user import get_endorser_model
from endorsement.dao.uwnetid_admin import get_owner_for_shared_netid
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.models import EndorsementRecord, Endorser
from endorsement.notifications.endorsement import warn_new_shared_netid_owner

logger = logging.getLogger(__name__)


def validate_shared_endorsers():
    orphans = []
    new_owners = {}

    for endorser in Endorser.objects.all():
        endorsements = EndorsementRecord.objects.filter(
            is_deleted__isnull=True,
            endorser__netid=endorser.netid,
            endorsee__is_person=False)

        if len(endorsements):
            netid_supported = get_supported_resources_for_netid(endorser.netid)
            if netid_supported is None:
                continue

            owned = [n.name for n in netid_supported if n.is_owner()]

            for e in endorsements:
                if e.endorsee.netid not in owned:
                    orphans.append(e)

    for orphan in orphans:
        owner = get_owner_for_shared_netid(orphan.endorsee.netid)

        if owner is None:
            # let expiration proceed naturally
            logger.error(
                f"Share netid {orphan.endorsee.netid} owned by {orphan.endorser.netid} no longer exists")
            continue

        # quietly sweep away record if new owner already endorsed
        try:
            noe = EndorsementRecord.objects.get(
                is_deleted__isnull=True,
                endorser__netid=owner,
                endorsee=orphan.endorsee,
                category_code=orphan.category_code)
            logger.info(
                f"shared: old owner {orphan.endorser.netid} of {orphan.endorsee.netid} ({orphan.category_code}) revoked for {noe.endorser.netid}")
            clear_endorsement(orphan)
            continue
        except EndorsementRecord.DoesNotExist:
            pass

        if owner in new_owners:
            new_owners[owner].append(orphan)
        else:
            new_owners[owner] = [orphan]

    for owner, endorsements in new_owners.items():
        try:
            new_owner = get_endorser_model(owner)
            warn_new_shared_netid_owner(new_owner, endorsements)
            # mail sent, clone endorsment record with new owner
            for er in endorsements:
                # no longer endorsed by previous owner
                er.revoke()
                logger.info(
                    f"shared: new record for {new_owner.netid} of {er.endorsee.netid} ({er.category_code}) from {er.endorser.netid}")
                # create record for new owner, preserving warning date
                er.pk = None
                er.endorser = new_owner
                er.accept_id = None
                er.datetime_expired = None
                er.datetime_notice_2_emailed = None
                er.datetime_notice_3_emailed = None
                er.datetime_notice_4_emailed = None
                er.is_deleted = None
                er.save()
        except Exception:  # noqa: S110
            pass
