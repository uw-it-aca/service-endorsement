from .base_settings import *

ENDORSEMENT_SERVICES = [s.strip() for s in os.getenv(
    'ENDORSEMENT_SERVICES', '*').split(',')]

ALLOWED_HOSTS = ['*']

CACHES = {
    'default' : {
        'BACKEND' : 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION' : 'prt_sessions'
    }
}

if os.getenv('AUTH', 'NONE') == 'SAML_MOCK':
    MOCK_SAML_ATTRIBUTES = {
        'uwnetid': ['jstaff'],
        'affiliations': ['employee', 'member'],
        'eppn': ['jstaff@washington.edu'],
        'scopedAffiliations': ['employee@washington.edu', 'member@washington.edu'],
        'isMemberOf': ['u_test_group', 'u_test_another_group',
                       'u_acadev_provision_support'],
    }

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication'
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
}

if not os.getenv("ENV") == "localdev":
    RESTCLIENTS_DAO_CACHE_CLASS = 'endorsement.cache.RestClientsCache'
    if os.getenv("ENV") == "prod":
        APP_SERVER_BASE = 'https://provision.uw.edu'

INSTALLED_APPS += [
    'webpack_loader',
    'endorsement',
    'userservice',
    'django_client_logger',
    'supporttools',
    'rest_framework.authtoken',
]

MIDDLEWARE += ['userservice.user.UserServiceMiddleware']

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
else:
    RESTCLIENTS_PRT_HOST = 'https://staff.washington.edu'
    RESTCLIENTS_PRT_DAO_CLASS = 'Live'

PROVISION_ADMIN_GROUP = 'u_acadev_provision_support'

USERSERVICE_VALIDATION_MODULE = "endorsement.userservice_validation.validate"
USERSERVICE_OVERRIDE_AUTH_MODULE = "endorsement.userservice_validation.can_override_user"
USERSERVICE_ADMIN_GROUP='u_acadev_provision_support'
RESTCLIENTS_ADMIN_GROUP='u_acadev_provision_support'
AUTHZ_GROUP_BACKEND = 'authz_group.authz_implementation.uw_group_service.UWGroupService'

RESTCLIENTS_DEFAULT_TIMEOUT = 3

SUPPORTTOOLS_PARENT_APP = "PRT"
SUPPORTTOOLS_PARENT_APP_URL = "/"

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 587
EMAIL_SSL_CERTFILE = os.getenv('CERT_PATH', '')
EMAIL_SSL_KEYFILE = os.getenv('KEY_PATH', '')
EMAIL_USE_TLS=True
if os.getenv("SAFE_EMAIL_RECIPIENT", None):
    SAFE_EMAIL_RECIPIENT = os.getenv("SAFE_EMAIL_RECIPIENT")
    EMAIL_BACKEND = 'saferecipient.EmailBackend'
    EMAIL_NOREPLY_ADDRESS = 'Service Endorsement <endorsement-noreply@uw.edu>'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_REPLY_ADDRESS = 'UW-IT <help@uw.edu>'
