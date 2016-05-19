import hashlib
from datetime import datetime
from django.utils import timezone
from django.db import models


class User(models.Model):
    uwnetid = models.SlugField(max_length=16,
                               db_index=True,
                               unique=True)

    uwregid = models.CharField(max_length=32,
                               null=True,
                               db_index=True,
                               unique=True)

    last_visit = models.DateTimeField(default=timezone.now())

    class Meta:
        db_table = "uw_service_endorsement_user"
