"""
Service Endorsement Exceptions
"""
from restclients_core.exceptions import InvalidNetID


class UnrecognizedUWNetid(Exception):
    pass


class NoEndorsementException(Exception):
    pass
