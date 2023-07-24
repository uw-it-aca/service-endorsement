# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import re

UW_EMAIL_DOMAIN = "uw.edu"


def uw_email_address(name):
    return name if (re.match('^[^@]+@(.+)$', name)) else "{}@{}".format(
        name, UW_EMAIL_DOMAIN)
