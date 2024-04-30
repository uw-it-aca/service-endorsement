# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.conf import settings
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin
from endorsement.util.date import datetime_to_str
import secrets
import json


class MemberManager(models.Manager):
    def get_member(self, name):
        member, _ = self.get_or_create(name=name)
        return member


class Member(ExportModelOperationsMixin('member'), models.Model):
    """
    Member represents user associated with a shared drive
    """
    name = models.CharField(max_length=128)

    def json_data(self):
        return self.name

    objects = MemberManager()

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

    Quota limit is represnted as an integer number of Gigabytes
    """
    SUBSIDIZED_QUOTA = 100

    org_unit_id = models.CharField(max_length=32)
    org_unit_name = models.CharField(max_length=64, null=True)
    quota_limit = models.IntegerField(null=True)

    @property
    def is_subsidized(self):
        return self.drive_quota.quota_limit <= self.SUBSIDIZED_QUOTA

    def json_data(self):
        return {
            "org_unit_id": self.org_unit_id,
            "org_unit_name": self.org_unit_name,
            "quota_limit": self.quota_limit,
            "is_subsidized": self.quota_limit <= self.SUBSIDIZED_QUOTA
        }


class SharedDrive(ExportModelOperationsMixin('shared_drive'), models.Model):
    """
    SharedDrive model represents a shared drive, its current quota
    and its members
    """
    drive_id = models.SlugField(max_length=32)
    drive_name = models.CharField(max_length=128)
    drive_quota = models.ForeignKey(SharedDriveQuota, on_delete=models.PROTECT)
    drive_usage = models.IntegerField(null=True)
    members = models.ManyToManyField(SharedDriveMember)
    query_date = models.DateTimeField(null=True)

    def json_data(self):
        return {
            "drive_id": self.drive_id,
            "drive_name": self.drive_name,
            "drive_usage": self.drive_usage,
            "drive_quota": self.drive_quota.json_data(),
            "members": [m.json_data() for m in self.members.all()]
        }

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDriveAcceptance(
        ExportModelOperationsMixin('shared_drive_acceptance'), models.Model):
    """
    SharedDriveAcceptance model records each instance of a shared drive
    record being accepted or revoked by a shared drive manager.
    """
    ACCEPT = 0
    REVOKE = 1

    ACCEPTANCE_ACTION_CHOICES = (
        (ACCEPT, "Accept"),
        (REVOKE, "Revoke"))

    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    action = models.SmallIntegerField(
        default=ACCEPT, choices=ACCEPTANCE_ACTION_CHOICES)
    datetime_accepted = models.DateTimeField(auto_now_add=True)

    def json_data(self):
        return {
            "member": self.member.json_data(),
            "action": self.ACCEPTANCE_ACTION_CHOICES[self.action][1],
            "datetime_accepted": datetime_to_str(self.datetime_accepted)
        }

    def __str__(self):
        return json.dumps(self.json_data())


class ITBillSubscription(
        ExportModelOperationsMixin('itbill_subscription'), models.Model):
    MANAGER_ROLE = "organizer"

    SUBSCRIPTION_DRAFT = 0
    SUBSCRIPTION_PROVISIONING = 1
    SUBSCRIPTION_DEPLOYED = 2
    SUBSCRIPTION_DEPROVISION = 3
    SUBSCRIPTION_CLOSED = 4
    SUBSCRIPTION_CANCELLED = 5
    SUBSCRIPTION_STATE_CHOICES = (
        (SUBSCRIPTION_DRAFT, "Draft"),
        (SUBSCRIPTION_PROVISIONING, "Provisioning"),
        (SUBSCRIPTION_DEPLOYED, "Deployed"),
        (SUBSCRIPTION_DEPROVISION, "Deprovision"),
        (SUBSCRIPTION_CLOSED, "Closed"),
        (SUBSCRIPTION_CANCELLED, "Cancelled")
    )

    PRIORITY_NONE = 0
    PRIORITY_DEFAULT = 1
    PRIORITY_HIGH = 2
    PRIORITY_CHOICES = (
        (PRIORITY_NONE, 'none'),
        (PRIORITY_DEFAULT, 'normal'),
        (PRIORITY_HIGH, 'high')
    )

    key_remote = models.SlugField(max_length=32, unique=True, null=True)
    name = models.CharField(max_length=128, null=True)
    url = models.CharField(max_length=256, null=True)
    state = models.SmallIntegerField(
        default=SUBSCRIPTION_DRAFT, choices=SUBSCRIPTION_STATE_CHOICES)
    query_priority = models.SmallIntegerField(
        default=PRIORITY_DEFAULT, choices=PRIORITY_CHOICES)
    query_datetime = models.DateTimeField(null=True)

    def save(self, *args, **kwargs):
        if not self.key_remote:
            self.key_remote = secrets.token_hex(16)

        if not self.name:
            self.name = getattr(
                settings, "ITBILL_SHARED_DRIVE_NAME_FORMAT", "{}").format(
                    self.shared_drive.drive_id),

        super(SharedDriveSubscription, self).save(*args, **kwargs)

    def json_data(self):
        return {
            "key_remote": self.key_remote,
            "name": self.name,
            "url": self.url,
            "state": self.SUBSCRIPTION_STATE_CHOICES[self.state][1],
            "query_priority": self.PRIORITY_CHOICES[
                self.query_priority][1],
            "query_datetime": datetime_to_str(
                self.query_datetime)
        }

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDriveRecordManager(models.Manager):
    def get_shared_drives_for_netid(self, netid, drive_id=None):
        parms = {
            "shared_drive__members__member__name": netid,
            "is_deleted__isnull": True}

        if drive_id:
            parms["shared_drive__drive_id"] = drive_id

        return self.filter(**parms)

    def get_record_by_drive_id(self, drive_id):
        return self.get(
            shared_drive__drive_id=drive_id, is_deleted__isnull=True)


class SharedDriveRecord(
        ExportModelOperationsMixin('shared_drive_record'), models.Model):
    """
    SharedDriveRecord model represents the binding between a 
    shared drive and its corresponding subscription, and preserves
    various states and timestamps to manage its lifecycle. 
    """

    shared_drive = models.ForeignKey(
        SharedDrive, on_delete=models.PROTECT)
    subscription = models.ForeignKey(
        ITBillSubscription, on_delete=models.PROTECT, null=True)
    acted_as = models.SlugField(max_length=32, null=True)
    datetime_created = models.DateTimeField(null=True)
    datetime_accepted = models.DateTimeField(null=True)
    datetime_emailed = models.DateTimeField(null=True)
    datetime_notice_1_emailed = models.DateTimeField(null=True)
    datetime_notice_2_emailed = models.DateTimeField(null=True)
    datetime_notice_3_emailed = models.DateTimeField(null=True)
    datetime_notice_4_emailed = models.DateTimeField(null=True)
    datetime_renewed = models.DateTimeField(null=True)
    datetime_expired = models.DateTimeField(null=True)
    acceptance = models.ManyToManyField(SharedDriveAcceptance, blank=True)
    is_deleted = models.BooleanField(null=True)

    objects = SharedDriveRecordManager()

    @property
    def expiration_date(self):
        lifespan = getattr(settings, 'SHARED_DRIVE_LIFESPAN_DAYS', 365)
        claim_span = getattr(settings, 'SHARED_DRIVE_CLAIM_DAYS', 30)
        initial_date = (self.datetime_renewed or self.datetime_accepted)
        return (self.datetime_expired or
                (initial_date + timezone.timedelta(days=lifespan)) if (
                    initial_date) else (
                        self.datetime_created + timezone.timedelta(
                            claim_span)) if (
                                self.datetime_created) else None)

    def set_acceptance(self, member_netid, accept=True):
        member = Member.objects.get_member(member_netid)
        action = SharedDriveAcceptance.ACCEPT if (
            accept) else SharedDriveAcceptance.REVOKE

        acceptance = SharedDriveAcceptance.objects.create(
            member=member, action=action)
        self.acceptance.add(acceptance)

        if accept:
            self.datetime_accepted = acceptance.datetime_accepted
        else:
            self.datetime_expired = acceptance.datetime_accepted
            self.is_deleted = True

        self.save()

    def json_data(self):
        return {
            "drive": self.shared_drive.json_data(),
            "subscription": self.subscription.json_data() if (
                self.subscription) else None,
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
            "datetime_accepted": datetime_to_str(self.datetime_accepted),
            "datetime_renewed": datetime_to_str(self.datetime_renewed),
            "datetime_expired": datetime_to_str(self.datetime_expired),
            "datetime_expiration": datetime_to_str(self.expiration_date),
            "is_deleted": self.is_deleted
        }

    def __str__(self):
        return json.dumps(self.json_data())
