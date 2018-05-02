from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from uw_uwnetid.models import Category
import hashlib
import random


def datetime_to_str(d_obj):
    if d_obj is not None:
        return d_obj.strftime("%Y-%m-%d %H:%M:%S")
    return None


class Endorser(models.Model):
    netid = models.SlugField(max_length=32,
                             db_index=True,
                             unique=True)
    regid = models.CharField(max_length=32,
                             db_index=True,
                             unique=True)
    display_name = models.CharField(max_length=64,
                                    null=True)
    is_valid = models.NullBooleanField()
    last_visit = models.DateTimeField(null=True)

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid

    def __str__(self):
        return "{%s}" % ', '.join([
            "netid: %s" % self.netid,
            "regid: %s" % self.regid,
            "is_valid: %s" % self.is_valid,
            "last_visit: %s" % datetime_to_str(self.last_visit)
        ])

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid,
            "name": self.display_name,
            "is_valid": self.is_valid,
            "last_visit": datetime_to_str(self.last_visit)
            }

    class Meta:
        db_table = 'uw_service_endorsement_endorser'


class Endorsee(models.Model):
    netid = models.SlugField(max_length=32,
                             db_index=True,
                             unique=True)
    regid = models.CharField(max_length=32,
                             db_index=True,
                             unique=True)
    display_name = models.CharField(max_length=64,
                                    null=True)
    kerberos_active_permitted = models.NullBooleanField(default=False)

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid

    def __str__(self):
        return "{%s}" % ', '.join([
            "netid: %s" % self.netid,
            "regid: %s" % self.regid,
            "name: %s" % self.display_name,
            "is_valid: %s" % self.kerberos_active_permitted
        ])

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid,
            "name": self.display_name,
            "is_valid": self.kerberos_active_permitted
            }

    class Meta:
        db_table = 'uw_service_endorsement_endorsee'


class EndorseeEmail(models.Model):
    """
    Distinct from Endorsee model in that endorsee could be person
    which includes email, or entity (shared, etc) netid without email
    """
    endorsee = models.ForeignKey(Endorsee,
                                 on_delete=models.PROTECT)
    email = models.CharField(max_length=128,
                             null=True)

    def json_data(self):
        return {
            "netid": self.endorsee.netid,
            "email": self.email
            }

    class Meta:
        db_table = 'uw_service_endorsement_endorsee_email'


class EndorsementRecord(models.Model):
    GOOGLE_SUITE_ENDORSEE = Category.GOOGLE_SUITE_ENDORSEE
    OFFICE_365_ENDORSEE = Category.OFFICE_365_ENDORSEE

    CATEGORY_CODE_CHOICES = (
        (OFFICE_365_ENDORSEE, "UW Office 365"),
        (GOOGLE_SUITE_ENDORSEE, "UW G Suite"),
    )

    endorser = models.ForeignKey(Endorser,
                                 on_delete=models.PROTECT)
    endorsee = models.ForeignKey(Endorsee,
                                 on_delete=models.PROTECT)
    category_code = models.SmallIntegerField(
        choices=CATEGORY_CODE_CHOICES)
    reason = models.CharField(max_length=64, null=True)
    accept_salt = models.CharField(max_length=32)
    accept_id = models.CharField(max_length=32, null=True)
    datetime_created = models.DateTimeField(null=True)
    datetime_emailed = models.DateTimeField(null=True)
    datetime_endorsed = models.DateTimeField(null=True)
    datetime_renewed = models.DateTimeField(null=True)
    datetime_expired = models.DateTimeField(null=True)

    def __eq__(self, other):
        return other is not None and\
            self.endorser == other.endorser and\
            self.endorsee == other.endorsee and\
            self.category_code == other.category_code

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
        return hashlib.md5("%s%s%s%s" % (
            self.endorser.netid, endorsee_netid,
            self.category_code, self.accept_salt)).hexdigest()

    def __str__(self):
        return "{%s}" % ', '.join([
            "endorser: %s" % self.endorser,
            "endorsee: %s" % self.endorsee,
            "category_code: %s" % self.category_code,
            "category_name: %s" % self.get_category_code_display(),
            "reason: %s" % self.reason,
            "accept_id: %s" % self.accept_id,
            "datetime_endorsed: %s" % (
                datetime_to_str(self.datetime_endorsed)),
            "datetime_emailed: %s" % (
                datetime_to_str(self.datetime_emailed)),
            "datetime_renewed: %s" % (
                datetime_to_str(self.datetime_renewed)),
            "datetime_expired: %s" % (
                datetime_to_str(self.datetime_expired)),
        ])

    def json_data(self):
        return {
            "endorser": self.endorser.json_data(),
            "endorsee": self.endorsee.json_data(),
            "category_code": self.category_code,
            "category_name": self.get_category_code_display(),
            "reason": self.reason,
            "accept_id": self.accept_id,
            "datetime_endorsed": datetime_to_str(self.datetime_endorsed),
            "datetime_emailed": datetime_to_str(self.datetime_emailed),
            "datetime_renewed": datetime_to_str(self.datetime_renewed),
            "datetime_expired": datetime_to_str(self.datetime_expired),
            "accept_url": self.accept_url()
        }

    def accept_url(self):
        return None if (self.datetime_endorsed) else "%s%s" % (
            getattr(settings, "APP_SERVER_BASE",
                    "http://provision-test.uw.edu"),
            reverse('accept_view',
                    kwargs={'accept_id': self.accept_id}))

    class Meta:
        unique_together = (("endorser", "category_code", "endorsee"),)
        db_table = 'uw_service_endorsement_endorsement'
