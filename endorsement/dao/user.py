import logging
from django.utils import timezone
from endorsement.models.core import Endorser, Endorsee, EndorseeEmail
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.pws import get_endorser_data, get_endorsee_data
from endorsement.dao.uwnetid_subscription_60 import is_valid_endorsee
from endorsement.dao.uwnetid_categories import get_shared_categories_for_netid


logger = logging.getLogger(__name__)


def get_endorser_model(uwnetid):
    """
    return an Endorser object
    @exception: DataFailureException
    """
    uwregid, display_name = get_endorser_data(uwnetid)
    updated_values = {
        'netid': uwnetid,
        'display_name': display_name,
        'is_valid': is_valid_endorser(uwnetid),
        'last_visit': timezone.now()
    }

    user, created = Endorser.objects.update_or_create(
        regid=uwregid, defaults=updated_values)

    if created:
        logger.info("Create endorser: %s" % user)

    return user


def get_endorsee_model(uwnetid):
    """
    return an Endorsee object
    @exception: DataFailureException
    """
    uwregid, display_name, email, is_person = get_endorsee_data(uwnetid)
    kerberos_active_permitted = is_valid_endorsee(uwnetid)
    user, created = Endorsee.objects.update_or_create(
        regid=uwregid,
        defaults={
            'netid': uwnetid,
            'display_name': display_name,
            'is_person': is_person,
            'kerberos_active_permitted': kerberos_active_permitted})

    if created:
        logger.info("Create endorsee: %s" % user)

    return user


def get_endorsee_email_model(endorsee, endorser, email=None):
    """
    return an EndorseeEmail object, never updating with Null email.
    @exception: DataFailureException
    """
    if email and len(email):
        endorsee_email, created = EndorseeEmail.objects.update_or_create(
            endorsee=endorsee, endorser=endorser, defaults={'email': email})
    else:
        uwregid, display_name, pws_email, is_person = get_endorsee_data(
            endorsee.netid)
        endorsee_email, created = EndorseeEmail.objects.get_or_create(
            endorsee=endorsee, endorser=endorser,
            defaults={'email': pws_email})

    if created:
        logger.info("Create endorsee email: %s %s %s" % (
            endorsee.netid, endorser.netid, email))

    return endorsee_email


def is_shared_netid(netid):
    for category in get_shared_categories_for_netid(netid):
        if category.category_code == 11 and category.source_code == 4:
            return True

    return False
