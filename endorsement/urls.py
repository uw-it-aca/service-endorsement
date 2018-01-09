import re
from django.conf.urls import url
from endorsement.views.logger import log_interaction
from endorsement.views import page
from endorsement.views.endorsee_search import endorsee_search
from endorsement.views.api.validate import Validate
from endorsement.views.api.endorse import Endorse
from endorsement.views.api.endorsed import Endorsed
from endorsement.views.api.endorsee import Endorsee


urlpatterns = [
    url(r'^logger/(?P<interaction_type>\w+)$', log_interaction, name='logger'),
    url(r'^logout', page.logout, name='logout'),
    url(r'^admin/endorsee', endorsee_search, name='endorsee_search'),
    url(r'^api/v1/validate', Validate.as_view(), name='validate_api'),
    url(r'^api/v1/endorsee/(?P<endorsee>.+)$',
        Endorsee.as_view(), name='endorsee_api'),
    url(r'^api/v1/endorsed', Endorsed.as_view(), name='endorsed_api'),
    url(r'^api/v1/endorse', Endorse.as_view(), name='endorse_api'),
    url(r'.*', page.index, name='home'),
]
