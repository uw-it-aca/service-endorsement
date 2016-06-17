from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^support', include('userservice.urls')),
    url(r'^logging/', include('django_client_logger.urls')),
    url(r'^', include('endorsement.urls')),
]
