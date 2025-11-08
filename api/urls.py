from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ScopeViewSet, PackageViewSet, SubscriptionViewSet,
    UserGoalViewSet, AIMessageViewSet,
    PaymentWebhookView, PaymentVerificationView,
    DashboardStatsView
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'scopes', ScopeViewSet, basename='scope')
router.register(r'packages', PackageViewSet, basename='package')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'goals', UserGoalViewSet, basename='goal')
router.register(r'messages', AIMessageViewSet, basename='message')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Payment endpoints
    path('payments/webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('payments/verify/<str:charge_id>/', PaymentVerificationView.as_view(), name='payment-verify'),

    # Dashboard
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
