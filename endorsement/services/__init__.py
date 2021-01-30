from django.conf import settings
from endorsement.models import EndorsementRecord
from endorsement.dao.endorse import (
    is_permitted, get_endorsement, initiate_endorsement, activate_category,
    activate_subscriptions, store_endorsement, clear_endorsement)
from endorsement.exceptions import NoEndorsementException
from importlib import import_module


EXPORTED_SERVICES = []

# Endorsed Service base class


class EndorsementService(object):
    def category_name(self):
        return dict(EndorsementRecord.CATEGORY_CODE_CHOICES)[
            self.category_code()]

    def get_endorsement(self, endorser, endorsee):
        return get_endorsement(endorser, endorsee, self.category_code())

    def is_permitted(self, endorser, endorsee):
        try:
            self.get_endorsement(endorser, endorsee)
            return True, True
        except NoEndorsementException:
            return is_permitted(
                endorser, endorsee, self.subscription_codes()), False

    def initiate_endorsement(self, endorser, endorsee, reason):
        return initiate_endorsement(
            endorser, endorsee, reason, self.category_code())

    def store_endorsement(self, endorser, endorsee, acted_as, reason):
        activate_category(endorsee.netid, self.category_code())
        activate_subscriptions(
            endorsee.netid, endorser.netid, self.subscription_codes())
        return store_endorsement(
            endorser, endorsee, acted_as, reason, self.category_code())

    def clear_endorsement(self, endorser, endorsee):
        return clear_endorsement(self.get_endorsement(endorser, endorsee))


def endorsement_services():
    if len(EXPORTED_SERVICES):
        return EXPORTED_SERVICES

    for module_name in getattr(settings, 'ENDORSEMENT_SERVICES', []):
        module = import_module(module_name)
        service_class = getattr(module, 'exported_service')
        EXPORTED_SERVICES.append(getattr(module, service_class)())

    return EXPORTED_SERVICES


def endorsement_services_context():
    services = {}
    for service in endorsement_services():
        services[service.service_name()] = {
            'category_code': service.category_code(),
            'category_name': service.category_name(),
            'service_link': service.service_link()
        }

    return services


def service_supports_shared(service):
    shared = service.shared_parameters()
    return ((shared['supported_roles'] is not None and
             len(shared['supported_roles']) > 0) or
            (shared['supported_types'] is not None and
             len(shared['supported_types']) > 0))


def service_names():
    names = service_name_list()
    return '{} and {}'.format(', '.join(names[:-1]), names[-1]) if (
        len(names) > 1) else names[0]


def service_name_list():
    return [s.category_name() for s in endorsement_services()]


def get_endorsement_service(service_tag):
    for service in endorsement_services():
        if service_tag == service.service_name():
            return service

    return None
