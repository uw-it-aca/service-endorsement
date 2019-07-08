from .base_settings import *

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'webpack_loader',
    'endorsement',
    'userservice',
    'django_client_logger',
    'supporttools'
]

MIDDLEWARE += [
    'userservice.user.UserServiceMiddleware'
]

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
