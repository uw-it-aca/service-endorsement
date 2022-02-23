# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
String utilities
"""


def listed_list(list_list):
    """Return presentable string from given list
    """
    return '{} and {}'.format(', '.join(list_list[:-1]), list_list[-1]) if (
        len(list_list) > 1) else list_list[0]
