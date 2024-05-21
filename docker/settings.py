# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from .base_settings import *

ENDORSEMENT_SERVICES = [s.strip() for s in os.getenv(
    'ENDORSEMENT_SERVICES', '*').split(',')]

ENDORSEMENT_PROVISIONING = [s.strip() for s in os.getenv(
    'ENDORSEMENT_PROVISIONING', '*').split(',')]

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
                       'u_acadev_provision_support', 'u_acadev_provision_admin'],
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
    else:
        PROVISIONER_ACCESS_TEST = 'endorsement.provisioner_validation.allowed_test_endorsers'

INSTALLED_APPS += [
    'django.contrib.humanize',
    'webpack_loader',
    'endorsement',
    'userservice',
    'django_client_logger',
    'supporttools',
    'persistent_message',
    'rest_framework.authtoken',
]

MIDDLEWARE += ['userservice.user.UserServiceMiddleware']

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'supporttools.context_processors.supportools_globals',
    'endorsement.context_processors.supporttools_globals',
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
    RESTCLIENTS_MSCA_HOST = 'https://pplat-apimgmt.azure-api.net'
    RESTCLIENTS_MSCA_DAO_CLASS = 'Live'
    RESTCLIENTS_MSCA_TIMEOUT = os.getenv(
        "MSCA_TIMEOUT", RESTCLIENTS_DEFAULT_TIMEOUT)
    RESTCLIENTS_MSCA_SUBSCRIPTION_KEY = os.getenv('MSCA_SUBSCRIPTION_KEY', '')

    RESTCLIENTS_ITBILL_DAO_CLASS = 'Live'
    RESTCLIENTS_ITBILL_HOST=os.getenv('ITBILL_HOST')
    RESTCLIENTS_ITBILL_BASIC_AUTH=os.getenv('ITBILL_BASIC_AUTH')

ITBILL_SHARED_DRIVE_SUBSIDIZED_QUOTA=100
ITBILL_SHARED_DRIVE_NAME_FORMAT="GSD_{}"
ITBILL_SHARED_DRIVE_PRODUCT_SYS_ID=os.getenv(
    'ITBILL_SHARED_DRIVE_PRODUCT_SYS_ID')
ITBILL_FORM_URL_BASE=os.getenv('ITBILL_HOST')
ITBILL_FORM_URL_BASE_ID=os.getenv('ITBILL_FORM_URL_BASE_ID')
ITBILL_FORM_URL_SYS_ID=os.getenv('ITBILL_FORM_URL_SYS_ID')

RESTCLIENTS_MSCA_OAUTH_TOKEN_URL = os.getenv("MSCA_OAUTH_TOKEN_URL")
RESTCLIENTS_MSCA_REPORT_SCOPE = os.getenv("MSCA_REPORT_SCOPE")
RESTCLIENTS_MSCA_CLIENT_ID = os.getenv("MSCA_CLIENT_ID")
RESTCLIENTS_MSCA_CLIENT_SECRET = os.getenv("MSCA_CLIENT_SECRET")


PROVISION_ADMIN_GROUP = 'u_acadev_provision_admin'
PROVISION_SUPPORT_GROUP = 'u_acadev_provision_support'
PROVISION_TEST_GROUP = 'u_acadev_provision_test'

USERSERVICE_VALIDATION_MODULE = "endorsement.userservice_validation.validate"
USERSERVICE_OVERRIDE_AUTH_MODULE = "endorsement.userservice_validation.can_override_user"
PERSISTENT_MESSAGE_AUTH_MODULE = 'endorsement.views.support.can_manage_persistent_messages'
USERSERVICE_ADMIN_GROUP='u_acadev_provision_admin'
RESTCLIENTS_ADMIN_GROUP='u_acadev_provision_admin'
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
    SAFE_EMAIL_SAFELIST = [s.strip() for s in os.getenv(
        'SAFE_EMAIL_SAFELIST', '').split(',')]
    EMAIL_BACKEND = 'saferecipient.EmailBackend'
    EMAIL_NOREPLY_ADDRESS = 'Service Endorsement <endorsement-noreply@uw.edu>'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_REPLY_ADDRESS = 'UW-IT <help@uw.edu>'
