from .base_settings import *

ALLOWED_HOSTS = ['*']

CACHES = {
    'default' : {
        'BACKEND' : 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION' : 'prt_sessions'
    }
}

if os.getenv("ENV") == "prod":
    INSTALLED_APPS += ['rc_django',]
    RESTCLIENTS_DAO_CACHE_CLASS='endorsement.cache.ProvisionCache'

INSTALLED_APPS += [
    'django_prometheus',
    'webpack_loader',
    'endorsement',
    'userservice',
    'django_client_logger',
    'supporttools'
]

MIDDLEWARE = ['django_prometheus.middleware.PrometheusBeforeMiddleware'] +\
             MIDDLEWARE +\
             ['userservice.user.UserServiceMiddleware',
              'django_prometheus.middleware.PrometheusAfterMiddleware']

if not os.getenv("ENV") == "localdev":
    DATABASES['default']['ENGINE'] = 'django_prometheus.db.backends.postgresql'


TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'supporttools.context_processors.supportools_globals',
    'endorsement.context_processors.is_desktop'
]

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'endorsement/bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'endorsement', 'static', 'webpack-stats.json'),
    }
}

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

if os.getenv("ENV") == "localdev":
    DEBUG = True

PROVISION_ADMIN_GROUP = 'u_acadev_provision_support'

USERSERVICE_VALIDATION_MODULE = "endorsement.userservice_validation.validate"
USERSERVICE_OVERRIDE_AUTH_MODULE = "endorsement.userservice_validation.can_override_user"
USERSERVICE_ADMIN_GROUP='u_acadev_provision_support'
RESTCLIENTS_ADMIN_GROUP='u_acadev_provision_support'
AUTHZ_GROUP_BACKEND = 'authz_group.authz_implementation.uw_group_service.UWGroupService'

RESTCLIENTS_DEFAULT_TIMEOUT = 3

RESTCLIENTS_PRT_DAO_CLASS = 'Live'
RESTCLIENTS_PRT_HOST = 'https://staff.washington.edu'

SUPPORTTOOLS_PARENT_APP = "PRT"
SUPPORTTOOLS_PARENT_APP_URL = "/"
