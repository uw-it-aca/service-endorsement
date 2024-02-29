# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin
from endorsement.util.date import datetime_to_str
import json


class Member(ExportModelOperationsMixin('member'), models.Model):
    name = models.CharField(max_length=128)

    def json_data(self):
        return self.name

    def __str__(self):
        return json.dumps(self.json_data())


class Role(ExportModelOperationsMixin('role'), models.Model):
    role = models.CharField(max_length=32)

    def json_data(self):
        return self.role

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDriveMember(
        ExportModelOperationsMixin('shared_drive_member'), models.Model):
    """
    Member model represents users/groups responsible the given
    shared drive and corresponding subscription.
    """
    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)

    def json_data(self):
        return {
            "name": self.member.json_data(),
            "role": self.role.json_data()
            }

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDriveQuota(
        ExportModelOperationsMixin('shared_drive_tier'), models.Model):
    """
    SharedDriveQuota model represents a quota (tier)
    """
    org_unit = models.CharField(max_length=32)
    quota_limit = models.IntegerField(null=True)
    name = models.CharField(max_length=64, null=True)

    def json_data(self):
        return {
            "org_unit": self.org_unit,
            "quota": self.quota_limit,
            "name": self.name
        }


class SharedDrive(ExportModelOperationsMixin('shared_drive'), models.Model):
    """
    SharedDrive model represents a shared drive, its current quota
    and its members
    """
    drive_id = models.SlugField(max_length=32)
    drive_name = models.CharField(max_length=128)
    drive_quota = models.ForeignKey(SharedDriveQuota, on_delete=models.PROTECT)
    members = models.ManyToManyField(SharedDriveMember)

    def json_data(self):
        return {
            "drive_id": self.drive_id,
            "drive_name": self.drive_name,
            "drive_quota": self.drive_quota.json_data(),
            "members": [m.json_data() for m in self.members.all()]
        }

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDriveRecordManager(models.Manager):
    def get_shared_drives_for_netid(self, netid):
        return self.filter(
            shared_drive__members__member__name=netid,
            is_deleted__isnull=True)


class SharedDriveRecord(
        ExportModelOperationsMixin('shared_drive_record'), models.Model):
    """
    SharedDriveRecord model represents the binding between a 
    shared drive and its corresponding subscription, and preserves
    various states and timestamps to manage its lifecycle. 
    """
    MANAGER_ROLE = "organizer"

    shared_drive = models.ForeignKey(SharedDrive, on_delete=models.PROTECT)
    subscription_id = models.SlugField(max_length=32, null=True)
    state = models.CharField(max_length=128, null=True)
    acted_as = models.SlugField(max_length=32, null=True)
    datetime_created = models.DateTimeField(null=True)
    datetime_emailed = models.DateTimeField(null=True)
    datetime_notice_1_emailed = models.DateTimeField(null=True)
    datetime_notice_2_emailed = models.DateTimeField(null=True)
    datetime_notice_3_emailed = models.DateTimeField(null=True)
    datetime_notice_4_emailed = models.DateTimeField(null=True)
    datetime_granted = models.DateTimeField(null=True)
    datetime_renewed = models.DateTimeField(null=True)
    datetime_expired = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(null=True)

    objects = SharedDriveRecordManager()

    def json_data(self):
        return {
            "shared_drive": self.shared_drive.json_data(),
            "subscription_id": self.subscription_id,
            "state": self.state,
            "acted_as": self.acted_as,
            "datetime_created": datetime_to_str(self.datetime_created),
            "datetime_emailed": datetime_to_str(self.datetime_emailed),
            "datetime_notice_1_emailed": datetime_to_str(
                self.datetime_notice_1_emailed),
            "datetime_notice_2_emailed": datetime_to_str(
                self.datetime_notice_2_emailed),
            "datetime_notice_3_emailed": datetime_to_str(
                self.datetime_notice_3_emailed),
            "datetime_notice_4_emailed": datetime_to_str(
                self.datetime_notice_4_emailed),
            "datetime_granted": datetime_to_str(self.datetime_granted),
            "datetime_renewed": datetime_to_str(self.datetime_renewed),
            "datetime_expired": datetime_to_str(self.datetime_expired),
            "is_deleted": self.is_deleted
        }

    def __str__(self):
        return json.dumps(self.json_data())
