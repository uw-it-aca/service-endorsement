from restclients_core.dao import DAO
from restclients_core.exceptions import DataFailureException
from endorsement.services import endorsement_categories
from os.path import abspath, dirname
import urllib3
import os


class PRT_DAO(DAO):
    def service_name(self):
        return 'prt'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]


def kerberos_inactive_url(category):
    return "/krl/stats/prt/cat{}.csv".format(category)


def get_kerberos_inactive_netids():
    urllib3.disable_warnings()

    inactive_netids = []
    for category in endorsement_categories():
        inactive_netids += get_kerberos_inactive_netids_for_category(category)

    return [netid for netid in set(inactive_netids) if len(netid) > 0]


def get_kerberos_inactive_netids_for_category(category):
    url = kerberos_inactive_url(category)
    response = PRT_DAO().getURL(url)

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    return response.data.decode('utf-8').strip().split('\n')
