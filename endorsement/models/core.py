# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin
from uw_uwnetid.models import Category
import hashlib
import random
import json


def datetime_to_str(d_obj):
    if d_obj is not None:
        return d_obj.strftime("%Y-%m-%d %H:%M:%S")
    return None


class Endorser(ExportModelOperationsMixin('endorser'), models.Model):
    netid = models.SlugField(max_length=32,
                             db_index=True,
                             unique=True)
    regid = models.CharField(max_length=32,
                             db_index=True,
                             unique=True)
    display_name = models.CharField(max_length=256,
                                    null=True)
    is_valid = models.BooleanField(null=True)
    datetime_emailed = models.DateTimeField(null=True)
    last_visit = models.DateTimeField(null=True)

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid,
            "name": self.display_name,
            "is_valid": self.is_valid,
            "last_visit": datetime_to_str(self.last_visit)
            }

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid

    def __str__(self):
        return json.dumps(self.json_data())

    class Meta:
        db_table = 'uw_service_endorsement_endorser'


class Endorsee(ExportModelOperationsMixin('endorsee'), models.Model):
    netid = models.SlugField(max_length=32,
                             db_index=True,
                             unique=True)
    regid = models.CharField(max_length=32,
                             db_index=True,
                             unique=True)
    display_name = models.CharField(max_length=256,
                                    null=True)
    is_person = models.BooleanField(null=True,default=True)
    kerberos_active_permitted = models.BooleanField(null=True,default=False)

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid,
            "name": self.display_name,
            "is_valid": self.kerberos_active_permitted,
            "is_person": self.is_person
            }

    def __str__(self):
        return json.dumps(self.json_data())

    class Meta:
        db_table = 'uw_service_endorsement_endorsee'


class EndorseeEmail(
        ExportModelOperationsMixin('endorsee_email'), models.Model):
    """
    Distinct from Endorsee model in that endorsee could be person
    which includes email, or entity (shared, etc) netid without email
    """
    endorsee = models.ForeignKey(Endorsee,
                                 on_delete=models.PROTECT)
    endorser = models.ForeignKey(Endorser,
                                 null=True,
                                 on_delete=models.PROTECT)
    email = models.CharField(max_length=128,
                             null=True)

    def json_data(self):
        return {
            "netid": self.endorsee.netid,
            "email": self.email
            }

    def __str__(self):
        return json.dumps(self.json_data())

    class Meta:
        db_table = 'uw_service_endorsement_endorsee_email'


class EndorsementRecordManager(models.Manager):
    def get_endorsement(self, endorser=None, endorsee=None,
                        category_code=None):
        params = {
            'is_deleted__isnull': True
        }

        if endorser:
            params['endorser'] = endorser

        if endorsee:
            params['endorsee'] = endorsee

        if category_code:
            params['category_code'] = category_code

        if 'endorser' in params and 'endorsee' in params:
            return super(EndorsementRecordManager, self).get(**params)

        return super(EndorsementRecordManager, self).get_queryset().filter(
            **params)

    def get_endorsements_for_endorser(self, endorser, category_code=None):
        return self.get_endorsement(endorser, None, category_code)

    def get_all_endorsements_for_endorser(self, endorser, category_code=None):
        return super(EndorsementRecordManager, self).get_queryset().filter(
            endorser=endorser)

    def get_endorsements_for_endorsee(self, endorsee, category_code=None):
        return self.get_endorsement(None, endorsee, category_code)

    def get_endorsements_for_endorsee_re(self, endorsee_regex):
        endorsees = Endorsee.objects.filter(
            netid__regex=r'^{0}$'.format(endorsee_regex)).values_list(
                'id', flat=True)

        return super(EndorsementRecordManager, self).get_queryset().filter(
            endorsee_id__in=endorsees, is_deleted__isnull=True)

    def get_all_endorsements_for_endorsee_re(self, endorsee_regex):
        endorsees = Endorsee.objects.filter(
            netid__regex=r'^{0}$'.format(endorsee_regex)).values_list(
                'id', flat=True)

        return super(EndorsementRecordManager, self).get_queryset().filter(
            endorsee_id__in=endorsees)

    def emailed(self, id):
        datetime_emailed = timezone.now()
        super(EndorsementRecordManager, self).get_queryset().filter(
            pk=id, is_deleted__isnull=True).update(
                datetime_emailed=datetime_emailed)

    def get_accept_endorsement(self, accept_id, endorsed=None):
        params = {
            'accept_id': accept_id,
            'is_deleted__isnull': True
        }

        if endorsed is not None:
            params['datetime_endorsed__isnull'] = False if (
                endorsed is True) else True

        return super(EndorsementRecordManager, self).get_queryset().filter(
            **params)

    def get_unendorsed_unnotified(self):
        return super(EndorsementRecordManager, self).get_queryset().filter(
            datetime_emailed__isnull=True,
            datetime_endorsed__isnull=True,
            is_deleted__isnull=True)

    def get_endorsed_unnotified(self):
        return super(EndorsementRecordManager, self).get_queryset().filter(
            datetime_emailed__isnull=True,
            datetime_endorsed__isnull=False,
            is_deleted__isnull=True)


class EndorsementRecord(
        ExportModelOperationsMixin('endorsement_record'), models.Model):
    GOOGLE_SUITE_ENDORSEE = Category.GOOGLE_SUITE_ENDORSEE
    OFFICE_365_ENDORSEE = Category.OFFICE_365_ENDORSEE
    CANVAS_PROVISIONEE = Category.CANVAS_PROVISIONEE
    ZOOM_LICENSED_PROVISIONEE = Category.ZOOM_LICENSED_PROVISIONEE
    ZOOM_BASIC_PROVISIONEE = Category.ZOOM_BASIC_PROVISIONEE
    HUSKY_ONNET_EXT_PROVISIONEE = Category.HUSKY_ONNET_EXT_PROVISIONEE

    CATEGORY_CODE_CHOICES = (
        (OFFICE_365_ENDORSEE, "UW Office 365"),
        (GOOGLE_SUITE_ENDORSEE, "UW Google"),
        (CANVAS_PROVISIONEE, "Canvas and Panopto"),
        (ZOOM_LICENSED_PROVISIONEE, "UW Zoom Licensed"),
        (ZOOM_BASIC_PROVISIONEE, "UW Zoom Basic"),
        (HUSKY_ONNET_EXT_PROVISIONEE, "Husky OnNet for Affiliates"),
    )

    endorser = models.ForeignKey(Endorser,
                                 on_delete=models.PROTECT)
    endorsee = models.ForeignKey(Endorsee,
                                 on_delete=models.PROTECT)
    category_code = models.SmallIntegerField(
        choices=CATEGORY_CODE_CHOICES)
    reason = models.CharField(max_length=64, null=True)
    acted_as = models.SlugField(max_length=32, null=True)
    accept_salt = models.CharField(max_length=32)
    accept_id = models.CharField(max_length=32, null=True,
                                 unique=True)
    datetime_created = models.DateTimeField(null=True)
    datetime_emailed = models.DateTimeField(null=True)
    datetime_notice_1_emailed = models.DateTimeField(null=True)
    datetime_notice_2_emailed = models.DateTimeField(null=True)
    datetime_notice_3_emailed = models.DateTimeField(null=True)
    datetime_notice_4_emailed = models.DateTimeField(null=True)
    datetime_endorsed = models.DateTimeField(null=True)
    datetime_renewed = models.DateTimeField(null=True)
    datetime_expired = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(null=True)

    objects = EndorsementRecordManager()

    def __eq__(self, other):
        return (other is not None and
                self.endorser == other.endorser and
                self.endorsee == other.endorsee and
                self.category_code == other.category_code)

    def save(self, *args, **kwargs):
        if not self.accept_salt:
            self.accept_salt = "".join(
                ["0123456789abcdef"[
                    random.randint(0, 0xF)] for _ in range(32)])

        if not self.accept_id:
            self.accept_id = self.get_accept_id(self.endorsee.netid)
        super(EndorsementRecord, self).save(*args, **kwargs)

    def valid_endorsee(self, endorsee_netid):
        return self.accept_id == self.get_accept_id(endorsee_netid)

    def get_accept_id(self, endorsee_netid):
        val = "{0}{1}{2}{3}".format(
            self.endorser.netid, endorsee_netid,
            self.category_code, self.accept_salt)
        return hashlib.md5(val.encode()).hexdigest()

    def revoke(self):
        self.datetime_expired = timezone.now()
        self.is_deleted = True
        self.save()

    def json_data(self):
        return {
            "endorser": self.endorser.json_data(),
            "endorsee": self.endorsee.json_data(),
            "category_code": self.category_code,
            "category_name": self.get_category_code_display(),
            "reason": self.reason,
            "acted_as": self.acted_as,
            "accept_id": self.accept_id,
            "datetime_endorsed": datetime_to_str(self.datetime_endorsed),
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
            "is_revoked": self.is_deleted,
            "accept_url": self.accept_url()
        }

    def accept_url(self):
        return None if (self.datetime_endorsed) else "{0}{1}".format(
            getattr(settings, "APP_SERVER_BASE",
                    "http://test.provision.uw.edu"),
            reverse('accept_view',
                    kwargs={'accept_id': self.accept_id}))

    def __str__(self):
        return json.dumps(self.json_data())

    class Meta:
        unique_together = (("endorser", "category_code", "endorsee"),)
        db_table = 'uw_service_endorsement_endorsement'
