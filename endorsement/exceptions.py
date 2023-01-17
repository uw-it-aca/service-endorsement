# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Service Endorsement Exceptions
"""
from restclients_core.exceptions import InvalidNetID


class UnrecognizedUWNetid(Exception):
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
