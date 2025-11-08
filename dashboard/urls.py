from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),

    # Packages
    path('packages/', views.packages_list, name='packages'),
    path('packages/create/', views.package_create, name='package_create'),
    path('packages/<int:pk>/edit/', views.package_edit, name='package_edit'),

    # Subscriptions
    path('subscriptions/', views.subscriptions_list, name='subscriptions'),
    path('subscriptions/<int:pk>/', views.subscription_detail, name='subscription_detail'),
    path('subscriptions/<int:pk>/edit/', views.subscription_edit, name='subscription_edit'),

    # Messages
    path('messages/', views.messages_list, name='messages'),

    # Users
    path('users/', views.users_list, name='users'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),

    # Scopes
    path('scopes/', views.scopes_list, name='scopes'),
    path('scopes/create/', views.scope_create, name='scope_create'),
    path('scopes/<int:pk>/edit/', views.scope_edit, name='scope_edit'),

    # Settings & Info
    path('settings/', views.settings_view, name='settings'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),

    # API
    path('api/analytics/', views.analytics_api, name='analytics_api'),
]
