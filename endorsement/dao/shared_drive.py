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


def load_shared_drives(file_path):
    """
    populate shared drive models
    """
    with open(file_path, 'r') as csvfile:
        next(csvfile, None)
        for row in csv.reader(csvfile, delimiter=","):
            a = SharedDriveData(row)
            try:
                shared_drive_record = get_shared_drive_record(a)
            except SharedDriveNonPrivilegedMember as ex:
                logger.info(f"{ex}")
            except Exception as ex:
                logger.error(f"shared drive record: {a}: {ex}")


def get_shared_drive_record(a):
    """
    ensure shared drive record is created
    """
    shared_drive = get_shared_drive(a)
    shared_drive_record, _ = SharedDriveRecord.objects.get_or_create(
        shared_drive=shared_drive)
    return shared_drive_record


def get_shared_drive(a):
    """
    return a shared drive model
    """
    drive_quota = get_drive_quota(a)
    shared_drive_member = get_shared_drive_member(a)
    shared_drive, _ = SharedDrive.objects.get_or_create(
        drive_id=a.DriveId, drive_name=a.DriveName, drive_quota=drive_quota)
    shared_drive.members.add(shared_drive_member)
    return shared_drive


def get_drive_quota(a):
    """
    return a shared drive quota model
    """
    drive_quota, _ = SharedDriveQuota.objects.get_or_create(org_unit=a.OrgUnit)
    return drive_quota


def get_shared_drive_member(a):
    """
    return a shared drive member model
    """
    member = get_member(a)
    role = get_role(a)
    shared_drive_member, _ = SharedDriveMember.objects.get_or_create(
        member=member, role=role)
    return shared_drive_member


def get_member(a):
    """
    return a member model, netid-ing as necessary
    """
    is_netid = re.match(
        r'^(?P<netid>[^@]+)@(uw|(u\.)?washington)\.edu$', a.Member, re.I)
    member, _ = Member.objects.get_or_create(
        name=is_netid.group('netid') if is_netid else a.Member)
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


class SharedDriveData(object):
    SHARED_DRIVE_COLUMNS = [
        "DriveId", "DriveName", "TotalMembers", "OrgUnit", "Member",
        "Role", "QueryDate"]

    def __init__(self, row):
        for i, k in enumerate(self.SHARED_DRIVE_COLUMNS):
            setattr(self, k, row[i])
