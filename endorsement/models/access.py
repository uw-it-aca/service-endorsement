# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin
from endorsement.util.date import datetime_to_str
import json


class Accessor(ExportModelOperationsMixin('accessor'), models.Model):
    name = models.SlugField(max_length=64,
                            db_index=True,
                            unique=True)
    display_name = models.CharField(max_length=256,
                                    null=True)
    is_valid = models.BooleanField(default=False)
    is_shared_netid = models.BooleanField(null=True)
    is_group = models.BooleanField(null=True)

    def json_data(self):
        return {
            "name": self.name,
            "display_name": self.display_name,
            "is_valid": self.is_valid,
            "is_shared_netid": self.is_shared_netid,
            "is_group": self.is_group
            }

    def __eq__(self, other):
        return other is not None and self.name == other.name

    def __str__(self):
        return json.dumps(self.json_data())

    class Meta:
        db_table = 'uw_service_endorsement_accessor'


class Accessee(ExportModelOperationsMixin('accessee'), models.Model):
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
        return other is not None and\
            self.regid == other.regid

    def json_data(self):
        return {
            "netid": self.netid,
            "display_name": self.display_name,
            "regid": self.regid,
            "is_valid": self.is_valid
            }

    def __str__(self):
        return json.dumps(self.json_data())

    class Meta:
        db_table = 'uw_service_endorsement_accessee'


class AccessRecordManager(models.Manager):
    def get_access(self, accessor=None, accessee=None):
        params = {
            'is_deleted__isnull': True
        }

        if accessor:
            params['accessor'] = accessor

        if accessee:
            params['accessee'] = accessee

        if 'accessor' in params and 'accessee' in params:
            return super(AccessRecordManager, self).get(**params)

        return super(AccessRecordManager, self).get_queryset().filter(
            **params)

    def get_access_for_accessor(self, accessor):
        return self.get_access(accessor, None)

    def get_all_access_for_accessor(self, accessor, right_id=None):
        return super(AccessRecordManager, self).get_queryset().filter(
            accessor=accessor)

    def get_access_for_accessee(self, accessee):
        return self.get_access(None, accessee)

    def get_access_for_accessee_re(self, accessee_regex):
        accessees = Accessee.objects.filter(
            netid__regex=r'^{0}$'.format(accessee_regex)).values_list(
                'id', flat=True)

        return super(AccessRecordManager, self).get_queryset().filter(
            accessee_id__in=accessees, is_deleted__isnull=True)

    def get_all_endorsements_for_accessee_re(self, accessee_regex):
        accessees = Accessee.objects.filter(
            netid__regex=r'^{0}$'.format(accessee_regex)).values_list(
                'id', flat=True)

        return super(AccessRecordManager, self).get_queryset().filter(
            accessee_id__in=accessees)

    def emailed(self, id):
        datetime_emailed = timezone.now()
        super(AccessRecordManager, self).get_queryset().filter(
            pk=id, is_deleted__isnull=True).update(
                datetime_emailed=datetime_emailed)


class AccessRecord(
        ExportModelOperationsMixin('access_record'), models.Model):

    accessee = models.ForeignKey(Accessee,
                                 on_delete=models.PROTECT)
    accessor = models.ForeignKey(Accessor,
                                 on_delete=models.PROTECT)
    right_id = models.SlugField(max_length=24, null=True)
    right_name = models.SlugField(max_length=64, null=True)
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

    objects = AccessRecordManager()

    def __eq__(self, other):
        return (other is not None and
                self.accessor == other.accessor and
                self.accessee == other.accessee and
                self.right_id == other.right_id)

    def revoke(self):
        self.datetime_expired = timezone.now()
        self.is_deleted = True
        self.save()

    def json_data(self):
        return {
            "accessor": self.accessor.json_data(),
            "accessee": self.accessee.json_data(),
            "right_id": self.right_id,
            "right_name": self.right_name,
            "acted_as": self.acted_as,
            "datetime_granted": datetime_to_str(self.datetime_granted),
            "datetime_emailed": datetime_to_str(self.datetime_emailed),
            "datetime_renewed": datetime_to_str(self.datetime_renewed),
            "datetime_expired": datetime_to_str(self.datetime_expired),
            "datetime_notice_1_emailed": datetime_to_str(
                self.datetime_notice_1_emailed),
            "datetime_notice_2_emailed": datetime_to_str(
                self.datetime_notice_2_emailed),
            "datetime_notice_3_emailed": datetime_to_str(
                self.datetime_notice_3_emailed),
            "datetime_notice_4_emailed": datetime_to_str(
                self.datetime_notice_4_emailed),
            "is_revoked": self.is_deleted
        }

    def __str__(self):
        return json.dumps(self.json_data())

    class Meta:
        unique_together = (("accessor", "accessee"),)
        db_table = 'uw_service_endorsement_access'
