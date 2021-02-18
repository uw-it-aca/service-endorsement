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
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.uwnetid_categories import shared_netid_has_category
from endorsement.exceptions import NoEndorsementException
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

    # properties required for shared netid service provisioning
    SHARED_SUPPORTED_ROLES = []
    SHARED_SUPPORTED_TYPES = []
    SHARED_EXCLUDED_CATEGORIES = []
    SHARED_ALLOW_EXISTING = False

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
    def service_link(self):
        """URL to end-user information about the endorsed service"""
        pass

    @property
    def supports_shared_netids(self):
        return ((len(self.SHARED_SUPPORTED_ROLES) > 0) or
                (self.SHARED_SUPPORTED_TYPES is not None and
                 len(self.SHARED_SUPPORTED_TYPES) > 0))

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

    def valid_endorsee(self, endorsee):
        if endorsee.is_person:
            return True

        for supported in get_supported_resources_for_netid(endorsee.netid):
            if endorsee.netid == supported.name:
                return self.valid_supported_netid(supported)

        return False

    def valid_supported_netid(self, supported):
        """

        Based on roles and types associated with shared netids that are
        elible for endorsement as well as associated categories that
        exclude otherwise eligible netids.
        """

        # length based on
        # https://wiki.cac.washington.edu/display/SMW/UW+NetID+Namespace
        max_length = 29

        return (self.supports_shared_netids and
                self.valid_shared_netid_role(supported.role) and
                self.valid_shared_netid_type(supported.netid_type) and
                len(supported.netid_type) <= max_length and
                not shared_netid_has_category(
                    supported.name, self.SHARED_EXCLUDED_CATEGORIES))

    def valid_shared_netid_role(self, role):
        """Return whether or not shared netid role is valid for this service
        """
        return (role in self.SHARED_SUPPORTED_ROLES)

    def valid_shared_netid_type(self, netid_type):
        """Return whether or not shared netid type is valid for this service
        """
        return (netid_type in self.SHARED_SUPPORTED_TYPES)

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
        ENDORSEMENT_SERVICES = []

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

            ENDORSEMENT_SERVICES.append(
                getattr(module, 'EndorsementService')())

        ENDORSEMENT_SERVICES.sort(key=lambda s: s.category_name)

    return ENDORSEMENT_SERVICES


def endorsement_categories():
    categories = []
    for service in endorsement_services():
        categories.append(service.category_code)

    categories.sort()
    return categories


def endorsement_services_context():
    services = {}
    for service in endorsement_services():
        services[service.service_name] = {
            'category_code': service.category_code,
            'category_name': service.category_name,
            'service_link': service.service_link
        }

    return services


def service_names():
    names = service_name_list()
    return '{} and {}'.format(', '.join(names[:-1]), names[-1]) if (
        len(names) > 1) else names[0]


def service_name_list():
    return [s.category_name for s in endorsement_services()]


def get_endorsement_service(service_ref):
    """
    Return endorsment service based on service name
    """
    key = ('service_name' if isinstance(service_ref, str) else
           'category_code' if isinstance(service_ref, int) else None)

    if key:
        for service in endorsement_services():
            if service_ref == getattr(service, key):
                return service

    return None
