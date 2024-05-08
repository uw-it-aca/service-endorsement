# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.models.shared_drive import (
    SharedDriveMember, Member, Role, SharedDrive,
    SharedDriveQuota, SharedDriveRecord)
from endorsement.exceptions import SharedDriveNonPrivilegedMember
import csv
import re
import logging


logger = logging.getLogger(__name__)
netid_regex = re.compile(
    r'^(?P<netid>[^@]+)@(uw|(u\.)?washington)\.edu$', re.I)


def shared_drive_lifecycle_expired(drive_record):
    """
    Set lifecycle to expired for shared drive
    """
    logger.info(f"Shared drive {drive_record} lifecycle expired")


def load_shared_drives_from_csv(file_path):
    """
    populate shared drive models
    """
    seen_shared_drives = set()
    columns = None
    with open(file_path, 'r') as csvfile:
        for row in csv.reader(csvfile, delimiter=","):
            try:
                if columns:
                    a = DataFromRow(row=row, columns=columns)
                    load_shared_drive_record(
                        a, a.DriveId in seen_shared_drives)
                    seen_shared_drives.add(a.DriveId)
                else:
                    columns = list(filter(None, row))
            except SharedDriveNonPrivilegedMember as ex:
                logger.info(f"{ex}")
            except Exception as ex:
                logger.error(f"shared drive record: {a}: {ex}")


def load_shared_drive_record(a, is_seen):
    """
    ensure shared drive record is created
    """
    shared_drive = upsert_shared_drive(a, is_seen)
    shared_drive_record, _ = SharedDriveRecord.objects.get_or_create(
        shared_drive=shared_drive)
    return shared_drive_record


def upsert_shared_drive(a, is_seen):
    """
    return a shared drive model for given DriveId, allowing for
    name, quota and membership chantges
    """
    drive_quota = get_drive_quota(a)
    shared_drive_member = get_shared_drive_member(a)
    shared_drive, created = SharedDrive.objects.update_or_create(
        drive_id=a.DriveId, defaults={
            'drive_name': a.DriveName,
            'drive_quota': drive_quota})

    if not created and not is_seen:
        shared_drive.members.clear()

    shared_drive.members.add(shared_drive_member)
    return shared_drive


def get_drive_quota(a):
    """
    return a shared drive quota model from OrgUnit
    """
    drive_quota, _ = SharedDriveQuota.objects.get_or_create(org_unit=a.OrgUnit)
    return drive_quota


def get_shared_drive_member(a):
    """
    return a shared drive member model from Member and Role
    """
    member = get_member(a)
    role = get_role(a)
    shared_drive_member, _ = SharedDriveMember.objects.get_or_create(
        member=member, role=role)
    return shared_drive_member


def get_member(a):
    """
    return a member model, bare netid or non-uw email
    """
    netid = netid_regex.match(a.Member)
    member, _ = Member.objects.get_or_create(
        name=netid.group('netid') if netid else a.Member)
    return member


def get_role(a):
    """
    return a role model
    """
    # cull non-manager roles until others are interesting
    if a.Role != SharedDriveRecord.MANAGER_ROLE:
        raise SharedDriveNonPrivilegedMember(
            f"Shared drive member {a.Member} is not a manager")

    role, _ = Role.objects.get_or_create(role=a.Role)
    return role


class DataFromRow(object):
    def __init__(self, *args, **kwargs):
        columns = kwargs.get('columns', [])
        row = kwargs.get('row', [])

        for i, k in enumerate(columns):
            setattr(self, k, row[i])
