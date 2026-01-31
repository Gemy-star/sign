"""
Custom decorators for dashboard access control
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from functools import wraps


def is_admin_or_staff(user):
    """
    Check if user is staff (superuser) or has admin role in CustomUser
    """
    return user.is_staff or (hasattr(user, 'role') and user.role == 'admin')


def admin_required(view_func=None, redirect_field_name='next', login_url='login'):
    """
    Decorator for views that checks that the user is logged in and is either
    a staff member (superuser) or has admin role in CustomUser, redirecting
    to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        is_admin_or_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


# For backward compatibility, we can also create an alias
dashboard_admin_required = admin_required
