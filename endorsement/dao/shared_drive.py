# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import collections
import datetime as dt
from endorsement.dao.gws import is_group_member
from endorsement.dao.itbill import get_subscription_by_key_remote
from endorsement.exceptions import ITBillSubscriptionNotFound
from endorsement.models import (
    ITBillSubscription,
)

from endorsement.models.shared_drive import (
    Member,
    Role,
    SharedDrive,
    SharedDriveMember,
    SharedDriveQuota,
    SharedDriveRecord,
)
from endorsement.exceptions import SharedDriveNonPrivilegedMember
import re
import logging

# methods are imported to populate namespace and be used elsewhere
from uw_msca.shared_drive import (  # noqa: F401
    get_default_quota,
    get_google_drive_states,
    set_drive_quota,
)
from uw_msca.models import GoogleDriveState


logger = logging.getLogger(__name__)
netid_regex = re.compile(
    r"^(?P<netid>[^@]+)@(uw|(u\.)?washington)\.edu$", re.I
)


def load_shared_drives(google_drive_states):
    """
    Populate SharedDriveRecord models as reported by uw_mwsa.

    Returns the final SharedDriveRecord created.
    """
    seen_drive_ids = set()

    retval = None

    for gds in google_drive_states:
        try:
            retval: SharedDriveRecord = load_shared_drive_record(
                gds,
                is_seen=gds.drive_id in seen_drive_ids,
            )
        except SharedDriveNonPrivilegedMember as e:
            logger.info(f"{e}")
        except Exception as e:
            logger.error(f"shared drive record: {gds}: {e}")
        else:
            seen_drive_ids.add(gds.drive_id)

    return retval


def load_shared_drive_record(a: GoogleDriveState, is_seen):
    """
    ensure shared drive record is created
    """
    shared_drive = upsert_shared_drive(a, is_seen)
    shared_drive_record, _ = SharedDriveRecord.objects.get_or_create(
        shared_drive=shared_drive,
        defaults={
            "datetime_created": dt.datetime.now(dt.timezone.utc),
        },
    )
    return shared_drive_record


def upsert_shared_drive(a: GoogleDriveState, is_seen):
    """
    return a shared drive model for given DriveId, allowing for
    name, quota and membership changes
    """
    drive_quota = get_drive_quota(a)
    shared_drive_member = get_shared_drive_member(a)
    shared_drive, created = SharedDrive.objects.update_or_create(
        drive_id=a.drive_id,
        defaults={
            "drive_name": a.drive_name,
            "drive_quota": drive_quota,
        },
    )

    if not created and not is_seen:
        # clear e.g., yesterday's membership and re-add
        shared_drive.members.clear()

    shared_drive.members.add(shared_drive_member)
    return shared_drive


def get_drive_quota(a):
    """
    return a shared drive quota model from OrgUnit
    """
    defaults = {"org_unit_name": a.org_unit_name}
    try:
        defaults["quota_limit"] = a.quota_limit
    except ValueError:
        "Drive has no quota set. Probably in invalid org unit."

    drive_quota, _ = SharedDriveQuota.objects.update_or_create(
        org_unit_id=a.org_unit_id,
        defaults=defaults,
    )
    return drive_quota


def get_shared_drive_member(a: GoogleDriveState):
    """
    return a shared drive member model from Member and Role
    """
    member = get_member(a)
    role = get_role(a)
    shared_drive_member, _ = SharedDriveMember.objects.get_or_create(
        member=member, role=role
    )
    return shared_drive_member


def get_member(a: GoogleDriveState):
    """
    return a member model, bare netid or non-uw email
    """
    netid = netid_regex.match(a.member)
    name = netid.group("netid") if netid else a.member

    return Member.objects.get_member(name=name)


def get_role(a: GoogleDriveState):
    """
    Return a Role model.

    Raises SharedDriveNonPrivilegedMember IFF role is not a manager role.
    """
    # cull non-manager roles until others are interesting
    if a.role != Role.MANAGER_ROLE:
        msg = "Shared drive member {} is not a manager ({!r}) and instead {!r}"
        raise SharedDriveNonPrivilegedMember(
            msg.format(a.member, Role.MANAGER_ROLE, a.role),
        )

    role, _ = Role.objects.get_or_create(role=a.role)
    return role


def get_subscription(sdr: SharedDriveRecord):
    sub = sdr.subscription
    if sub is not None:
        return sub

    key_remote = sdr.get_itbill_key_remote()

    try:
        sub_json = get_subscription_by_key_remote(key_remote)
    except ITBillSubscriptionNotFound:
        return None
    except Exception:
        logging.exception(
            f"Error attempting to find ITBill subscription for {key_remote}"
        )
    else:
        sub = ITBillSubscription()
        sub.from_json(sub_json)
        sdr.subscription = sub
        sdr.save()
        return sdr.subscription


class Reconciler:
    """
    Reconciles Shared Drives.
    """

    def reconcile(self):
        id_GoogleDriveState = self.GoogleDriveState_by_drive_id()
        default_quota = get_default_quota()

        prt_drive_ids = self.get_prt_drive_ids()
        msca_drive_ids = set(id_GoogleDriveState.keys())

        new = msca_drive_ids - prt_drive_ids
        missing = prt_drive_ids - msca_drive_ids
        existing = msca_drive_ids & prt_drive_ids

        self.handle_new_drives(
            new,
            id_GoogleDriveState,
            default_quota,
        )
        self.handle_missing_drives(missing, default_quota)
        self.reconcile_existing_drives(
            existing, id_GoogleDriveState, subsidized_quota=default_quota
        )

        # query itbill status for partiular key_memote
        # only add provisions  and quanties to itbill models
        # for the given product sys_id
        # (could it be the case that the product sys_id is not unique?)

    def handle_new_drives(self, drive_ids, id_GoogleDriveState, default_quota):
        """
        Create shared drive record with implicit provisioned date.

        This is expected on the first day of acceptance lifecycle as we get
        everything previously existing bootstrapped. After that, in theory, all
        the new shared drives will be created via PRT and thus this shouldn't
        happen.
        """
        for drive_id in drive_ids:
            drive_states = id_GoogleDriveState[drive_id]

            # TODO: probably wrap remainder of loop in a transaction...

            # create SharedDriveRecord + SharedDrive + Members/Roles
            sdr: SharedDriveRecord = load_shared_drives(drive_states)
            if sdr is None:  # diagnostic
                print(
                    f"Got None back when providing {len(drive_states)} "
                    "records to load_shared_Drive"
                )
                print(
                    "{drive_id=} Member roles: "
                    f"{set(X.role for X in drive_states)}"
                )

            if sdr is None:
                # examples:
                # drive_id 0APhs8SozJRR3Uk9PVA; all members in SUSPENDED role
                #   if no drive members have an "organizer" role the
                #   SharedDriveRecord is not created

                # In these cases PRT has no administrator to alert
                # TODO: confirm with dsnorton this should be silently ignored
                continue

            quota = sdr.shared_drive.drive_quota
            if quota.quota_limit == default_quota:
                continue

            sub = get_subscription(sdr)
            if sub is None:
                set_drive_quota(drive_id=drive_id, quota=default_quota)
                quota.quota_limit = default_quota
                quota.save()

    def handle_missing_drives(self, missing_drive_ids, default_quota):
        """
        For drives that no longer exist as reported by MSCA.

        This means the drive no longer exists or no longer has managers.

        If deleted it is expected the related SharedDriveRecord would have
        is_deleted set to True.

        The last manager departing would happen out of band.
        """
        # TODO: should we be logging this or performing any other actions?
        records = SharedDrive.objects.filter(drive_id__in=missing_drive_ids)
        for record in records:
            record.is_deleted = True

        SharedDrive.objects.bulk_update(records, fields=["is_deleted"])

    def reconcile_existing_drives(
        self, drives, id_GoogleDriveState, subsidized_quota
    ):
        # helper functions that probably need to be moved to a DAO file
        def managers_for_shared_drive(google_drive_states):
            """
            Returns SharedDriveMember objects for privileged members.
            """
            result = []
            for gds in google_drive_states:
                try:
                    member = get_shared_drive_member(gds)
                except SharedDriveNonPrivilegedMember:
                    pass
                else:
                    result.append(member)

            return result

        def get_current_subscription(sdr: SharedDriveRecord):
            """
            Returns the current subscription associated with shared_drive.

            If there is no subscription OR the subscription is not in a
            "deployed" state returns None
            """
            sub = sdr.subscription
            if sub is None:
                return None

            if sub.state == ITBillSubscription.SUBSCRIPTION_DEPLOYED:
                return sub
            else:
                return None

        def get_subscription_quota_gigabytes(sub: ITBillSubscription):
            """
            Return integer quota for subscription. Units are GB.
            """
            provision = sub.get_provisions().get()  # can there ever be != 1?
            quota = provision.current_quantity_gigabytes
            return quota

        # END helper functions

        for drive_id in drives:
            drive_states = id_GoogleDriveState[drive_id]
            # drive states are expected to be consistent for most fields
            # notably excepting "member" and "role"
            drive_state = drive_states[0]

            shared_drive = SharedDrive.objects.get(drive_id=drive_id)

            # TODO: wrap below in a transaction?

            # update drive manager list
            managers = managers_for_shared_drive(drive_states)
            shared_drive.members.set(managers)

            # update drive name
            if shared_drive.drive_name != drive_state.drive_name:
                shared_drive.drive_name = drive_state.drive_name
                shared_drive.save()

            # confirm drive and subscription match
            #
            # an ITBill subscription is being used to pay for additional disk
            # storage space in a Shared Drive.
            #
            # We will assume that in any case the ITBill subscription diverges
            # from current state that the state should be adjusted to match
            # the subscription

            expecting_subscription = (
                drive_state.quota_limit != subsidized_quota
            )

            sdr = shared_drive.shareddriverecord_set.get()
            sub = get_current_subscription(sdr)
            have_subscription = sub is not None

            if not expecting_subscription and not have_subscription:
                # most common case - drive using subsidized quota
                continue

            elif have_subscription and not expecting_subscription:
                # at subsidized quota, not what subscription specifies
                # set quota for
                quota = get_subscription_quota_gigabytes(sub)
                set_drive_quota(
                    quota=quota,
                    drive_id=drive_id,
                )

            elif expecting_subscription and have_subscription:
                "confirm quota in alignment"
                raise NotImplementedError()
            elif expecting_subscription and not have_subscription:
                # subscription (presumed) closed/ cancelled
                # in absense of a subscription, become subsidized
                set_drive_quota(
                    quota=subsidized_quota,
                    drive_id=drive_id,
                )

    def get_prt_drive_ids(self):
        """
        Return drive_id values for all drives PRT expects report data for.

        This includes all drives not explicited deleted.
        """
        # ids = SharedDrive.objects.values_list("drive_id")
        objs = SharedDrive.objects.filter(is_deleted__isnull=True)
        ids = objs.values_list("drive_id", flat=True)
        return set(ids)

    def is_current_employee(self, uwnetid):
        # for shared drives, only include members/managers that are in
        # the uw_employee group since we'll be showing managers that aren't
        # able to do anything about the subscription since their access to
        # prt will be denied.
        return is_group_member(uwnetid, group="uw_employee")

    def GoogleDriveState_by_drive_id(self):
        """
        Return a dict with drive state information

        key: drive_id
        value: list of GoogleDriveState objects referring to that drive_id.
        """
        # TODO: FIX THIS! Use a build that validates e.g.,
        # consistent drive_name on a per-append basis...
        result = collections.defaultdict(list)

        for gds in get_google_drive_states():
            result[gds.drive_id].append(gds)

        return result
