from django.db import models
from django.utils import timezone


def datetime_to_str(d_obj):
    if d_obj is not None:
        return d_obj.strftime("%Y-%m-%d %H:%M:%S")
    return None


class Endorser(models.Model):
    uwnetid = models.SlugField(max_length=16,
                               db_index=True,
                               unique=True)
    uwregid = models.CharField(max_length=32,
                               null=True,
                               db_index=True,
                               unique=True)
    is_faculty = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    last_visit = models.DateTimeField(default=timezone.now())

    def json_data(self):
        return {
            "uwnetid": self.uwnetid,
            "uwregid": self.uwregid,
            "is_faculty": self.is_faculty,
            "is_staff": self.is_staff,
            "last_visit": datetime_to_str(self.last_visit)
            }

    class Meta:
        db_table = "uw_service_endorsement_endorser"


class Endorsee(models.Model):
    uwnetid = models.SlugField(max_length=16,
                               db_index=True,
                               unique=True)
    uwregid = models.CharField(max_length=32,
                               null=True,
                               db_index=True,
                               unique=True)

    def json_data(self):
        return {
            "uwnetid": self.uwnetid,
            "uwregid": self.uwregid
            }

    class Meta:
        db_table = "uw_service_endorsement_endorsee"
