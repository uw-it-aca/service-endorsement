from restclients_core.dao import DAO
from restclients_core.exceptions import DataFailureException


class PRT_DAO(DAO):
    def service_name(self):
        return 'prt'


def kerberos_inactive_url(category):
    return "/krl/stats/prt/cat{}.csv".format(category)


def get_kerberos_inactive_netids_for_category(category):
    url = kerberos_inactive_url(category)
    response = PRT_DAO().getURL(url)

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    return response.data.strip().split('\n')