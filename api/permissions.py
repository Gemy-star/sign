from rest_framework import permissions
from django.utils import timezone
from .models import Subscription


class IsNormalUser(permissions.BasePermission):
    """
    Permission to check if user is normal
    """
    message = "Normal user access required."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_normal
        )


class IsAdminUser(permissions.BasePermission):
    """
    Permission to check if user is admin
    """
    message = "Admin access required."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_admin
        )


class IsSubscriberUser(permissions.BasePermission):
    """
    Permission to check if user is subscriber
    """
    message = "Subscriber access required."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_subscriber
        )


class HasActiveTrialOrSubscription(permissions.BasePermission):
    """
    Permission to check if user has active trial or subscription
    """
    message = "You need an active trial or subscription to access this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check for active trial
        if request.user.has_active_trial:
            return True

        # Check for active subscription
        has_active = Subscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).exists()

        return has_active


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class HasActiveSubscription(permissions.BasePermission):
    """
    Permission to check if user has an active subscription
    """
    message = "You need an active subscription to access this resource."

    def has_permission(self, request, view):
        # Allow if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Check for active subscription
        has_active = Subscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).exists()

        return has_active


class HasCustomGoalsEnabled(permissions.BasePermission):
    """
    Permission to check if user's subscription allows custom goals
    """
    message = "Your subscription package does not include custom goals feature."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Get active subscription
        active_sub = Subscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).first()

        if not active_sub:
            return False

        return active_sub.package.custom_goals_enabled
