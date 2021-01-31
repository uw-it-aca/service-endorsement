from django.conf import settings
from endorsement.models import EndorsementRecord
from endorsement.dao.endorse import (
    is_permitted, get_endorsement, initiate_endorsement, activate_category,
    activate_subscriptions, store_endorsement, clear_endorsement)
from endorsement.exceptions import NoEndorsementException
from abc import ABC, abstractmethod
from importlib import import_module
from os import listdir
import re

ENDORSEMENT_SERVICES = None


class EndorsementServiceBase(ABC):
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
    @abstractmethod
    def shared_parameters(self):
        """Shared UWNetId requirements

        Defines roles and types associated with shared netids that are
        elible for endorsement as well as associated categories that
        exclude otherwise eligible netids.
        """
        return {
            'supported_roles': [],
            'supported_types': [],
            'excluded_categories': [],
        }

    @property
    def supports_shared(self):
        return (self.shared_parameters is not None and
                ((self.shared_parameters['supported_roles'] is not None and
                  len(self.shared_parameters['supported_roles']) > 0) or
                 (self.shared_parameters['supported_types'] is not None and
                  len(self.shared_parameters['supported_types']) > 0)))

    @property
    def category_name(self):
        """Service's presentable name"""
        return dict(
            EndorsementRecord.CATEGORY_CODE_CHOICES)[self.category_code]

    def get_endorsement(self, endorser, endorsee):
        return get_endorsement(endorser, endorsee, self.category_code)

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
        activate_category(endorsee.netid, self.category_code)
        activate_subscriptions(
            endorsee.netid, endorser.netid, self.subscription_codes)
        return store_endorsement(
            endorser, endorsee, acted_as, reason, self.category_code)

    def clear_endorsement(self, endorser, endorsee):
        return clear_endorsement(self.get_endorsement(endorser, endorsee))


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
            module = import_module(
                "endorsement.services.{}".format(module_name))
            ENDORSEMENT_SERVICES.append(
                getattr(module, 'EndorsementService')())

    return ENDORSEMENT_SERVICES


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


def get_endorsement_service(service_tag):
    for service in endorsement_services():
        if service_tag == service.service_name:
            return service

    return None
