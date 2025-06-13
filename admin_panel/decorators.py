from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    if user.is_authenticated and user.is_staff:
        return True
    raise PermissionDenied