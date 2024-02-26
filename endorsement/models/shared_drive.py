# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin
from endorsement.util.date import datetime_to_str
import json


class Manager(ExportModelOperationsMixin('manager'), models.Model):
    """
    Manager model represents user who is responsible the given
    shared drive and corresponding subscription.
    """
    netid = models.SlugField(max_length=32,
                             db_index=True,
                             unique=True)
    display_name = models.CharField(max_length=256,
                                    null=True)
    regid = models.CharField(max_length=32,
                             db_index=True,
                             unique=True)
    is_valid = models.BooleanField(default=False)

    def __eq__(self, other):
        return other is not None and self.regid == other.regid

    def json_data(self):
        return {
            "netid": self.netid,
            "display_name": self.display_name,
            "regid": self.regid,
            "is_valid": self.is_valid
            }

    def __str__(self):
        return json.dumps(self.json_data())


class SharedDriveTier(
        ExportModelOperationsMixin('shared_drive_tier'), models.Model):
    """
    SharedDriveTier model represents the shared drive tier.
    It mainly serves to cache specific shared drive values
    for quickly displaying details for the given manager's tier.
    """
    tier_id = models.SlugField(max_length=32, null=True)
    quota = models.IntegerField(null=True)
    name = models.CharField(max_length=64, null=True)
    def json_data(self):
        return {
            "tier_id": self.tier_id,
            "quota": self.quota,
            "name": self.name
            }


class SharedDriveRecord(
        ExportModelOperationsMixin('shared_drive_record'), models.Model):
    """
    SharedDriveRecord model represents the binding between a 
    shared drive and its corresponding subscription, and preserves
    various states and timestamps to manage its lifecycle. 
    """
    manager = models.ForeignKey(
        Manager, on_delete=models.PROTECT)
    subscription_id = models.SlugField(max_length=32, null=True)
    shared_drive_id = models.SlugField(max_length=32, null=True)
    shared_drive_tier = models.ForeignKey(
        SharedDriveTier, on_delete=models.PROTECT)
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

    def json_data(self):
        return {
            "manager": self.manager.json_data(),
            "subscription_id": self.subscription_id,
            "shared_drive_tier": self.shared_drive_tier.json_data(),
            "shared_drive_id": self.shared_drive_id,
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
