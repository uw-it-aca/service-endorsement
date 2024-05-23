# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import collections
import datetime as dt
import re
import logging

# methods are imported to populate namespace and be used elsewhere
from uw_msca.shared_drive import (  # noqa: F401
    get_default_quota,
    get_google_drive_states,
    set_drive_quota,
)
from uw_msca.models import GoogleDriveState

from endorsement.dao.gws import is_group_member
from endorsement.dao.itbill import (
    get_subscription_by_key_remote,
    load_itbill_subscription,
)
from endorsement.exceptions import (
    ITBillSubscriptionNotFound,
    SharedDriveNonPrivilegedMember,
    SharedDriveRecordNotFound,
)
from endorsement.models.itbill import (
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


logger = logging.getLogger(__name__)
netid_regex = re.compile(
    r"^(?P<netid>[^@]+)@(uw|(u\.)?washington)\.edu$", re.I
)


def sync_quota_from_subscription(drive_id):
    """
    apply SharedDriveQuota value to MSCA SharedDrive drive_id
    """
    try:
        record = SharedDriveRecord.objects.get_record_by_drive_id(drive_id)
        if record.subscription is None:
            raise ITBillSubscriptionNotFound(drive_id)

        state = record.subscription.state
        if state == ITBillSubscription.SUBSCRIPTION_DEPLOYED:
            return
        #
        #
        #
        # TODO: work with msca restclient to update shared drive
        #
        #
        #
    except SharedDriveRecord.DoesNotExist:
        raise SharedDriveRecordNotFound(drive_id)


def shared_drive_lifecycle_expired(drive_record):
    """
    Set lifecycle to expired for shared drive
    """
    logger.info(f"Shared drive {drive_record} lifecycle expired")


def load_shared_drives(google_drive_states):
    """
    Populate SharedDriveRecord models as reported by uw_mwsa.
    """
    seen_drive_ids = set()

    for gds in google_drive_states:
        try:
            load_shared_drive_record(
                gds,
                is_seen=gds.drive_id in seen_drive_ids,
            )
        except SharedDriveNonPrivilegedMember as e:
            logger.info(f"{e}")
        except Exception as e:
            logger.error(f"shared drive record: {gds}: {e}")
        else:
            seen_drive_ids.add(gds.drive_id)


def load_shared_drive_record(a: GoogleDriveState, is_seen):
    """
    ensure shared drive record is created
    Note: first time we see a record is implicit acceptance
          as the external process of creating the drive
          already lead the manager past terms click thru
    """
    shared_drive = upsert_shared_drive(a, is_seen)
    if not is_seen:
        # spare a get() since record is already created
        now = dt.datetime.now(dt.timezone.utc)
        shared_drive_record, _ = SharedDriveRecord.objects.get_or_create(
            shared_drive=shared_drive,
            defaults={
                "datetime_accepted": now,
                "datetime_created": now
            }
        )

        # backfill if missed
        if not shared_drive_record.datetime_accepted:
            shared_drive_record.datetime_accepted = now
            shared_drive_record.save()


def upsert_shared_drive(a: GoogleDriveState, is_seen):
    """
    return a shared drive model for given DriveId, allowing for
    name, quota and membership changes
    """
    if is_seen:
        shared_drive = SharedDrive.objects.get(drive_id=a.drive_id)
    else:
        # spare a save() since defaults should NOT change per CSV row
        shared_drive, created = SharedDrive.objects.update_or_create(
            drive_id=a.drive_id,
            defaults={
                "drive_name": a.drive_name,
                "drive_quota": get_drive_quota(a),
                "drive_usage": a.size_gigabytes
            },
        )

        if not created:
            # clear e.g., yesterday's membership and re-add
            shared_drive.members.clear()

    shared_drive_member = get_shared_drive_member(a)
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
    netid_match = netid_regex.match(a.member)
    netid = netid_match.group("netid") if netid_match else a.member

    return Member.objects.get_member(netid=netid)


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


def get_or_load_active_subscription(sdr: SharedDriveRecord):
    """
    Get the active ("deployed") ITBillSubscription for a SharedDriveRecord.

    Returns None if no subscription exists or is not in the "deployed" state.
    """
    sub = load_or_update_subscription(sdr)
    if sub is None:
        return None

    if sub.state != ITBillSubscription.SUBSCRIPTION_DEPLOYED:
        return None

    return sub


def load_or_update_subscription(sdr: SharedDriveRecord):
    """
    Return the ITBillSubscription associated with a SharedDriveRecord.

    If no ITBillSubscription is currently associated checks ITBill and loads
    any subscription found there.

    If an ITBillSubscription is currently associated then checks ITBill and
    updates with current information.

    Returns None if no subscription exists, else the subscription.
    """
    # Do we already have an ITBillSubscription on file?
    if sdr.subscription is not None:
        load_itbill_subscription(sdr)
        sdr.subscription.save()
        return sdr.subscription

    # Does an ITBill subscription exist remotely and we just have to get it?
    key_remote = sdr.get_itbill_key_remote()

    try:
        sub_json = get_subscription_by_key_remote(key_remote)
    except ITBillSubscriptionNotFound:
        # TODO: probably run endorsement.dao.initiate_subscription
        return None
    except Exception:
        logging.exception(
            f"Error attempting to find ITBill subscription for {key_remote}"
        )
        return None  # just raise?
    else:
        sub = ITBillSubscription()
        sub.save()
        sdr.subscription = sub
        sdr.update_subscription(sub_json)
        return sdr.subscription


def get_expected_shared_drive_record_quota(
    sdr: SharedDriveRecord, *, no_subscription_quota
):
    """
    Return quota that should be applied to shared drive record.

    If this drive has a deployed ITBillSubscription, the quota will be whatever
    the subscription specifies.

    Otherwise no_subscription_quota will be returned.

    Returned quota will be an int with implied units GB.
    """
    sub = get_or_load_active_subscription(sdr)
    if sub is None:
        return no_subscription_quota
    else:
        # WARNING: implies there is only 1 provision
        # should we pin this down more? currently ITBillProvision
        # does not maintain enough data to differentiate between
        # a shared drive provision and anything else
        shared_drive_provision = sub.get_provisions().get()
        return shared_drive_provision.current_quantity_gigabytes


def reconcile_drive_quota(sdr: SharedDriveRecord, *, no_subscription_quota):
    drive_quota = sdr.shared_drive.drive_quota

    quota_actual = drive_quota.quota_limit
    quota_correct = get_expected_shared_drive_record_quota(
        sdr, no_subscription_quota=no_subscription_quota
    )

    if quota_actual != quota_correct:
        # TODO: error handling!
        set_drive_quota(
            drive_id=sdr.shared_drive.drive_id, quota=quota_correct
        )
        drive_quota.quota_limit = quota_correct
        drive_quota.save()


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

            if sdr is None:
                # examples:
                # drive_id 0APhs8SozJRR3Uk9PVA; all members in SUSPENDED role
                #   if no drive members have an "organizer" role the
                #   SharedDriveRecord is not created

                # In these cases PRT has no administrator to alert
                # TODO: confirm with dsnorton this should be silently ignored
                continue

            reconcile_drive_quota(sdr, no_subscription_quota=default_quota)

            # TODO: handle lack of provisioning status.
            #   case 1: drive has managers - do we alert them?
            #   case 2: drive has no mangers - ???

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
            sdr = SharedDriveRecord.objects.get_record_by_drive_id(drive_id)
            reconcile_drive_quota(sdr, no_subscription_quota=subsidized_quota)

            # confirm drive still has a provision with current manager list
            # TODO: what do we do if they do not?
            #   case 1: drive still has managers - do we alert them?
            #   case 2: drive has no mangers - ???

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
