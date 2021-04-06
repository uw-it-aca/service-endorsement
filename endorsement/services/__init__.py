# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
"""
Base class for endorsed services encapsulating common support functions
and lifecycle values

By default, all services defined by the EndorsementServiceBase class
are available for endorsement, but this list can be overridded by the
ENDORSEMENT_SERVICES setting, where endorsement classes are either
listed individually or all grouped together by "['*']".
"""

from django.conf import settings
from endorsement.models import EndorsementRecord
from endorsement.dao.endorse import (
    is_permitted, get_endorsement, initiate_endorsement,
    store_endorsement, clear_endorsement)
from endorsement.dao.user import get_endorsee_model
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.uwnetid_categories import shared_netid_has_category
from endorsement.exceptions import NoEndorsementException, UnrecognizedUWNetid

from abc import ABC, abstractmethod
from importlib import import_module
from os import listdir
import re

# Services available for endorsement
ENDORSEMENT_SERVICES = None

# Default lifecycle day counts
DEFAULT_ENDORSEMENT_LIFETIME = 365
DEFAULT_ENDORSEMENT_GRACETIME = 90
PRIOR_DAYS_NOTICE_WARNING_1 = 90
PRIOR_DAYS_NOTICE_WARNING_2 = 30
PRIOR_DAYS_NOTICE_WARNING_3 = 7
PRIOR_DAYS_NOTICE_WARNING_4 = 0


class EndorsementServiceBase(ABC):
    """
    Properties and methods to support creating, revoking, renewing and
    expiring service endorsements.
    """

    @property
    @abstractmethod
    def service_name(self):
        """Service name slug"""
        pass

    @property
    @abstractmethod
    def category_code(self):
        """Endorsed service's UW-IAM Category"""
        pass

    @property
    @abstractmethod
    def subscription_codes(self):
        """Endorsed services UW-IAM Subscription code list"""
        pass

    @property
    @abstractmethod
    def service_renewal_statement(self):
        """Statement to include with renewal notification"""
        pass

    @property
    @abstractmethod
    def service_link(self):
        """URL to end-user information about the endorsed service"""
        pass

    @property
    @abstractmethod
    def shared_params(self):
        return {
            'roles': [],
            'types': [],
            'excluded_categories': [],
            'allow_existing_endorsement': False
        }

    @property
    def supports_shared_netids(self):
        return ((len(self.shared_params['roles']) > 0) or
                (self.shared_params['types'] is not None and
                 len(self.shared_params['types']) > 0))

    @property
    def category_name(self):
        """Service's presentable name"""
        return dict(
            EndorsementRecord.CATEGORY_CODE_CHOICES)[self.category_code]

    @property
    def endorsement_lifetime(self):
        return DEFAULT_ENDORSEMENT_LIFETIME

    @property
    def endorsement_graceperiod(self):
        return DEFAULT_ENDORSEMENT_GRACETIME

    def get_endorsement(self, endorser, endorsee):
        return get_endorsement(endorser, endorsee, self.category_code)

    def valid_endorsee(self, endorsee, endorser):
        if self.valid_person_endorsee(endorsee):
            return True

        for supported in get_supported_resources_for_netid(endorser.netid):
            if endorsee.netid == supported.name:
                return self.valid_supported_netid(supported, endorser)

        return False

    def valid_person_endorsee(self, endorsee):
        return endorsee.is_person

    def valid_supported_netid(self, resource, endorser):
        """

        Based on roles and types associated with shared netids that are
        elible for endorsement as well as associated categories that
        exclude otherwise eligible netids.
        """
        return (self.supports_shared_netids
                and ((self.valid_supported_role(resource)
                      and self.valid_supported_type(resource)
                      and not self.invalid_supported_category(resource))
                     or self.valid_existing_endorsement(resource, endorser)))

    def valid_supported_role(self, resource):
        roles = self.shared_params.get('roles', '*')
        return (roles == '*' or resource.role in roles)

    def valid_supported_type(self, resource):
        # length based on https://wiki.cac.washington.edu/x/YYkW
        max_length = 29

        types = self.shared_params.get('types', '*')
        return ((types == '*' or resource.netid_type in types) and
                len(resource.netid_type) <= max_length)

    def invalid_supported_category(self, supported):
        return shared_netid_has_category(
            supported.name, self.shared_params['excluded_categories'])

    def valid_existing_endorsement(self, resource, endorser):
        if self.shared_params['allow_existing_endorsement']:
            try:
                self.get_endorsement(
                    endorser, get_endorsee_model(resource.name))
                return True
            except (NoEndorsementException, UnrecognizedUWNetid):
                pass

        return False

    def is_permitted(self, endorser, endorsee):
        try:
            self.get_endorsement(endorser, endorsee)
            return True, True
        except NoEndorsementException:
            return is_permitted(
                endorser, endorsee, self.subscription_codes), False

    def initiate_endorsement(self, endorser, endorsee, reason):
        return initiate_endorsement(
            endorser, endorsee, reason, self.category_code)

    def store_endorsement(self, endorser, endorsee, acted_as, reason):
        return store_endorsement(
            endorser, endorsee, self.category_code,
            self.subscription_codes, acted_as, reason)

    def clear_endorsement(self, endorser, endorsee):
        return clear_endorsement(self.get_endorsement(endorser, endorsee))

    def endorsement_expiration_warning(self, level=1):
        """
        for the given warning message level, return days prior to
        expiration that a warning should be sent.

        level 1 is the first warning, level 2 the second and so on
        to final warning at 0 days before expiration
        """
        try:
            return [
                PRIOR_DAYS_NOTICE_WARNING_1,
                PRIOR_DAYS_NOTICE_WARNING_2,
                PRIOR_DAYS_NOTICE_WARNING_3,
                PRIOR_DAYS_NOTICE_WARNING_4
            ][level - 1]
        except IndexError:
            return None


def endorsement_services():
    """Return endorsement service list

    Loads all defined service modules unless settings specifies otherwise
    """
    global ENDORSEMENT_SERVICES

    if ENDORSEMENT_SERVICES is None:
        ENDORSEMENT_SERVICES = _load_endorsement_services()

    return ENDORSEMENT_SERVICES


def _load_endorsement_services():
    endorsement_services = []

    module_names = getattr(settings, 'ENDORSEMENT_SERVICES', ["*"])
    if module_names and module_names[0] == '*':
        module_names = [s.split('.')[0]
                        for s in listdir('endorsement/services')
                        if re.match(r'^[a-z].*\.py$', s)]

    for module_name in module_names:
        try:
            module = import_module(
                "endorsement.services.{}".format(module_name))
        except Exception as ex:
            raise Exception(
                "Cannot load module {}: {}".format(module_name, ex))

        endorsement_services.append(getattr(
            module, 'EndorsementService')())

    endorsement_services.sort(key=lambda s: s.category_name)
    return endorsement_services


def endorsement_categories():
    categories = [s.category_code for s in endorsement_services()]
    categories.sort()
    return categories


def endorsement_services_context():
    return {service.service_name: {
        'category_code': service.category_code,
        'category_name': service.category_name,
        'service_link': service.service_link
    } for service in endorsement_services()}


def service_names(service_list=None):
    names = service_list if service_list else service_name_list()
    return '{} and {}'.format(', '.join(names[:-1]), names[-1]) if (
        len(names) > 1) else names[0]


def service_name_list():
    return [s.category_name for s in endorsement_services()]


def get_endorsement_service(service_ref):
    """
    Return endorsment service based on service name
    """
    if isinstance(service_ref, str):
        key = 'service_name'
    elif isinstance(service_ref, int):
        key = 'category_code'
    else:
        return None

    return next((s for s in endorsement_services() if (
        service_ref == getattr(s, key))), None)
