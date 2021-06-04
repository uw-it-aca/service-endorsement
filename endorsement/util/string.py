# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
String routines
"""


def listed_list(l):
    """Return presentable string from given list
    """
    return '{} and {}'.format(', '.join(l[:-1]), l[-1]) if len(l) > 1 else l[0]
