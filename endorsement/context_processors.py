# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
"""
"""


def is_desktop(request):
    desktopapp = (not getattr(request, 'is_mobile', False) and
                  not getattr(request, 'is_tablet', False))
    return {
        'is_desktop': desktopapp
    }
