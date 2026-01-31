from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings
from django.utils import timezone
from datetime import timedelta


class CustomRefreshToken(RefreshToken):
    """
    Custom JWT token that includes user scopes and permissions
    """

    @classmethod
    def for_user(cls, user):
        """
        Create a token with custom claims including user scopes and permissions
        """
        token = super().for_user(user)

        # Add custom claims
        token['user_id'] = user.id
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        token['scopes'] = user.get_user_scopes()
        token['permissions'] = user.get_user_permissions()
        token['has_active_trial'] = user.has_active_trial
        token['trial_remaining_days'] = user.trial_remaining_days
        token['is_verified'] = user.is_phone_verified
        token['exp'] = timezone.now() + timedelta(days=7)  # Extended expiry

        return token


def get_user_token(user):
    """
    Generate JWT token with user scopes and permissions
    """
    refresh = CustomRefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'scopes': user.get_user_scopes(),
            'permissions': user.get_user_permissions(),
            'has_active_trial': user.has_active_trial,
            'trial_remaining_days': user.trial_remaining_days,
            'is_verified': user.is_phone_verified,
        }
    }
