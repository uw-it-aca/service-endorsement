from django.db import models
from django.utils import timezone


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
    is_valid = models.BooleanField(null=True)
    last_visit = models.DateTimeField(null=True)

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid

    def __str__(self):
        return "{%s: %s, %s: %s, %s: %s, %s: %s}" % (
            "netid", self.netid,
            "regid", self.regid,
            "is_valid", self.is_valid,
            "last_visit", datetime_to_str(self.last_visit)
            )

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid,
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
    kerberos_active_permitted = models.BooleanField(null=True)

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid

    def __str__(self):
        return "{%s: %s, %s: %s, %s: %s, %s: %s}" % (
            "netid", self.netid,
            "regid", self.regid,
            "name", self.display_name,
            "is_valid", self.kerberos_active_permitted,
            )

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid,
            "name": self.display_name,
            "is_valid": self.kerberos_active_permitted
            }

    class Meta:
        db_table = 'uw_service_endorsement_endorsee'


class EndorsementRecord(models.Model):
    endorser = models.ForeignKey(Endorser,
                                 on_delete=models.PROTECT)
    endorsee = models.ForeignKey(Endorsee,
                                 on_delete=models.PROTECT)
    datetime_endorsed = models.DateTimeField(null=True)
    datetime_renewed = models.DateTimeField(null=True)
    datetime_expired = models.DateTimeField(null=True)

    def __eq__(self, other):
        return other is not None and\
            self.endorser == other.endorser and\
            self.endorsee == other.endorsee

    def __str__(self):
        return "{%s: %s, %s: %s, %s: %s, %s: %s, %s: %s}" % (
            "endorser", self.endorser,
            "endorsee", self.endorsee,
            "datetime_endorsed", datetime_to_str(self.datetime_endorsed),
            "datetime_renewed", datetime_to_str(self.datetime_renewed),
            "datetime_expired", datetime_to_str(self.datetime_expired)
            )

    def json_data(self):
        data = {
            "endorser": self.endorser.json_data(),
            "endorsee": self.endorsee.json_data(),
            "datetime_endorsed": datetime_to_str(self.datetime_endorsed),
            "datetime_renewed": datetime_to_str(self.datetime_renewed),
            "datetime_expired": datetime_to_str(self.datetime_expired)
            }
        return data

    class Meta:
        unique_together = (("endorser", "endorsee"),)
        db_table = 'uw_service_endorsement_endorsement'
