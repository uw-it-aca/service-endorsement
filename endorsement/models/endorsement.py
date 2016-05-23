from django.db import models
from django.utils import timezone
from endorsement.models.user import Endorsee, Endorser, datetime_to_str


class Endorsement(models.Model):
    endorser = models.ForeignKey(Endorser, on_delete=models.PROTECT)
    endorsee = models.ForeignKey(Endorsee, on_delete=models.PROTECT)
    datetime_endorsed = models.DateTimeField(default=timezone.now())
    datetime_renewed = models.DateTimeField(default=timezone.now())
    datetime_expired = models.DateTimeField(null=True)

    def json_data(self):
        data = {
            "endorser_uwnetid": self.endorser.uwnetid,
            "endorsee_uwnetid": self.endorsee.uwnetid,
            "datetime_endorsed": datetime_to_str(self.datetime_endorsed),
            "datetime_renewed": datetime_to_str(self.datetime_renewed),
            "datetime_expired": datetime_to_str(self.datetime_expired)
            }
        return data

    class Meta:
        unique_together = (("endorser", "endorsee"),)
        db_table = "uw_service_endorsement_endorsement"
