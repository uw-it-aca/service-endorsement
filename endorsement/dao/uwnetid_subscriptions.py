# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_uwnetid.models import Subscription
from uw_uwnetid.subscription import (
    get_netid_subscriptions, update_subscription)
from restclients_core.exceptions import DataFailureException
from endorsement.exceptions import SubscriptionFailureException
import re
import logging


logger = logging.getLogger(__name__)


def active_subscriptions_for_netid(netid, subscription_codes):
    response = get_netid_subscriptions(netid, subscription_codes)
    for sub in response:
        if (sub.subscription_code in subscription_codes and
                sub.status_code != Subscription.STATUS_UNPERMITTED):
            subscription_codes.remove(sub.subscription_code)
    return len(subscription_codes) == 0


def activate_subscriptions(endorsee_netid, endorser_netid, subscriptions):
    try:
        response_list = update_subscription(
            endorsee_netid, 'activate', subscriptions)

        for response in response_list:
            sub_code = int(response.query['subscriptionCode'])
            if (response.http_status == 200 and
                sub_code in subscriptions and
                    response.result.lower() == 'success'):
                subscriptions.remove(sub_code)

        if len(subscriptions) > 0:
            for response in response_list:
                if response.result.lower() != 'success':
                    logger.error('subscription error: {0}: {1} - {2}'.format(
                            response.query['subscriptionCode'],
                            response.result, response.more_info))

            raise SubscriptionFailureException(
                _error_message(response.more_info))

    except DataFailureException as ex:
        raise SubscriptionFailureException('{0}'.format(ex))


def _error_message(error):
    message = 'Invalid Subscription Response'

    # uwnetid web service has fancy marked-up error responses
    # remap wording here
    print("ERROR ERROR ERROR: {}".format(error))

    custom = re.match(('<p><font color=red><b>ERROR: </b></font>'
                       'UW NetID <b>([^<]+)</b> not present in '
                       'NETID Active Directory.</p>'), error)
    if custom:
        message = "INACTIVE_NETID"

    return message
