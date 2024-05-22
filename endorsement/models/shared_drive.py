# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json

from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin

from endorsement.models.base import RecordManagerBase
from endorsement.models.itbill import ITBillSubscription
from endorsement.util.date import datetime_to_str
from endorsement.policy import DEFAULT_LIFETIME
from endorsement.util.itbill.shared_drive import (
    itbill_form_url, shared_drive_subsidized_quota,
    shared_drive_subscription_deadline)


class MemberManager(models.Manager):
    def get_member(self, netid):
        member, _ = self.get_or_create(netid=netid)
        return member


class Member(ExportModelOperationsMixin("member"), models.Model):
    """
    Member represents user associated with a shared drive
    """

    netid = models.CharField(max_length=128)

    def json_data(self):
        return self.netid

    objects = MemberManager()

    def __str__(self):
        return json.dumps(self.json_data())


class Role(ExportModelOperationsMixin("role"), models.Model):
    """
    Role assigned to user in Google shared drive.

    There are two versions of this documentation:
    - https://developers.google.com/drive/api/guides/ref-roles (dev-oriented)
    - https://support.google.com/a/users/answer/12380484?hl=en (user-oriented)

    The roles are slightly out of alignment (dev has 6; user has 5)
    """

    # per Ken Stribling in MSCA we can use these translations
    MANAGER_ROLE = "organizer"
    CONTENT_MANAGER = "fileOrganizer"

    role = models.CharField(max_length=32)

    def json_data(self):
        return self.role

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDriveMember(
    ExportModelOperationsMixin("shared_drive_member"), models.Model
):
    """
    Member model represents users/groups responsible the given
    shared drive and corresponding subscription.
    """

    member = models.ForeignKey(Member, on_delete=models.PROTECT)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)

    def json_data(self):
        return {
            "netid": self.member.json_data(),
            "role": self.role.json_data(),
        }

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDriveQuota(
    ExportModelOperationsMixin("shared_drive_tier"), models.Model
):
    """
    SharedDriveQuota model represents a quota (tier)

    Quota limit is represnted as an integer number of Gigabytes
    """

    org_unit_id = models.CharField(max_length=32)
    org_unit_name = models.CharField(max_length=64)
    quota_limit = models.IntegerField(default=0)

    @property
    def is_subsidized(self):
        return self.quota_limit <= shared_drive_subsidized_quota()

    def json_data(self):
        return {
            "org_unit_id": self.org_unit_id,
            "org_unit_name": self.org_unit_name,
            "quota_limit": self.quota_limit,
            "is_subsidized": self.is_subsidized,
        }

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDrive(ExportModelOperationsMixin("shared_drive"), models.Model):
    """
    SharedDrive model represents a shared drive, its current quota
    and its members
    """

    # NOTE: maximum observed is 19 characters (2024-05-16)
    drive_id = models.SlugField(max_length=25)
    drive_name = models.CharField(max_length=128)
    drive_quota = models.ForeignKey(SharedDriveQuota, on_delete=models.PROTECT)
    drive_usage = models.IntegerField(null=True)
    members = models.ManyToManyField(SharedDriveMember, blank=True)
    query_date = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(null=True)

    def get_members(self):
        return [m.member.netid for m in self.members.all()]

    def json_data(self):
        return {
            "drive_id": self.drive_id,
            "drive_name": self.drive_name,
            "drive_usage": self.drive_usage,
            "drive_quota": self.drive_quota.json_data(),
            "members": [m.json_data() for m in self.members.all()],
        }

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDriveRecordManager(RecordManagerBase):
    def get_member_drives(self, member_netid, drive_id=None):
        parms = {
            "shared_drive__members__member__netid": member_netid,
            "is_deleted__isnull": True,
        }

        if drive_id:
            parms["shared_drive__drive_id"] = drive_id

        return self.filter(**parms).order_by('shared_drive__drive_name')

    def get_record_by_drive_id(self, drive_id):
        return self.get(
            shared_drive__drive_id=drive_id, is_deleted__isnull=True
        )

    def get_over_quota_non_subscribed(self):
        quota = shared_drive_subsidized_quota()
        return self.filter(
            datetime_over_quota_emailed__isnull=True,
            shared_drive__drive_quota__quota_limit__gt=quota,
            subscription__isnull=True,
            is_deleted__isnull=True,
        )


class SharedDriveRecord(
    ExportModelOperationsMixin("shared_drive_record"), models.Model
):
    """
    SharedDriveRecord model represents the binding between a
    shared drive and its corresponding subscription, and preserves
    various states and timestamps to manage its lifecycle.
    """

    shared_drive = models.ForeignKey(SharedDrive, on_delete=models.PROTECT)
    subscription = models.ForeignKey(
        ITBillSubscription, on_delete=models.PROTECT, null=True
    )
    datetime_created = models.DateTimeField(null=True)
    datetime_accepted = models.DateTimeField(null=True)
    datetime_emailed = models.DateTimeField(null=True)
    datetime_notice_1_emailed = models.DateTimeField(null=True)
    datetime_notice_2_emailed = models.DateTimeField(null=True)
    datetime_notice_3_emailed = models.DateTimeField(null=True)
    datetime_notice_4_emailed = models.DateTimeField(null=True)
    datetime_over_quota_emailed = models.DateTimeField(null=True)
    datetime_expired = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(null=True)

    objects = SharedDriveRecordManager()

    @property
    def expiration_date(self):
        return (
            self.datetime_expired
            or (self.datetime_accepted + timezone.timedelta(
                days=DEFAULT_LIFETIME
            ))
            if (self.datetime_accepted)
            else (
                (self.datetime_created + timezone.timedelta(
                    DEFAULT_LIFETIME
                ))
                if (self.datetime_created)
                else None
            )
        )

    def get_itbill_key_remote(self):
        """
        Compute 'key_remote' field for ITBill.
        """
        # if changing be sure this does not exceed the max_length of
        # ITBillSubscription.key_remote
        key_remote = f"prt_sd_{self.shared_drive.drive_id}"
        return key_remote

    @property
    def itbill_form_url(self):
        return itbill_form_url(
            self.subscription.key_remote, self.shared_drive.drive_name) if (
                self.subscription) else None

    @property
    def acceptor(self):
        if not self.datetime_accepted:
            return None

        try:
            return SharedDriveAcceptance.objects.get(
                shared_drive_record=self,
                datetime_created=self.datetime_accepted,
            )
        except SharedDriveAcceptance.DoesNotExist:
            return None

    def get_acceptance(self):
        return SharedDriveAcceptance.objects.filter(shared_drive_record=self)

    def set_acceptance(self, member_netid, accept=True, acted_as=None):
        member = Member.objects.get_member(member_netid)
        acted_as_member = Member.objects.get_member(
            acted_as) if acted_as else None
        action = (
            SharedDriveAcceptance.ACCEPT
            if (accept)
            else SharedDriveAcceptance.REVOKE
        )

        acceptance = SharedDriveAcceptance.objects.create(
            shared_drive_record=self, action=action,
            member=member, acted_as=acted_as_member
        )

        if accept:
            self.datetime_accepted = acceptance.datetime_accepted
        else:
            self.datetime_expired = acceptance.datetime_accepted

        self.save()

    def update_subscription(self, itbill):
        self.subscription.from_json(itbill)
        self.subscription.save()
        self.save()

    def json_data(self):
        return {
            "drive": self.shared_drive.json_data(),
            "subscription": (
                self.subscription.json_data() if (self.subscription) else None
            ),
            "itbill_form_url": self.itbill_form_url,
            "datetime_created": datetime_to_str(self.datetime_created),
            "datetime_emailed": datetime_to_str(self.datetime_emailed),
            "datetime_notice_1_emailed": datetime_to_str(
                self.datetime_notice_1_emailed
            ),
            "datetime_notice_2_emailed": datetime_to_str(
                self.datetime_notice_2_emailed
            ),
            "datetime_notice_3_emailed": datetime_to_str(
                self.datetime_notice_3_emailed
            ),
            "datetime_notice_4_emailed": datetime_to_str(
                self.datetime_notice_4_emailed
            ),
            "datetime_accepted": datetime_to_str(self.datetime_accepted),
            "acceptance": [a.json_data() for a in self.get_acceptance()],
            "datetime_expired": datetime_to_str(self.datetime_expired),
            "datetime_expiration": datetime_to_str(self.expiration_date),
            "datetime_subscription_deadline": datetime_to_str(
                shared_drive_subscription_deadline()),
            "is_deleted": self.is_deleted,
        }

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDriveAcceptance(
    ExportModelOperationsMixin("shared_drive_acceptance"), models.Model
):
    """
    SharedDriveAcceptance model records each instance of a shared drive
    record being accepted or revoked by a shared drive manager.
    """

    ACCEPT = 0
    REVOKE = 1

    ACCEPTANCE_ACTION_CHOICES = ((ACCEPT, "Accept"), (REVOKE, "Revoke"))

    shared_drive_record = models.ForeignKey(
        SharedDriveRecord, on_delete=models.PROTECT
    )
    member = models.ForeignKey(
        Member, on_delete=models.PROTECT, related_name='member')
    acted_as = models.ForeignKey(
        Member, on_delete=models.PROTECT, null=True, related_name='acted_as')
    action = models.SmallIntegerField(
        default=ACCEPT, choices=ACCEPTANCE_ACTION_CHOICES
    )
    datetime_created = models.DateTimeField(auto_now_add=True)

    def json_data(self):
        return {
            "member": self.member.json_data(),
            "acted_as": self.acted_as.json_data() if acted_as else None,
            "action": self.ACCEPTANCE_ACTION_CHOICES[self.action][1],
            "datetime_created": datetime_to_str(self.datetime_createted),
        }

    def __str__(self):
        return json.dumps(self.json_data())
