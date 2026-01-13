# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import secrets


def key_remote():
    return secrets.token_hex(16)
