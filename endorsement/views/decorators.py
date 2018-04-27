from django.shortcuts import render
from endorsement.dao.gws import is_in_admin_group


def admin_required(group_key):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not is_in_admin_group(group_key):
                return render(request, 'no_access.html', {})

            return func(request, *args, **kwargs)
        return wrapper
    return decorator
