from .base_settings import *

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += [
    'templatetag_handlebars',
    'authz_group',
    'django_mobileesp',
    'endorsement',
    'userservice',
    'django_client_logger',
    'supporttools',
    'compressor'
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

from django_mobileesp.detector import mobileesp_agent as agent

DETECT_USER_AGENTS = {
    'is_tablet': agent.detectTierTablet,
    'is_mobile': agent.detectMobileQuick,
}

MIDDLEWARE_CLASSES = MIDDLEWARE + [
    'django_mobileesp.middleware.UserAgentDetectionMiddleware',
]

if os.getenv("ENV") == "localdev":
    DEBUG = True

PROVISION_ADMIN_GROUP = ""
