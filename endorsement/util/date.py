# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


def datetime_to_str(d_obj):
    return d_obj.strftime("%Y-%m-%d %H:%M:%S") if d_obj else None
