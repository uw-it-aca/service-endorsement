from rc_django.cache_implementation import TimedCache
import re


class ProvisionCache(TimedCache):
    """ A custom cache implementation for Provision Request Tool. """

    url_policies = {}
    url_policies["pws"] = (
        (re.compile(r"^/identity/v\d/person/"), 60 * 30),
        (re.compile(r"^/identity/v\d/entity/"), 60 * 30),
    )
    url_policies["gws"] = (
        (re.compile(r"^/group_sws/v2/group/"), 60 * 2),
    )

    def getCache(self, service, url, headers):
        cache_time = self.getCacheTime(service, url)
        if cache_time is not None:
            return self._response_from_cache(service, url, headers, cache_time)
        else:
            return None

    def getCacheTime(self, service, url):
        if service in ProvisionCache.url_policies:
            service_policies = ProvisionCache.url_policies[service]

            for policy in service_policies:
                pattern = policy[0]
                policy_cache_time = policy[1]

                if pattern.match(url):
                    return policy_cache_time
        return

    def processResponse(self, service, url, response):
        if self.getCacheTime(service, url) is not None:
            return self._process_response(service, url, response)
        else:
            return
