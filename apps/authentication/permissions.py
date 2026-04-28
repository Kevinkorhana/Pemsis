from functools import wraps
from ninja.errors import HttpError

def has_role(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.auth.profile.role not in roles:
                raise HttpError(403, "Anda tidak memiliki izin untuk akses ini.")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

is_admin = has_role(['admin'])
is_instructor = has_role(['instructor', 'admin'])
is_student = has_role(['student', 'admin'])