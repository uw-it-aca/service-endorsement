# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from endorsement.models import EndorsementRecord as ER
from endorsement.services import get_endorsement_service
from endorsement.dao.notification import notify_invalid_endorser
from uw_saml.utils import is_member_of_group
from importlib import import_module
import logging


logger = logging.getLogger(__name__)


PROVISION_TEST_GROUP = 'u_acadev_provision_test'
PROVISIONER_ACCESS_TEST = 'PROVISIONER_ACCESS_TEST'
_endorser_access = None


def can_view_endorsements(request):
    global _endorser_access

    if not _endorser_access:
        try:
            validation = getattr(settings, PROVISIONER_ACCESS_TEST)
            module, validator = validation.rsplit('.', 1)
            try:
                mod = import_module(module)
            except ImportError as ex:
                logger.error("Cannot import {}: {}".format(
                    PROVISIONER_ACCESS_TEST, ex))
                return False

            try:
                _endorser_access = getattr(mod, validator)
            except AttributeError:
                logger.error("Module {} missing {}".format(
                    PROVISIONER_ACCESS_TEST, validator))
                return False
        except AttributeError:
            _endorser_access = allowed_prod_endorsers

    return _endorser_access(request)


def allowed_prod_endorsers(request):
    return True


def allowed_test_endorsers(request):
    return is_member_of_group(request, getattr(
        settings, "PROVISION_TEST_GROUP", PROVISION_TEST_GROUP))


def validate_endorsers():
    endorsements = ER.objects.filter(
        datetime_endorsed__isnull=False,
        is_deleted__isnull=True,
        endorsee__is_person=True,
        endorser__datetime_emailed__isnull=True)

    for endorser_id in list(set([e.endorser.id for e in endorsements])):
        invalid_endorsements = []
        for endorsement in endorsements.filter(
                endorser__id=endorser_id, endorsee__is_person=True):
            service = get_endorsement_service(endorsement.category_code)
            try:
                if not service.valid_endorser(endorsement.endorser.netid):
                    invalid_endorsements.append(endorsement)
            except Exception as ex:
                logger.error('Validation of {} failed: {}'.format(
                    endorsement.endorser.netid, ex))

        if len(invalid_endorsements) > 0:
            notify_invalid_endorser(invalid_endorsements)
