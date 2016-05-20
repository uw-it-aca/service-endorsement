"""
This module encapsulates the interactions with
the UW Affiliation Group API resource
"""

import logging
from django.conf import settings
from restclients.gws import GWS
from endorsement.dao.user import get_netid_of_current_user


logger = logging.getLogger(__name__)
gws = GWS()


def _is_member(groupid):
    """
    Return True if the current user netid is
    an effective member of the given group
    """
    return gws.is_effective_member(groupid,
                                   get_netid_of_current_user())


def is_staff():
    """
    Return True if the user is an UW staff currently
    """
    return _is_member('uw_staff')


def is_faculty():
    """
    Return True if the user is an UW faculty currently
    """
    return _is_member('uw_faculty')
