import re
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from endorsement.views.logger import log_interaction
from endorsement.views import page


urlpatterns = [
    url(r'^logger/(?P<interaction_type>\w+)$', log_interaction, name='logger'),
    url(r'^logout', page.logout, name='logout'),
    url(r'.*', page.index, name='home'),
]
