from rest_framework import permissions
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


class ScopePermission(permissions.BasePermission):
    """
    Custom permission class that checks if user has required scope
    """

    def __init__(self, required_scopes=None):
        self.required_scopes = required_scopes or []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Get user scopes from token or user model
        user_scopes = self.get_user_scopes(request)

        # Check if user has all required scopes
        return all(scope in user_scopes for scope in self.required_scopes)

    def get_user_scopes(self, request):
        """Get user scopes from JWT token or user model"""
        # Try to get from JWT token first
        auth = getattr(request, 'auth', None)
        if auth and hasattr(auth, 'payload'):
            return auth.payload.get('scopes', [])

        # Fallback to user model
        return request.user.get_user_scopes()


def require_scope(*scopes):
    """
    Decorator to require specific scopes for API endpoints
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            user_scopes = request.user.get_user_scopes()

            # Check if user has all required scopes
            if not all(scope in user_scopes for scope in scopes):
                return Response(
                    {
                        'error': 'Insufficient permissions',
                        'required_scopes': list(scopes),
                        'user_scopes': user_scopes
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(view, request, *args, **kwargs)
        return wrapper
    return decorator


def require_permission(*permissions):
    """
    Decorator to require specific permissions for API endpoints
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            user_permissions = request.user.get_user_permissions()

            # Check if user has all required permissions
            if not all(perm in user_permissions for perm in permissions):
                return Response(
                    {
                        'error': 'Insufficient permissions',
                        'required_permissions': list(permissions),
                        'user_permissions': user_permissions
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(view, request, *args, **kwargs)
        return wrapper
    return decorator


def require_feature(feature):
    """
    Decorator to require specific feature access
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(view, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not request.user.can_access_feature(feature):
                return Response(
                    {
                        'error': f'Feature "{feature}" not available',
                        'message': 'This feature requires an active subscription or trial',
                        'user_role': request.user.role,
                        'has_active_trial': request.user.has_active_trial,
                        'trial_remaining_days': request.user.trial_remaining_days
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(view, request, *args, **kwargs)
        return wrapper
    return decorator


class AdminScopePermission(ScopePermission):
    """Permission class requiring admin scope"""

    def __init__(self):
        super().__init__(required_scopes=['admin'])


class SubscriberScopePermission(ScopePermission):
    """Permission class requiring subscriber scope"""

    def __init__(self):
        super().__init__(required_scopes=['subscriber'])


class TrialScopePermission(ScopePermission):
    """Permission class requiring trial scope"""

    def __init__(self):
        super().__init__(required_scopes=['trial'])


class CustomGoalsPermission(ScopePermission):
    """Permission class requiring custom goals scope"""

    def __init__(self):
        super().__init__(required_scopes=['custom_goals'])


class PrioritySupportPermission(ScopePermission):
    """Permission class requiring priority support scope"""

    def __init__(self):
        super().__init__(required_scopes=['priority_support'])


def check_subscription_or_trial(view_func):
    """
    Decorator to check if user has active subscription or trial
    """
    @wraps(view_func)
    def wrapper(view, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user has active trial or subscription
        has_access = (
            request.user.has_active_trial or
            request.user.subscriptions.filter(
                status='active',
                end_date__gt=timezone.now()
            ).exists()
        )

        if not has_access:
            return Response(
                {
                    'error': 'Active subscription or trial required',
                    'message': 'Please subscribe to access this feature',
                    'trial_available': not request.user.has_used_trial,
                    'user_role': request.user.role
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return view_func(view, request, *args, **kwargs)
    return wrapper
