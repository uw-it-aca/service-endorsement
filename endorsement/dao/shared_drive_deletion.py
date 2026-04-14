# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_msca.shared_drive import mark_drive_for_deletion as _delete_drive
from uw_msca.shared_drive import rescue_drive_from_deletion as _rescue_drive
from restclients_core.exceptions import DataFailureException
import logging


logger = logging.getLogger(__name__)


def mark_drive_for_deletion(drive_id):
    try:
        logger.info(f"Expire shared drive {drive_id} mark for deletion")
        return _delete_drive(drive_id)
    except DataFailureException as ex:
        logger.error(f"Expire shared drive {drive_id} failed: {ex}")

    return None


def rescue_drive_from_deletion(shared_drive):
    """
        Restore OrgUnit for shared drive previously marked for deletion

        Actions:
           - call msca rescue method with original drive quota
    """
    try:
        logger.info("Rescue shared drive {shared_drive.drive_name} "
                    f"({shared_drive.drive_id}) from deletion")
        return _rescue_drive(
            shared_drive.drive_quota.quota_limit,
            shared_drive.drive_id)
    except Exception as ex:
        logger.error(
            f"Rescue shared drive {shared_drive.drive_name} "
            f"({shared_drive.drive_id}) from deletion failed: {ex}")

    return None
