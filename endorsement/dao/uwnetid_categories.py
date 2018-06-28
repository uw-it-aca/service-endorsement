import logging
from uw_uwnetid.models import Category
from uw_uwnetid.category import get_netid_categories


logger = logging.getLogger(__name__)


def get_shared_categories_for_netid(netid):
    return get_netid_categories(netid, [
        Category.ALTID_SHARED_DEPARTMENTAL,
        Category.ALTID_SHARED_COURSE,
        Category.ALTID_SHARED_SAO,
        Category.ALTID_SHARED_CLINICAL_1,
        Category.ALTID_SUPPORT_DEPARTMENTAL])
