from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required


urlpatterns = patterns(
    'endorsement.views',
    url(r'^logger/(?P<interaction_type>\w+)$', 'logger.log_interaction'
        ),
    url(r'^logout', 'page.logout', name="myuw_logout"
        ),
    url(r'.*', 'page.index', name="home"),
)
