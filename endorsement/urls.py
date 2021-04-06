# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.urls import re_path
from endorsement.views import page
from endorsement.views.accept import accept
from endorsement.views.support.endorsee_search import endorsee_search
from endorsement.views.support.notifications import endorsee_notifications
from endorsement.views.support.endorsement_statistics import (
    endorsement_statistics)
from endorsement.views.api.validate import Validate
from endorsement.views.api.endorse import Endorse
from endorsement.views.api.accept import Accept
from endorsement.views.api.endorsee import Endorsee
from endorsement.views.api.endorsed import Endorsed
from endorsement.views.api.shared import Shared
from endorsement.views.api.statistics import Statistics
from endorsement.views.api.notification import Notification


urlpatterns = [
    re_path(r'^logout', page.logout, name='logout'),
    re_path(r'^accept/(?P<accept_id>[A-Za-z0-9]{32})$',
            accept, name='accept_view'),
    re_path(r'^admin/endorsee', endorsee_search, name='endorsee_search'),
    re_path(r'^admin/notifications', endorsee_notifications,
            name='endorsee_notifications'),
    re_path(r'^admin/statistics', endorsement_statistics,
            name='endorsement_statistics'),
    re_path(r'^api/v1/validate', Validate.as_view(), name='validate_api'),
    re_path(r'^api/v1/endorsee/(?P<endorsee>.+)$',
            Endorsee.as_view(), name='endorsee_api'),
    re_path(r'^api/v1/stats/(?P<type>.+)$',
            Statistics.as_view(), name='statistics_api'),
    re_path(r'^api/v1/endorsed', Endorsed.as_view(), name='endorsed_api'),
    re_path(r'^api/v1/endorse', Endorse.as_view(), name='endorse_api'),
    re_path(r'^api/v1/shared', Shared.as_view(), name='shared_api'),
    re_path(r'^api/v1/accept', Accept.as_view(), name='accept_api'),
    re_path(r'^api/v1/notification', Notification.as_view(),
            name='notification_api'),
    re_path(r'.*', page.index, name='home'),
]
