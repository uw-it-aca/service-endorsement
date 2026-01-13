# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from persistent_message.models import Message
from django.db.models import Q
import hashlib


def get_persistent_messages(tags=None, params={}):
    ret = {}

    for message in _active_messages(tags=tags):
        level = message.get_level_display().lower()
        if level not in ret:
            ret[level] = []

        msg_text = message.render(params)
        ret[level].append({
            'message': msg_text,
            'hash': hashlib.md5(msg_text.encode()).hexdigest()
        })

    return ret


def _active_messages(level=None, tags=None):
    now = Message.current_datetime()

    kwargs = {'begins__lte': now}
    if level is not None:
        kwargs['level'] = level

    if tags and len(tags):
        kwargs['tags__name__in'] = tags
    else:
        kwargs['tags__isnull'] = True

    return Message.objects.filter(
        Q(expires__gt=now) | Q(expires__isnull=True), **kwargs).order_by(
            '-level', '-begins').distinct()
