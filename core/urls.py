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
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Motivational Messages API",
        default_version='v1',
        description="""
        ## Welcome to the Motivational Messages API

        This API provides a comprehensive subscription-based platform for personal development
        and motivation. Users can subscribe to packages, select their focus areas (scopes),
        set personal goals, and receive AI-generated motivational messages.

        ### Key Features:
        - **Subscription Management**: Multiple package tiers with different features
        - **Personal Development Scopes**: 8 life domains including mental, physical, career, financial, etc.
        - **Custom Goals**: Set and track personal development goals
        - **AI-Generated Messages**: Personalized motivational content powered by ChatGPT
        - **Payment Integration**: Secure payments via Tap Payment Gateway

        ### Authentication:
        This API uses JWT (JSON Web Token) authentication. Obtain your token from `/api/auth/token/`
        and include it in the Authorization header: `Bearer <your_token>`
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@motivationalapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
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
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='api-root'),
]

# Django Silk profiler (only in development)
if settings.DEBUG:
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]
