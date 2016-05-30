from django.db import models


def datetime_to_str(d_obj):
    if d_obj is not None:
        return d_obj.strftime("%Y-%m-%d %H:%M:%S")
    return None


class Endorser(models.Model):
    netid = models.SlugField(max_length=16,
                             db_index=True,
                             unique=True)
    regid = models.CharField(max_length=32,
                             db_index=True,
                             unique=True)
    is_valid = models.BooleanField()
    last_visit = models.DateTimeField()

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid

    def __str__(self):
        return "{%s: %s, %s: %s, %s: %s, %s: %s}" % (
            "netid", self.netid,
            "regid", self.regid,
            "is_valid", self.is_valid,
            "last_visit", datetime_to_str(self.last_visit))

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid,
            "is_valid": self.is_valid,
            "last_visit": datetime_to_str(self.last_visit)
            }

    class Meta:
        db_table = "uw_service_endorsement_endorser"


class Endorsee(models.Model):
    netid = models.SlugField(max_length=16,
                             db_index=True,
                             unique=True)
    regid = models.CharField(max_length=32,
                             db_index=True,
                             unique=True)
    # lastname = models.CharField(max_length=64,
    #                             null=True)

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid

    def __str__(self):
        return "{%s: %s, %s: %s}" % (
            "netid", self.netid,
            "regid", self.regid)

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid
            }

    class Meta:
        db_table = "uw_service_endorsement_endorsee"
