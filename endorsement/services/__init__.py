# Copyright 2025 UW-IT, University of Washington
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
from endorsement.models import EndorsementRecord as ER
from endorsement.dao.gws import is_group_member
from endorsement.dao.endorse import (
    get_endorsement, initiate_endorsement,
    store_endorsement, clear_endorsement)
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.uwnetid_categories import shared_netid_has_category
from endorsement.dao.uwnetid_subscriptions import (
    active_subscriptions_for_netid)
from endorsement.exceptions import NoEndorsementException
from endorsement.util.string import listed_list
from uw_uwnetid.models import Category
from restclients_core.exceptions import DataFailureException

from abc import ABC, abstractmethod
from importlib import import_module
from os import listdir
import re

# default group containing valid endorsers
ENDORSER_GROUP = getattr(settings, "VALID_ENDORSER_GROUP", "uw_employee")

# Services available for endorsement
ENDORSEMENT_SERVICES = None


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
    def shared_params(self):
        """
        By default, no shared netids are supported
        If shared support is desired, provide a dict with one or more
        of the following keys:
           - roles: list of supported roles, or '*' to indicate any
           - types: list of supported types, or '*' to indicate any
           - excluded_categories: list of excluded category numbers
        """
        return None

    @property
    def supports_shared_netids(self):
        return (self.shared_params
                and (self.shared_params.get('roles', None)
                     or self.shared_params.get('types', None)
                     or self.shared_params.get('excluded_categories', None)))

    @property
    def category_name(self):
        """Service's presentable name"""
        return dict(ER.CATEGORY_CODE_CHOICES)[self.category_code]

    def get_endorsement(self, endorser, endorsee):
        return get_endorsement(endorser, endorsee, self.category_code)

    def valid_endorser(self, uwnetid):
        return is_group_member(uwnetid, ENDORSER_GROUP)

    def valid_endorsee(self, endorsee, endorser):
        if self.valid_person_endorsee(endorsee):
            return True

        # legacy non-person endorsees
        netid_supported = get_supported_resources_for_netid(endorser.netid)
        if netid_supported is None:
            netid_supported = []

        for supported in netid_supported:
            if endorsee.netid == supported.name:
                return self.valid_supported_netid(supported, endorser)

        return False

    def valid_person_endorsee(self, endorsee):
        return endorsee.is_person

    def valid_supported_netid(self, resource, endorser):
        """
        Based on roles and types associated with shared netids that are
        eligible for endorsement as well as associated categories that
        exclude otherwise eligible netids.
        """
        return (self.supports_shared_netids
                and (self.valid_shared_netid(resource)
                     or self.valid_legacy_shared_netid(resource, endorser)))

    def valid_shared_netid(self, resource):
        return (self.valid_supported_role(resource)
                and self.valid_supported_type(resource)
                and not self.invalid_supported_category(resource))

    def valid_legacy_shared_netid(self, resource, endorser):
        return False

    def valid_supported_role(self, resource):
        """
        acceptable roles are listed, or '*' to accept any role
        """
        try:
            roles = self.shared_params['roles']
            return (roles == '*' or (
                type(roles) == list and resource.role in roles))
        except KeyError:
            return False

    def valid_supported_type(self, resource):
        """
        acceptable types are listed, or '*' to accept any type

        max acceptable length is based on
        https://wiki.cac.washington.edu/x/YYkW
        """
        max_length = 29

        try:
            types = self.shared_params['types']
            return (types == '*' or (
                type(types) == list
                and resource.netid_type
                and resource.netid_type in types
                and len(resource.netid_type) <= max_length))
        except KeyError:
            return False

    def invalid_supported_category(self, supported):
        categories = []

        # shared clinical netids are uniformly disallowed by policy
        try:
            types = self.shared_params['types']
            if ((types == '*' or (type(types) == list and 'shared' in types))
                    and supported.netid_type == 'shared'):
                categories += [Category.ALTID_SHARED_CLINICAL_1]
        except KeyError:
            pass

        try:
            categories += self.shared_params['excluded_categories']
        except KeyError:
            pass

        return shared_netid_has_category(
            supported.name, categories) if len(categories) else False

    def is_permitted(self, endorser, endorsee):
        try:
            self.get_endorsement(endorser, endorsee)
            return True, True
        except NoEndorsementException:
            try:
                return active_subscriptions_for_netid(
                    endorsee.netid, self.subscription_codes), False
            except DataFailureException as ex:
                if getattr(settings, "DEBUG", False) and ex.status == 404:
                    # weirdness for testing with mock data
                    dao = getattr(settings, "RESTCLIENTS_DAO_CLASS", 'File')
                    if dao == 'File':
                        e = ER.objects.get_endorsements_for_endorsee(
                            endorsee, self.category_code)
                        return len(e) > 0, False
                    else:
                        raise

    def initiate_endorsement(self, endorser, endorsee, reason):
        return initiate_endorsement(
            endorser, endorsee, reason, self.category_code)

    def store_endorsement(self, endorser, endorsee, acted_as, reason):
        return store_endorsement(
            endorser, endorsee, self.category_code,
            self.subscription_codes, acted_as, reason)

    def clear_endorsement(self, endorser, endorsee):
        return clear_endorsement(self.get_endorsement(endorser, endorsee))


def is_valid_endorser(uwnetid):
    """
    Return True if any service accepts netid as an endorser
    """
    for service in endorsement_services():
        try:
            if service.valid_endorser(uwnetid):
                return True
        except Exception:
            pass

    return False


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


def service_context(service):
    return {
        'category_code': service.category_code,
        'category_name': service.category_name,
        'service_link': service.service_link
    }


def service_contexts(endorsee=None):
    return {service.service_name: service_context(service)
            for service in endorsement_services() if (
                    endorsee is None
                    or service.valid_person_endorsee(endorsee))}


def service_names(service_list=None):
    return listed_list(service_list if service_list else service_name_list())


def service_name_list():
    return list({s.category_name for s in endorsement_services()})


def get_endorsement_service(service_ref):
    """
    Return endorsment service based on service name
    """
    if isinstance(service_ref, str):
        key = 'service_name'
    elif isinstance(service_ref, int):
        key = 'category_code'
    elif isinstance(service_ref, list):
        key = 'subscription_codes'
    else:
        return None

    return next((s for s in endorsement_services() if (
        service_ref == getattr(s, key))), None)
