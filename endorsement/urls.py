# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.urls import re_path
from userservice.views import SupportView
from endorsement.views import page
from endorsement.views.accept import accept
from endorsement.views.support.endorser_search import EndorserSearch
from endorsement.views.support.endorsee_search import EndorseeSearch
from endorsement.views.support.member_search import MemberSearch
from endorsement.views.support.notifications import EndorseeNotifications
from endorsement.views.support.shared_proxy import SharedProxy
from endorsement.views.support.persistent_messages import PersistentMessages
from endorsement.views.support.endorsement_statistics import (
    EndorsementStatistics)
from endorsement.views.api.validate import Validate
from endorsement.views.api.endorse import Endorse
from endorsement.views.api.accept import Accept
from endorsement.views.api.endorsee import Endorsee
from endorsement.views.api.endorser import Endorser
from endorsement.views.api.endorsed import Endorsed
from endorsement.views.api.endorsements import Endorsements
from endorsement.views.api.shared import Shared
from endorsement.views.api.shared_owner import SharedOwner
from endorsement.views.api.shared_proxy import SharedProxyEndorse
from endorsement.views.api.member import Member
from endorsement.views.api.statistics import Statistics
from endorsement.views.api.office.access import (
    Access as OfficeAccess, AccessRights as OfficeAccessRights)
from endorsement.views.api.office.resolve import ResolveRightsConflict
from endorsement.views.api.office.validate import Validate as OfficeValidate
from endorsement.views.api.google.shared_drive import SharedDrive
from endorsement.views.api.google.itbill import SharedDriveITBillURL
from endorsement.views.api.notification import Notification


urlpatterns = [
    re_path(r'^logout', page.logout, name='logout'),
    re_path(r'^accept/(?P<accept_id>[A-Za-z0-9]{32})$',
            accept, name='accept_view'),
    re_path(r'^support/?$', EndorsementStatistics.as_view(),
            name='endorsement_statistics'),
    re_path(r'^support/provisionee/?', EndorseeSearch.as_view(),
            name='endorsee_search'),
    re_path(r'^support/provisioner/?', EndorserSearch.as_view(),
            name='endorser_search'),
    re_path(r'^support/member/?', MemberSearch.as_view(),
            name='member_search'),
    re_path(r'^support/notifications/?', EndorseeNotifications.as_view(),
            name='endorsee_notifications'),
    re_path(r'^support/override/?', SupportView.as_view(),
            name='userservice_override'),
    re_path(r'^support/persistent_messages/?', PersistentMessages.as_view(),
            name='manage_persistent_messages_init'),
    re_path(r'^support/shared_proxy/?', SharedProxy.as_view(),
            name='manage_shared_proxy'),
    re_path(r'^api/v1/validate', Validate.as_view(), name='validate_api'),
    re_path(r'^api/v1/endorsee/(?P<endorsee>.+)$',
            Endorsee.as_view(), name='endorsee_api'),
    re_path(r'^api/v1/endorser/(?P<endorser>.+)$',
            Endorser.as_view(), name='endorser_api'),
    re_path(r'^api/v1/endorsements/?$',
            Endorsements.as_view(), name='endorsements_api'),
    re_path(r'^api/v1/stats/(?P<type>.+)$',
            Statistics.as_view(), name='statistics_api'),
    re_path(r'^api/v1/endorsed', Endorsed.as_view(), name='endorsed_api'),
    re_path(r'^api/v1/endorse', Endorse.as_view(), name='endorse_api'),
    re_path(r'^api/v1/shared_owner/(?P<shared_netid>.*)$',
            SharedOwner.as_view(), name='shared_owner_api'),
    re_path(r'^api/v1/shared_proxy/?$',
            SharedProxyEndorse.as_view(), name='shared_proxy_endorse_api'),
    re_path(r'^api/v1/shared', Shared.as_view(), name='shared_api'),
    re_path(r'^api/v1/accept', Accept.as_view(), name='accept_api'),
    re_path(r'^api/v1/member/(?P<member>.+)$',
            Member.as_view(), name='member_api'),
    re_path(r'^api/v1/notification', Notification.as_view(),
            name='notification_api'),
    re_path(r'^office/v1/access/rights',
            OfficeAccessRights.as_view(), name='access_rights_api'),
    re_path(r'^office/v1/access/resolve',
            ResolveRightsConflict.as_view(), name='access_right_resolve_api'),
    re_path(r'^office/v1/access', OfficeAccess.as_view(), name='access_api'),
    re_path(r'^office/v1/validate', OfficeValidate.as_view(),
            name='office_validate_api'),
    re_path(r'^google/v1/shared_drive/(?P<drive_id>[\S^/]+)/itbill_url',
            SharedDriveITBillURL.as_view(), name='shared_drive_itbill_url'),
    re_path(r'^google/v1/shared_drive/(?P<drive_id>[^\s\/]+)?',
            SharedDrive.as_view(), name='shared_drive_api'),
    re_path(r'.*', page.index, name='home'),
]
