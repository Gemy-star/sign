from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('packages/', views.packages_list, name='packages'),
    path('subscriptions/', views.subscriptions_list, name='subscriptions'),
    path('subscriptions/<int:pk>/', views.subscription_detail, name='subscription_detail'),
    path('messages/', views.messages_list, name='messages'),
    path('users/', views.users_list, name='users'),
    path('scopes/', views.scopes_list, name='scopes'),
    path('api/analytics/', views.analytics_api, name='analytics_api'),
]
