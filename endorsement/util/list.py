# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


def distinct(seq):
    """Return a list of distinct items in the order they were found."""
    return [x for x in {x for x in seq}]
