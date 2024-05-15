# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.conf import settings


def subscription_name(shared_drive_record):
    return getattr(settings, "ITBILL_SHARED_DRIVE_NAME_FORMAT", "{}").format(
        shared_drive_record.shared_drive.drive_name)


def product_sys_id():
    return getattr(settings, "ITBILL_SHARED_DRIVE_PRODUCT_SYS_ID")


def shared_drive_subsidized_quota():
    return getattr(settings, "ITBILL_SHARED_DRIVE_SUBSIDIZED_QUOTA")
