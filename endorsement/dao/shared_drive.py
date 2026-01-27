# Copyright 2026 UW-IT, University of Washington
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
    expire_subscription,
)
from endorsement.notifications.shared_drive import (
    notify_admin_missing_drive_count_exceeded,
    notify_admin_over_quota_missing_subscription
)
from endorsement.util.itbill.shared_drive import (
    shared_drive_subscription_deadline
)
from endorsement.exceptions import (
    ITBillSubscriptionNotFound,
    SharedDriveNonPrivilegedMember,
    SharedDriveRecordNotFound,
    UnrecognizedUWNetid,
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
    r"^(?P<netid>[^@]+)(@(uw|(u\.)?washington)\.edu)?$", re.I
)
MISSING_DRIVE_THRESHOLD = 500
MISSING_DRIVE_NOTIFICATION = 150


def sync_quota_from_subscription(drive_id):
    """
    apply SharedDriveQuota value to MSCA SharedDrive drive_id
    """
    try:
        record = SharedDriveRecord.objects.get_record_by_drive_id(drive_id)
        if record.subscription is None:
            logger.info(f"sync: Shared drive {drive_id} has no subscription")
            raise ITBillSubscriptionNotFound(drive_id)

        state = record.subscription.state
        if state != ITBillSubscription.SUBSCRIPTION_DEPLOYED:
            logger.info(
                f"sync: Shared drive {drive_id}"
                f" subscription not deployed: {state}"
            )
            return

        default_quota = get_default_quota()
        reconcile_drive_quota(record, no_subscription_quota=default_quota)

    except SharedDriveRecord.DoesNotExist:
        raise SharedDriveRecordNotFound(drive_id)


def expire_shared_drives(gracetime, lifetime):
    """
    Expire shared drives that have exceeded their lifetime.
    """
    for drive in shared_drives_to_expire(gracetime, lifetime):
        shared_drive_lifecycle_expired(drive)


def shared_drive_lifecycle_expired(drive_record):
    """
    Set lifecycle to expired for shared drive

    Actions:
       - set shared_drive quota to 0 (org_unit_name "None"? pending delete?)
       - set subscription end_date to today using:
            - expire_subscription(drive_record)
    """
    logger.error(
        f"Shared drive {drive_record} lifecycle expired: not implemented")


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
        except (SharedDriveNonPrivilegedMember, UnrecognizedUWNetid) as e:
            logger.info(f"{e}")
        except Exception as e:
            logger.error(f"shared drive record: {gds}: {e}")
        else:
            seen_drive_ids.add(gds.drive_id)

    return retval


def load_shared_drive_record(a: GoogleDriveState, is_seen):
    """
    ensure shared drive record is created
    Note: first time we see a record is implicit acceptance
          as the external process of creating the drive
          already lead the manager past terms click thru
    """
    now = dt.datetime.now(dt.timezone.utc)
    shared_drive = upsert_shared_drive(a, is_seen)
    shared_drive_record, _ = SharedDriveRecord.objects.get_or_create(
        shared_drive=shared_drive,
        defaults={"datetime_accepted": now, "datetime_created": now},
    )

    # backfill if missed
    if not shared_drive_record.datetime_accepted:
        shared_drive_record.datetime_accepted = now
        shared_drive_record.save()

    # resurrect if drive previously marked as deleted
    if shared_drive_record.is_deleted:
        shared_drive_record.resurrect()

    return shared_drive_record


def upsert_shared_drive(a: GoogleDriveState, is_seen):
    """
    return a shared drive model for given DriveId, allowing for
    name, quota and membership changes
    """
    if is_seen:
        shared_drive = SharedDrive.objects.get(drive_id=a.drive_id)
    else:
        drive_quota = get_drive_quota(a)
        shared_drive, created = SharedDrive.objects.update_or_create(
            drive_id=a.drive_id,
            defaults={
                "drive_name": a.drive_name,
                "drive_quota": drive_quota,
                "drive_usage": a.size_gigabytes,
                "is_deleted": None,
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
        logger.error(f"Drive has no quota set. Probably in invalid org unit.")

    drive_quota, _ = SharedDriveQuota.objects.update_or_create(
        org_unit_id=a.org_unit_id,
        defaults=defaults,
    )
    return drive_quota


def get_drive_quota_by_quota_limit(quota_limit):
    """
    return a shared drive quota model for given quota_limit
    """
    defaults = {
        "org_unit_name": f"PRT-{quota_limit}GB",
        "org_unit_id": f"PRT-{quota_limit}",
    }

    drive_quota, _ = SharedDriveQuota.objects.get_or_create(
        quota_limit=quota_limit, defaults=defaults)

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
    return a member model, bare netid
    """
    netid_match = netid_regex.match(a.member)
    if netid_match:
        netid = netid_match.group("netid")
        return Member.objects.get_member(netid=netid)
    else:
        msg = "Non-NetID {} excluded"
        raise UnrecognizedUWNetid(msg.format(a.member))


def get_role(a: GoogleDriveState):
    """
    Return a Role model.

    Raises SharedDriveNonPrivilegedMember IFF role is not a manager role.
    """
    # cull non-manager roles until others are interesting
    if a.role != Role.MANAGER_ROLE:
        msg = "member {} is not a manager ({!r}) and instead {!r}"
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
        try:
            load_itbill_subscription(sdr)
            sdr.subscription.save()
            return sdr.subscription
        except ITBillSubscriptionNotFound as ex:
            sub = sdr.subscription
            if sub.state == ITBillSubscription.SUBSCRIPTION_DEPLOYED:
                logger.info("Remote key not found in itbill for drive "
                            f"{ex} in {sub.get_state_display} state.")
            else:
                logger.error(f"Remote key not found in itbill: {ex} "
                             "for drive in deployed state")
            return None

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
        logging.info(f"Update subscription: key_remote = {key_remote}")
        sub = ITBillSubscription(key_remote=key_remote)
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
        return sub.current_quota


def reconcile_drive_quota(
    sdr: SharedDriveRecord, *, no_subscription_quota, no_move_drive=False
):
    current_drive_quota = sdr.shared_drive.drive_quota

    quota_actual = current_drive_quota.quota_limit
    quota_correct = get_expected_shared_drive_record_quota(
        sdr, no_subscription_quota=no_subscription_quota
    )

    if quota_actual == 0:
        logger.info(
            f"reconcile: skip set drive for {sdr.shared_drive.drive_id} "
            f"as the drive has {quota_actual} quota set"
        )
        return

    if not quota_correct:
        logger.info(
            f"reconcile: skip set drive for {sdr.shared_drive.drive_id} "
            "as the subscription contains no current quota"
        )
        return

    # new drives are expected to have no subscription, but they are also
    # expected to have the subsidized quota size
    if (sdr.shared_drive.drive_quota.quota_limit > no_subscription_quota
            and sdr.subscription is None):
        if not no_move_drive:
            notify_admin_over_quota_missing_subscription(
                drive_name=sdr.shared_drive.drive_name,
                drive_id=sdr.shared_drive.drive_id,
                quota_correct=quota_correct)

        logger.info(
            f"reconcile: skip set drive for {sdr.shared_drive.drive_id} "
            "as there is no active subscription")

        return

    if quota_actual != quota_correct:
        if no_move_drive:
            logger.info(
                f"reconcile: SKIP set drive {sdr.shared_drive.drive_id} "
                f"from {quota_actual} to {quota_correct}"
            )
            return

        logger.info(
            f"reconcile: set drive {sdr.shared_drive.drive_id} "
            f"quota from {quota_actual} to {quota_correct} GB"
        )

        try:
            set_drive_quota(
                drive_id=sdr.shared_drive.drive_id, quota=quota_correct
            )
        except Exception as ex:
            logger.error(
                f"reconcile: set_drive_quota: "
                f"drive: {sdr.shared_drive.drive_id} "
                f"to {quota_correct} failed: {ex}"
            )
            return

        # udpate sdr.shared_drive.drive_quota
        drive_quota = get_drive_quota_by_quota_limit(quota_correct)
        sdr.shared_drive.drive_quota = drive_quota
        sdr.shared_drive.save()
    else:
        logger.debug(
            f"reconcile: drive {sdr.shared_drive.drive_id} "
            f"unchanged quota {quota_actual} GB"
        )


class Reconciler:
    """
    Reconciles Shared Drives.
    """

    def __init__(self, *args, **kwargs):
        self.no_move_drive = kwargs.get(
            'no_move_drive', False)
        self.missing_drive_threshold = kwargs.get(
            'missing_drive_threshold', MISSING_DRIVE_THRESHOLD)
        self.missing_drive_notification = kwargs.get(
            'missing_drive_notification',
            MISSING_DRIVE_NOTIFICATION)

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

            reconcile_drive_quota(
                sdr,
                no_subscription_quota=default_quota,
                no_move_drive=self.no_move_drive,
            )

            # TODO: handle lack of provisioning status.
            #   case 1: drive has managers - do we alert them?
            #   case 2: drive has no mangers - ???

    def handle_missing_drives(self, missing_drive_ids, default_quota):
        """
        For drives that no longer exist as reported by MSCA.

        This means the drive no longer exists or no longer has managers.

        If deleted it may be the case the related SharedDriveRecord is
        deleted as well (datetime_deleted set).

        The last manager departing would happen out of band.
        """
        missing_drive_count = len(missing_drive_ids)
        now = dt.datetime.now(dt.timezone.utc)

        logger.info(
            f"reconcile: {missing_drive_count} missing drives")

        drive_context = {
            'missing_drive_count': missing_drive_count,
            'missing_drive_notification': self.missing_drive_notification,
            'missing_drive_threshold': self.missing_drive_threshold
        }

        # failsafe for potentially truncated shared drive report
        if missing_drive_count > self.missing_drive_threshold:
            notify_admin_missing_drive_count_exceeded(**drive_context)
            logger.error(
                f"missing drive count exceeds threshold: "
                f"{missing_drive_count} > {self.missing_drive_threshold}"
            )
            return
        elif missing_drive_count > self.missing_drive_notification:
            notify_admin_missing_drive_count_exceeded(**drive_context)

        for sdr in SharedDriveRecord.objects.filter(
                shared_drive__drive_id__in=missing_drive_ids
        ):
            key_remote = f"key_remote: {sdr.subscription.key_remote}" if (
                sdr.subscription) else "no subscription"
            logger.info(f"delete record for drive {sdr.shared_drive.drive_id}"
                        f" with {key_remote}")

            # TODO: should we be performing any other actions?
            sdr.delete()

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
                except (
                    SharedDriveNonPrivilegedMember,
                    UnrecognizedUWNetid,
                ) as ex:
                    logger.info(
                        f"skip member: drive_id {gds.drive_id}: {ex}")
                else:
                    result.append(member)

            return result

        # END helper functions

        for drive_id in drives:
            drive_states = id_GoogleDriveState[drive_id]
            # drive states are expected to be consistent for most fields
            # notably excepting "member" and "role"
            drive_state = drive_states[0]

            try:
                shared_drive = SharedDrive.objects.get(drive_id=drive_id)

                # TODO: wrap below in a transaction?

                # update drive manager list
                try:
                    managers = managers_for_shared_drive(drive_states)
                    shared_drive.members.set(managers)
                except Exception as ex:
                    logger.error(
                        f"existing drive ({drive_id}): manage update: {ex}")

                # update drive name
                try:
                    if shared_drive.drive_name != drive_state.drive_name:
                        logger.info(f"name change: drive {drive_id} name "
                                    f"{shared_drive.drive_name} to "
                                    f"{drive_state.drive_name}")
                        shared_drive.drive_name = drive_state.drive_name
                        shared_drive.save()
                except Exception as ex:
                    logger.error(
                        f"existing drive ({drive_id}) "
                        f"name ({drive_state.drive_name}) update: {ex}")

                # update shared drive usage
                try:
                    if shared_drive.drive_usage != drive_state.size_gigabytes:
                        logger.info(f"drive usage: drive ({drive_id}) "
                                    f"usage {shared_drive.drive_usage} "
                                    f"updated to {drive_state.size_gigabytes}")
                        shared_drive.drive_usage = drive_state.size_gigabytes
                        shared_drive.save()
                except Exception as ex:
                    logger.error(
                        f"existing drive ({drive_id}) "
                        f"usage ({drive_state.drive_name}) update: {ex}")

                # confirm drive and subscription match
                sdr = SharedDriveRecord.objects.get_record_by_drive_id(
                    drive_id)
                reconcile_drive_quota(
                    sdr,
                    no_subscription_quota=subsidized_quota,
                    no_move_drive=self.no_move_drive,
                )

                # confirm drive still has a provision with
                # current manager list
                # TODO: what do we do if they do not?
                #   case 1: drive still has managers - do we alert them?
                #   case 2: drive has no mangers - ???

            except SharedDrive.DoesNotExist:
                logger.error(f"existing drive ({drive_id}): "
                             f"SharedDrive not found")
            except SharedDriveRecord.DoesNotExist:
                logger.error(f"existing drive ({drive_id}): "
                             f"SharedDriveRecord not found")

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


def get_shared_drives_for_member(member):
    return SharedDriveRecord.objects.get_member_drives(member)
