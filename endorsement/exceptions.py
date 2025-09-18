# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Service Endorsement Exceptions
"""
from restclients_core.exceptions import InvalidNetID


class UnrecognizedUWNetid(Exception):
    pass


class UnrecognizedGroupID(Exception):
    pass


class SharedUWNetid(Exception):
    pass


class NoEndorsementException(Exception):
    pass


class CategoryFailureException(Exception):
    pass


class SubscriptionFailureException(Exception):
    pass


class MissingReasonException(Exception):
    pass


class TooManyUWNetids(Exception):
    pass


class EmailFailureException(Exception):
    pass


class SharedDriveNonPrivilegedMember(Exception):
    pass


class SharedDriveRecordExists(Exception):
    pass


class SharedDriveRecordNotFound(Exception):
    pass


class ITBillSubscriptionNotFound(Exception):
    pass


class NoAccessRecordException(Exception):
    pass


class NullDelegateException(Exception):
    pass


class AccessRecordException(Exception):
    def __init__(self, *args, **kwargs):
        self.record = kwargs.pop('record', None)
        super().__init__(*args, **kwargs)


class DeletedAccessRecordException(AccessRecordException):
    pass


class TooManyRightsException(AccessRecordException):
    pass


class EmptyDelegateRightsException(AccessRecordException):
    pass


class DelegateRightMismatchException(AccessRecordException):
    pass


class DelegateParameterException(Exception):
    pass
