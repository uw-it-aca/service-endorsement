from .base_settings import *

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'endorsement',
    'userservice',
    'django_client_logger',
    'supporttools',
    'compressor'
]

MIDDLEWARE += [
    'userservice.user.UserServiceMiddleware'
]

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'supporttools.context_processors.supportools_globals',
    'endorsement.context_processors.is_desktop'
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
    ('text/x-sass', 'pyscss {infile} > {outfile}'),
    ('text/x-scss', 'pyscss {infile} > {outfile}'),
)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter'
]
COMPRESS_JS_FILTERS = [
    'compressor.filters.jsmin.JSMinFilter',
]

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
STATIC_ROOT = "/static"
COMPRESS_ROOT = "/static"

if os.getenv("ENV") == "localdev":
    DEBUG = True

PROVISION_ADMIN_GROUP = ""
