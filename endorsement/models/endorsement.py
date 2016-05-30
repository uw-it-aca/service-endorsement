from django.db import models
from endorsement.models.user import Endorsee, Endorser, datetime_to_str


class Endorsement(models.Model):
    endorser = models.ForeignKey(Endorser, on_delete=models.PROTECT)
    endorsee = models.ForeignKey(Endorsee, on_delete=models.PROTECT)
    datetime_endorsed = models.DateTimeField(null=True)
    datetime_renewed = models.DateTimeField(null=True)
    datetime_expired = models.DateTimeField(null=True)

    def __eq__(self, other):
        return other is not None and\
            self.endorser == other.endorser and\
            self.endorsee == other.endorsee

    def json_data(self):
        data = {
            "endorser_netid": self.endorser.netid,
            "endorsee_netid": self.endorsee.netid,
            "datetime_endorsed": datetime_to_str(self.datetime_endorsed),
            "datetime_renewed": datetime_to_str(self.datetime_renewed),
            "datetime_expired": datetime_to_str(self.datetime_expired)
            }
        return data

    class Meta:
        unique_together = (("endorser", "endorsee"),)
        db_table = "uw_service_endorsement_endorsement"
