from .base_urls import *
from django.urls import include, re_path


urlpatterns += [
    re_path(r'^support', include('userservice.urls')),
    re_path(r'^logging/', include('django_client_logger.urls')),
    re_path(r'^', include('django_prometheus.urls')),
    re_path(r'^', include('endorsement.urls')),
]
