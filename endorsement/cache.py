# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from memcached_clients import RestclientPymemcacheClient
import re


ONE_MINUTE = 60
HALF_HOUR = 60 * 30
ONE_HOUR = 60 * 60


class RestClientsCache(RestclientPymemcacheClient):
    def get_cache_expiration_time(self, service, url, status=200):
        if "pws" == service:
            if re.match(r"^/identity/v\d/person/", url):
                return HALF_HOUR

            if re.match(r"^/identity/v\d/entity/", url):
                return HALF_HOUR

        if "gws" == service:
            if re.match(r"^/group_sws/v\d/group/", url):
                return 2 * ONE_MINUTE

        if "uwnetid" == service:
            re_nws_base = (r"^/nws/v\d(-eval)?/uwnetid/"
                           r"[a-z][a-z0-9\-\_\.]{,127}")
            nws_supported = re.compile(
                r"{}/supported.json".format(re_nws_base))
            nws_category = re.compile(r"{}/category".format(re_nws_base))

            if nws_supported.match(url):
                return ONE_HOUR

            if nws_category.match(url):
                return ONE_HOUR
