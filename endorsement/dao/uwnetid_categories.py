import logging
from uw_uwnetid.category import get_netid_categories


logger = logging.getLogger(__name__)


def get_shared_categories_for_netid(netid):
    return get_netid_categories(netid, [11, 12])
