# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings
from datetime import datetime


def subscription_name(shared_drive_record):
    return getattr(settings, "ITBILL_SHARED_DRIVE_NAME_FORMAT", "{}").format(
        shared_drive_record.shared_drive.drive_name)


def product_sys_id():
    return getattr(settings, "ITBILL_SHARED_DRIVE_PRODUCT_SYS_ID")


def itbill_form_url_base():
    return getattr(settings, "ITBILL_FORM_URL_BASE")


def itbill_form_url_base_id():
    return getattr(settings, "ITBILL_FORM_URL_BASE_ID")


def itbill_form_sys_id():
    return getattr(settings, "ITBILL_FORM_URL_SYS_ID")


def itbill_form_url(key_remote, drive_name):
    return (
        f"{itbill_form_url_base()}sp?id={itbill_form_url_base_id()}"
        f"&sys_id={itbill_form_sys_id()}"
        f"&remote_key={key_remote}&shared_drive={drive_name}"
    )


def shared_drive_subsidized_quota():
    return getattr(settings, "ITBILL_SHARED_DRIVE_SUBSIDIZED_QUOTA")


def shared_drive_subscription_deadline():
    deadline = getattr(settings, "ITBILL_SUBSCRIPTION_DEADLINE")
    return datetime.strptime(deadline, "%m/%d/%Y") if deadline else None
