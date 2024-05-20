# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.db import models
from django.conf import settings
from django_prometheus.models import ExportModelOperationsMixin
from endorsement.util.date import datetime_to_str, date_to_str
from endorsement.util.key_remote import key_remote
import json


class ITBillSubscription(
    ExportModelOperationsMixin("itbill_subscription"), models.Model
):
    MANAGER_ROLE = "organizer"

    SUBSCRIPTION_DRAFT = 0
    SUBSCRIPTION_PROVISIONING = 1
    SUBSCRIPTION_DEPLOYED = 2
    SUBSCRIPTION_DEPROVISION = 3
    SUBSCRIPTION_CLOSED = 4
    SUBSCRIPTION_CANCELLED = 5
    SUBSCRIPTION_STATE_CHOICES = (
        (SUBSCRIPTION_DRAFT, "draft"),
        (SUBSCRIPTION_PROVISIONING, "provisioning"),
        (SUBSCRIPTION_DEPLOYED, "deployed"),
        (SUBSCRIPTION_DEPROVISION, "deprovision"),
        (SUBSCRIPTION_CLOSED, "closed"),
        (SUBSCRIPTION_CANCELLED, "cancelled"),
    )

    PRIORITY_NONE = 0
    PRIORITY_DEFAULT = 1
    PRIORITY_HIGH = 2
    PRIORITY_CHOICES = (
        (PRIORITY_NONE, "none"),
        (PRIORITY_DEFAULT, "normal"),
        (PRIORITY_HIGH, "high"),
    )

    # We have a high character limit, but we don't recommend a name too long
    #   (<30 is good). - ITBill Questions document
    key_remote = models.SlugField(max_length=32)
    state = models.SmallIntegerField(
        default=SUBSCRIPTION_DRAFT, choices=SUBSCRIPTION_STATE_CHOICES
    )
    query_priority = models.SmallIntegerField(
        default=PRIORITY_DEFAULT, choices=PRIORITY_CHOICES
    )
    query_datetime = models.DateTimeField(null=True)

    def from_json(self, itbill):
        """
        (re)load subscription from itbill data
        """
        (self.state,) = (
            value
            for value, label in ITBillSubscription.SUBSCRIPTION_STATE_CHOICES
            if label == itbill.lifecycle_state
        )
        self.query_priority = ITBillSubscription.PRIORITY_DEFAULT
        self.update_provisions(itbill.provisions)

    def get_provisions(self):
        return ITBillProvision.objects.filter(subscription=self)

    def create_provision(self, provision):
        provision_obj = ITBillProvision.objects.create(
            subscription=self, current_quantity=provision.current_quantity
        )

        provision_obj.from_json(provision)
        print(f"saving provision {provision_obj}")
        provision_obj.save()

    def update_provisions(self, provisions):
        self.clear_provisions()

        product_sys_id = getattr(
            settings, "ITBILL_SHARED_DRIVE_PRODUCT_SYS_ID"
        )
        for provision in provisions:
            if provision.product.sys_id == product_sys_id:
                self.create_provision(provision)

    def clear_provisions(self):
        provisions = self.get_provisions()
        for provision in provisions:
            provision.clear_quantities()

        provisions.delete()

    def json_data(self):
        return {
            "key_remote": self.key_remote,
            "provisions": [p.json_data() for p in self.get_provisions()],
            "state": self.SUBSCRIPTION_STATE_CHOICES[self.state][1],
            "query_priority": self.PRIORITY_CHOICES[self.query_priority][1],
            "query_datetime": datetime_to_str(self.query_datetime),
        }

    def __str__(self):
        return json.dumps(self.json_data())


class ITBillProvision(
    ExportModelOperationsMixin("itbill_provision"), models.Model
):
    """
    ITBillProvision model represents the provisioning of a shared drive
    """

    subscription = models.ForeignKey(
        ITBillSubscription, on_delete=models.PROTECT
    )
    current_quantity = models.IntegerField()

    @property
    def current_quantity_gigabytes(self):
        return (self.current_quantity * 100) + getattr(
            settings, "ITBILL_SHARED_DRIVE_SUBSIDIZED_QUOTA"
        )

    def from_json(self, provision):
        for quantity in provision.quantities:
            self.set_quantity(quantity)

    def get_quantities(self):
        return ITBillQuantity.objects.filter(
            provision=self).order_by('-start_date', '-end_date')

    def set_quantity(self, quantity):
        quantity_obj = ITBillQuantity.objects.create(provision=self)
        quantity_obj.from_json(quantity)
        print(f"saving quantity {quantity_obj}")
        quantity_obj.save()

    def clear_quantities(self):
        quantities = ITBillQuantity.objects.filter(provision=self)
        quantities.delete()

    def json_data(self):
        return {
            "quantities": [q.json_data() for q in self.get_quantities()],
            "current_quantity": self.current_quantity,
        }

    def __str__(self):
        return json.dumps(self.json_data())


class ITBillQuantity(
    ExportModelOperationsMixin("itbill_quantity"), models.Model
):
    """
    ITBillQuantity quanity is billable units of 100GB each

    ITBillProvision tracks the current quantity; this tracks the historical
    changes to that quantity, including the current quantity.
    """

    provision = models.ForeignKey(ITBillProvision, on_delete=models.PROTECT)
    quantity = models.IntegerField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    stage = models.CharField(max_length=32, null=True)

    @property
    def quantity_gigabytes(self):
        return (self.quantity * 100) + getattr(
            settings, "ITBILL_SHARED_DRIVE_SUBSIDIZED_QUOTA"
        )

    def from_json(self, quantity):
        self.quantity = int(quantity.quantity)
        self.start_date = quantity.start_date
        self.end_date = quantity.end_date
        self.stage = quantity.stage

    def json_data(self):
        return {
            "quantity": self.quantity,
            "quota_limit": self.quantity_gigabytes,
            "start_date": date_to_str(self.start_date),
            "end_date": date_to_str(self.end_date),
            "stage": self.stage,
        }

    def __str__(self):
        return json.dumps(self.json_data())
