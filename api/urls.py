from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ScopeViewSet, PackageViewSet, SubscriptionViewSet,
    UserGoalViewSet, AIMessageViewSet,
    PaymentWebhookView, PaymentVerificationView,
    DashboardStatsView, UserRegistrationView, UserLoginView,
    UserProfileView, AdminUserManagementView, TrialManagementView,
    ScopeManagementView, FeatureTestView
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'scopes', ScopeViewSet, basename='scope')
router.register(r'packages', PackageViewSet, basename='package')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'goals', UserGoalViewSet, basename='goal')
router.register(r'messages', AIMessageViewSet, basename='message')

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Admin endpoints
    path('admin/users/', AdminUserManagementView.as_view(), name='admin-users'),
    path('admin/trials/', TrialManagementView.as_view(), name='admin-trials'),

    # Scope management endpoints
    path('scopes/', ScopeManagementView.as_view(), name='scope-management'),
    path('features/test/', FeatureTestView.as_view(), name='feature-test'),

    # Router URLs
    path('', include(router.urls)),

    # Payment endpoints
    path('payments/webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('payments/verify/<str:charge_id>/', PaymentVerificationView.as_view(), name='payment-verify'),

    # Dashboard
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
