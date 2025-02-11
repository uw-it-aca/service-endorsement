# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from persistent_message.models import Message
import hashlib


def get_persistent_messages(tags, params):
    ret = {}

    for message in Message.objects.active_messages(tags=tags):
        level = message.get_level_display().lower()
        if level not in ret:
            ret[level] = []

        msg_text = message.render(params)
        ret[level].append({
            'message': msg_text,
            'hash': hashlib.md5(msg_text.encode()).hexdigest()
        })

    return ret
