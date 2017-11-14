from django.conf import settings


def has_google_analytics(request):

    ga_key = getattr(settings, 'GOOGLE_ANALYTICS_KEY', False)
    return {
        'GOOGLE_ANALYTICS_KEY': ga_key,
        'has_google_analytics': ga_key
    }


def is_desktop(request):

    desktopapp = not request.is_mobile and not request.is_tablet
    return {
        'is_desktop': desktopapp
    }
