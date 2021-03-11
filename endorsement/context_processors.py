"""
"""


def is_desktop(request):
    desktopapp = (not getattr(request, 'is_mobile', False) and
                  not getattr(request, 'is_tablet', False))
    return {
        'is_desktop': desktopapp
    }
