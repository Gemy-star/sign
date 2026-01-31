"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from dashboard import views as dashboard_views

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Personal Development API",
        default_version='v1',
        description="""
        ## Welcome to the Personal Development API

        This API provides a comprehensive subscription-based platform for personal development
        and growth with role-based access control and scope management.

        ### Key Features:
        - **User Management**: Normal users, subscribers, and admin roles
        - **Scope-Based Access**: Dynamic permissions based on user role and subscription
        - **Trial System**: Free trials for new users with automatic upgrade to subscribers
        - **Personal Development Scopes**: 8 life domains including mental, physical, career, financial, etc.
        - **Custom Goals**: Set and track personal development goals
        - **AI-Generated Messages**: Personalized content powered by ChatGPT
        - **Payment Integration**: Secure payments via Tap Payment Gateway

        ### Authentication & Authorization:
        The API uses JWT (JSON Web Token) authentication with embedded scopes and permissions.

        1. **Register**: `POST /api/auth/register/`
        2. **Login**: `POST /api/auth/login/` - Returns JWT with user scopes
        3. **Include Token**: `Authorization: Bearer <your_jwt_token>`

        ### User Roles & Scopes:
        - **Normal Users**: Basic access, can start trials
        - **Subscribers**: Full access to subscribed features
        - **Admins**: Full administrative access including user management

        ### API Endpoints:
        - **Authentication**: `/api/auth/` - Registration, login, profile management
        - **User Management**: `/api/admin/` - Admin-only user and trial management
        - **Scopes & Features**: `/api/scopes/` - Scope validation and feature access
        - **Subscriptions**: `/api/subscriptions/` - Package management and payments
        - **Goals**: `/api/goals/` - Personal goal tracking
        - **Messages**: `/api/messages/` - AI-generated guidance
        - **Dashboard**: `/api/dashboard/stats/` - User statistics and insights

        ### Scope-Based Access Control:
        Each JWT token includes user scopes and permissions. Endpoints are protected based on:
        - User role (admin, subscriber, normal)
        - Active trial status
        - Subscription level and features
        - Package-specific permissions (custom goals, priority support, etc.)
        """,
        terms_of_service="https://example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/', include('api.urls')),
    ],
)

urlpatterns = [
    # Root URL - Redirect to dashboard
    path('', dashboard_views.home_redirect, name='home'),

    # Authentication
    path('login/', dashboard_views.login_view, name='login'),
    path('logout/', dashboard_views.logout_view, name='logout'),

    # Admin
    path('admin/', admin.site.urls),

    # Dashboard
    path('dashboard/', include('dashboard.urls')),

    # API endpoints
    path('api/', include('api.urls')),

    # JWT Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Swagger Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api-docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
]

# Serve static and media files in development
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Silk profiler (only in development)
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]
