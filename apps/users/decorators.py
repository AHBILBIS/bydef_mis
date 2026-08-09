from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(*allowed_roles):
    """
    Decorator enforcing view-level RBAC. Returns HTTP 403 Forbidden
    if the logged-in user does not possess an allowed role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator
