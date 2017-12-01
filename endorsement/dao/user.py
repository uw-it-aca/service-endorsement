import logging
from django.utils import timezone
from endorsement.models.core import Endorser, Endorsee
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.pws import get_endorser_regid, get_endorsee_data
from endorsement.dao.uwnetid_subscription_60 import is_valid_endorsee


logger = logging.getLogger(__name__)


def get_endorser_model(uwnetid):
    """
    return an Endorser object
    @exception: DataFailureException
    """
    uwregid = get_endorser_regid(uwnetid)
    updated_values = {
        'netid': uwnetid,
        'is_valid': is_valid_endorser(uwnetid),
        'last_visit': timezone.now()
    }

    user, created = Endorser.objects.update_or_create(
        regid=uwregid, defaults=updated_values)

    return user, created


def get_endorsee_model(uwnetid):
    """
    return an Endorsee object
    @exception: DataFailureException
    """
    uwregid, display_anme = get_endorsee_data(uwnetid)
    kerberos_active_permitted = is_valid_endorsee(uwnetid)
    user, created = Endorsee.objects.update_or_create(
        regid=uwregid,
        defaults={
            'netid': uwnetid,
            'display_name': display_anme,
            'kerberos_active_permitted': kerberos_active_permitted})

    return user, created
