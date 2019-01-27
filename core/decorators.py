from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

def user_executor(function):
    def wrap(request, *args, **kwargs):
        if request.user.profile.group == 'EX' or request.user.is_superuser :
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    
    return wrap

def user_validator(function):
    def wrap(request, *args, **kwargs):
        if request.user.profile.group == 'VD' or request.user.is_superuser :
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    
    return wrap