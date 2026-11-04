from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from .models import StaffProfile, StaffActivityLog


def get_client_ip(request):
    """Safely retrieve the real IP address behind Coolify / Traefik proxy"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def staff_workspace_required(allowed_roles=None):
    """
    Strict security guard:
    1. Must be logged in
    2. Must have is_staff = True
    3. Must have an active StaffProfile (kill-switch check)
    4. Optional: role check ('moderator', 'verification_officer', 'customer_support')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"/admin/login/?next={request.path}")

            # Superusers (CEO) always bypass checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if not request.user.is_staff:
                raise PermissionDenied("Access Denied: You do not have staff credentials.")

            # Check for linked profile and CEO kill-switch
            try:
                profile = request.user.staff_profile
            except StaffProfile.DoesNotExist:
                raise PermissionDenied("Access Denied: No staff profile profile assigned to your account.")

            if not profile.is_active:
                raise PermissionDenied("Access Denied: Your staff account has been deactivated by administration.")

            if allowed_roles and profile.role not in allowed_roles:
                raise PermissionDenied(f"Access Denied: Your role ({profile.get_role_display()}) cannot access this section.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def log_staff_action(staff_user, action, target_id, details, request):
    """Helper to log immutable staff actions"""
    StaffActivityLog.objects.create(
        staff=staff_user,
        action=action,
        target_object_id=str(target_id),
        details=details,
        ip_address=get_client_ip(request)
    )