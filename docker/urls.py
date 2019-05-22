from django.conf.urls import  include, url


urlpatterns = [
    url(r'^', include('endorsement.urls')),
    url(r'^support', include('userservice.urls')),
    url(r'^logging/', include('django_client_logger.urls')),
]
