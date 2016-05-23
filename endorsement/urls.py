from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from myuw.views.logger import log_interaction
from myuw.views.page import index


urlpatterns = patterns(
    'endorsement.views',
    url(r'^logger/(?P<interaction_type>\w+)$', 'logger.log_interaction'
        ),
    url(r'^logout', 'page.logout', name="myuw_logout"
        ),
    url(r'.*', 'page.index', name="myuw_home"),
)
