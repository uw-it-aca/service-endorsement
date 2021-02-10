import logging
from uw_uwnetid.models import Category
from uw_uwnetid.category import get_netid_categories, update_catagory
from restclients_core.exceptions import DataFailureException
from endorsement.exceptions import CategoryFailureException


logger = logging.getLogger(__name__)


def is_active_category(category):
    return category.status_code == Category.STATUS_ACTIVE


def is_endorsed(endorsement):
    for cat in get_netid_categories(
            endorsement.endorsee.netid, endorsement.category_code):
        if cat.category_code == endorsement.category_code:
            return is_active_category(cat)

    return False


def set_active_category(netid, category_code):
    """
    return with given netid activated in category_code
    """
    _update_category(netid, category_code, Category.STATUS_ACTIVE)


def set_former_category(netid, category_code):
    """
    return with given netid category code set to former state
    """
    _update_category(netid, category_code, Category.STATUS_FORMER)


def _update_category(netid, category_code, status):
    try:
        response = update_catagory(netid, category_code, status)
        if response['responseList'][0]['result'].lower() != "success":
            raise CategoryFailureException(
                '{0}'.format(response['responseList'][0]['result']))
    except (KeyError, DataFailureException) as ex:
        raise CategoryFailureException('{0}'.format(ex))


def get_shared_categories_for_netid(netid):
    return get_netid_categories(netid, [
        Category.ALTID_SHARED_DEPARTMENTAL,
        Category.ALTID_SHARED_COURSE,
        Category.ALTID_SHARED_SAO,
        Category.ALTID_SHARED_CLINICAL_1,
        Category.ALTID_SUPPORT_DEPARTMENTAL])
