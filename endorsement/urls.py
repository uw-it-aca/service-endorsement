import re
from django.conf.urls import url
from endorsement.views.logger import log_interaction
from endorsement.views import page
from endorsement.views.api.validate import Validate
from endorsement.views.api.endorse import Endorse


urlpatterns = [
    url(r'^logger/(?P<interaction_type>\w+)$', log_interaction, name='logger'),
    url(r'^logout', page.logout, name='logout'),
    url(r'^api/v1/validate', Validate.as_view(), name='validate_api'),
    url(r'^api/v1/endorse', Endorse.as_view(), name='endorse_api'),
    url(r'.*', page.index, name='home'),
]
