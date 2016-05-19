"""
This module encapsulates the interactions with the restclients.pws,
provides Person information of the current user
"""

import logging
from django.conf import settings
from restclients.pws import PWS
from userservice.user import UserService


logger = logging.getLogger(__name__)
pws = PWS()


def get_netid_of_current_user():
    return UserService().get_user()


def _get_person_of_current_user():
    """
    Retrieve the person data using the netid of the current user
    """
    return pws.get_person_by_netid(get_netid_of_current_user())


def get_regid_of_current_user():
    """
    Return the regid of the current user
    """
    res = _get_person_of_current_user()
    return res.uwregid
