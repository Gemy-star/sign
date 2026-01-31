from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
import os
from api.models import (
    Scope, Package, Subscription, UserGoal,
    AIMessage, PaymentTransaction, CustomUser
)
from django.contrib.auth.models import User
from .decorators import admin_required


def home_redirect(request):
    """Redirect root URL to dashboard or login"""
    if request.user.is_authenticated and (request.user.is_staff or
                                         (hasattr(request.user, 'role') and request.user.role == 'admin')):
        return redirect('dashboard:home')
    return redirect('login')


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        if request.user.is_staff or (hasattr(request.user, 'role') and request.user.role == 'admin'):
            return redirect('dashboard:home')
        else:
            logout(request)
            messages.warning(request, 'يجب أن تكون مديرًا للوصول إلى لوحة التحكم')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Try to authenticate with username first, then email
        user = None
        if username:
            # First try as username (for backward compatibility)
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                # Try to find user by username
                user_obj = User.objects.get(username=username)
                user = authenticate(request, username=user_obj.email, password=password)
            except User.DoesNotExist:
                # If not found by username, try as email
                user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user is superuser (is_staff) or has admin role in CustomUser
            is_dashboard_user = user.is_staff or (hasattr(user, 'role') and user.role == 'admin')

            if is_dashboard_user:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard:home')
                return redirect(next_url)
            else:
                messages.error(request, 'يجب أن تكون مديرًا للوصول إلى لوحة التحكم')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')

    return render(request, 'dashboard/login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('login')


def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'dashboard/privacy_policy.html')


def terms_conditions(request):
    """Terms and conditions page"""
    return render(request, 'dashboard/terms_conditions.html')


@admin_required
def settings_view(request):
    """System settings page"""
    from django.conf import settings
    from constance import config

    # Get database engine name
    db_engine = settings.DATABASES['default']['ENGINE'].split('.')[-1]

    # Get cache backend name
    cache_backend = settings.CACHES['default']['BACKEND'].split('.')[-1]

    # Check configurations
    sendgrid_configured = bool(getattr(config, 'SENDGRID_API_KEY', ''))
    openai_configured = bool(os.environ.get('OPENAI_API_KEY', ''))
    tap_configured = bool(os.environ.get('TAP_API_KEY', '')) and bool(os.environ.get('TAP_SECRET_KEY', ''))

    context = {
        # System info
        'site_url': getattr(settings, 'SITE_URL', 'https://sign-sa.net'),
        'support_email': getattr(config, 'SUPPORT_EMAIL', 'support@sign-sa.net'),
        'timezone': settings.TIME_ZONE,

        # Database & Cache
        'db_engine': db_engine.upper(),
        'cache_backend': cache_backend,
        'debug': settings.DEBUG,

        # Email settings
        'email_host': settings.EMAIL_HOST,
        'email_port': settings.EMAIL_PORT,
        'email_use_tls': settings.EMAIL_USE_TLS,
        'email_from_address': getattr(config, 'EMAIL_FROM_ADDRESS', ''),
        'email_from_name': getattr(config, 'EMAIL_FROM_NAME', ''),

        # Configuration status
        'sendgrid_configured': sendgrid_configured,
        'openai_configured': openai_configured,
        'tap_configured': tap_configured,

        # Security settings
        'secure_ssl_redirect': getattr(settings, 'SECURE_SSL_REDIRECT', False),
        'hsts_enabled': getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0,
        'secure_cookies': getattr(settings, 'SESSION_COOKIE_SECURE', False),
        'cors_enabled': 'corsheaders' in settings.INSTALLED_APPS,
    }

    return render(request, 'dashboard/settings.html', context)


@admin_required
def dashboard_home(request):
    """Dashboard home page with statistics and charts"""

    # Calculate statistics using CustomUser
    total_users = CustomUser.objects.count()
    total_subscriptions = Subscription.objects.filter(status='active').count()
    total_revenue = PaymentTransaction.objects.filter(
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_messages = AIMessage.objects.count()

    # User role statistics
    normal_users = CustomUser.objects.filter(role='normal').count()
    subscribers = CustomUser.objects.filter(role='subscriber').count()
    admins = CustomUser.objects.filter(role='admin').count()

    # Calculate percentages
    if total_users > 0:
        normal_users_percent = (normal_users / total_users) * 100
        subscribers_percent = (subscribers / total_users) * 100
        admins_percent = (admins / total_users) * 100
    else:
        normal_users_percent = subscribers_percent = admins_percent = 0

    # Trial statistics
    active_trials = CustomUser.objects.filter(
        trial_expires_at__gt=timezone.now(),
        has_used_trial=True
    ).count()

    used_trials = CustomUser.objects.filter(has_used_trial=True).count()

    # Trials expiring in next 3 days
    expiring_soon = CustomUser.objects.filter(
        trial_expires_at__gt=timezone.now(),
        trial_expires_at__lte=timezone.now() + timedelta(days=3),
        has_used_trial=True
    ).count()

    # Trial to subscription conversion rate
    users_with_trials = CustomUser.objects.filter(has_used_trial=True).count()
    converted_users = CustomUser.objects.filter(
        role='subscriber',
        has_used_trial=True
    ).count()

    if users_with_trials > 0:
        trial_to_sub_conversion = (converted_users / users_with_trials) * 100
    else:
        trial_to_sub_conversion = 0

    # Recent activity
    recent_subscriptions = Subscription.objects.select_related(
        'user', 'package'
    ).order_by('-created_at')[:5]

    recent_messages = AIMessage.objects.select_related(
        'user', 'scope'
    ).order_by('-created_at')[:5]

    # Chart data
    today = timezone.now()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    # Users joined per day
    users_per_day = []
    for day in last_7_days:
        count = CustomUser.objects.filter(
            date_joined__date=day.date()
        ).count()
        users_per_day.append(count)

    # Revenue per day
    revenue_per_day = []
    for day in last_7_days:
        amount = PaymentTransaction.objects.filter(
            created_at__date=day.date(),
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        revenue_per_day.append(float(amount))

    # Subscriptions by package
    packages_data = Package.objects.annotate(
        sub_count=Count('subscriptions', filter=Q(subscriptions__status='active'))
    ).values('name', 'sub_count')

    context = {
        'total_users': total_users,
        'total_subscriptions': total_subscriptions,
        'total_revenue': total_revenue,
        'total_messages': total_messages,

        # User role statistics
        'normal_users': normal_users,
        'subscribers': subscribers,
        'admins': admins,
        'normal_users_percent': normal_users_percent,
        'subscribers_percent': subscribers_percent,
        'admins_percent': admins_percent,

        # Trial statistics
        'active_trials': active_trials,
        'used_trials': used_trials,
        'expiring_soon': expiring_soon,
        'trial_to_sub_conversion': round(trial_to_sub_conversion, 1),

        'recent_subscriptions': recent_subscriptions,
        'recent_messages': recent_messages,
        'users_per_day': users_per_day,
        'revenue_per_day': revenue_per_day,
        'packages_data': list(packages_data),
        'days_labels': [day.strftime('%A') for day in last_7_days],
    }

    return render(request, 'dashboard/home.html', context)


@admin_required
def packages_list(request):
    """List all packages"""
    packages = Package.objects.annotate(
        active_subs=Count('subscriptions', filter=Q(subscriptions__status='active')),
        total_revenue=Sum('subscriptions__amount_paid')
    ).order_by('display_order')

    context = {
        'packages': packages,
    }

    return render(request, 'dashboard/packages.html', context)


@admin_required
def subscriptions_list(request):
    """List all subscriptions"""
    status_filter = request.GET.get('status', '')

    subscriptions = Subscription.objects.select_related(
        'user', 'package'
    ).prefetch_related('selected_scopes')

    if status_filter:
        subscriptions = subscriptions.filter(status=status_filter)

    subscriptions = subscriptions.order_by('-created_at')[:50]

    # Get status counts
    status_counts = Subscription.objects.values('status').annotate(
        count=Count('id')
    )

    # Convert to dict with defaults for all statuses
    status_counts_dict = {
        'active': 0,
        'expired': 0,
        'cancelled': 0,
        'pending': 0,
        'failed': 0,
    }
    for item in status_counts:
        status_counts_dict[item['status']] = item['count']

    context = {
        'subscriptions': subscriptions,
        'status_filter': status_filter,
        'status_counts': status_counts_dict,
    }

    return render(request, 'dashboard/subscriptions.html', context)


@admin_required
def subscription_detail(request, pk):
    """View subscription details"""
    subscription = get_object_or_404(
        Subscription.objects.select_related('user', 'package').prefetch_related('selected_scopes'),
        pk=pk
    )

    # Get related data
    goals = UserGoal.objects.filter(subscription=subscription)
    messages = AIMessage.objects.filter(subscription=subscription).order_by('-created_at')[:10]
    transactions = PaymentTransaction.objects.filter(subscription=subscription).order_by('-created_at')

    context = {
        'subscription': subscription,
        'goals': goals,
        'messages': messages,
        'transactions': transactions,
    }

    return render(request, 'dashboard/subscription_detail.html', context)


@admin_required
def messages_list(request):
    """List all AI messages"""
    message_type = request.GET.get('type', '')

    messages = AIMessage.objects.select_related(
        'user', 'scope', 'goal'
    )

    if message_type:
        messages = messages.filter(message_type=message_type)

    messages = messages.order_by('-created_at')[:50]

    # Get type counts
    type_counts = AIMessage.objects.values('message_type').annotate(
        count=Count('id')
    )

    # Get average rating
    avg_rating = AIMessage.objects.filter(
        user_rating__isnull=False
    ).aggregate(Avg('user_rating'))['user_rating__avg']

    context = {
        'messages': messages,
        'message_type': message_type,
        'type_counts': {item['message_type']: item['count'] for item in type_counts},
        'avg_rating': avg_rating or 0,
    }

    return render(request, 'dashboard/messages.html', context)


@admin_required
def users_list(request):
    """List all users"""
    users = CustomUser.objects.annotate(
        active_subs=Count('subscriptions', filter=Q(subscriptions__status='active')),
        total_messages=Count('ai_messages')
    ).order_by('-date_joined')[:50]

    # Chart data - last 7 days
    today = timezone.now()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    new_users_per_day = []
    active_users_per_day = []

    for day in last_7_days:
        # New users joined on that day
        new_count = CustomUser.objects.filter(date_joined__date=day.date()).count()
        new_users_per_day.append(new_count)

        # Active users (users with active subscriptions or messages on that day)
        active_count = CustomUser.objects.filter(
            Q(subscriptions__status='active', subscriptions__start_date__lte=day) |
            Q(ai_messages__created_at__date=day.date())
        ).distinct().count()
        active_users_per_day.append(active_count)

    context = {
        'users': users,
        'days_labels': [day.strftime('%A') for day in last_7_days],
        'new_users_per_day': new_users_per_day,
        'active_users_per_day': active_users_per_day,
    }

    return render(request, 'dashboard/users.html', context)


@admin_required
def user_detail(request, pk):
    """View user details"""
    user = get_object_or_404(CustomUser, pk=pk)

    # Get user's subscriptions
    subscriptions = Subscription.objects.filter(user=user).select_related('package').order_by('-created_at')

    # Get user's messages
    messages_list = AIMessage.objects.filter(user=user).select_related('scope', 'goal').order_by('-created_at')[:20]

    # Get user's goals
    goals = UserGoal.objects.filter(user=user).order_by('-created_at')

    # Get user's payments
    payments = PaymentTransaction.objects.filter(subscription__user=user).order_by('-created_at')[:10]

    # Calculate stats
    total_spent = PaymentTransaction.objects.filter(
        subscription__user=user,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    active_subscription = subscriptions.filter(status='active').first()

    context = {
        'user_obj': user,  # Renamed to avoid conflict with request.user
        'subscriptions': subscriptions,
        'messages_list': messages_list,
        'goals': goals,
        'payments': payments,
        'total_spent': total_spent,
        'active_subscription': active_subscription,
    }

    return render(request, 'dashboard/user_detail.html', context)


@admin_required
def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        password = request.POST.get('password')
        role = request.POST.get('role', 'normal')  # Add role field
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active', 'on') == 'on'

        try:
            # Check if username exists
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'اسم المستخدم موجود بالفعل')
                return render(request, 'dashboard/user_form.html')

            # Check if email exists
            if email and CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'البريد الإلكتروني موجود بالفعل')
                return render(request, 'dashboard/user_form.html')

            # Create CustomUser
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_staff=is_staff,
                is_active=is_active
            )

            messages.success(request, f'تم إنشاء المستخدم {username} بنجاح')
            return redirect('dashboard:user_detail', pk=user.id)

        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
            return render(request, 'dashboard/user_form.html')

    return render(request, 'dashboard/user_form.html', {'is_edit': False})


@admin_required
def user_edit(request, pk):
    """Edit user details"""
    user = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.role = request.POST.get('role', user.role)  # Add role field
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active', 'on') == 'on'

        # Update password if provided
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)

        try:
            user.save()
            messages.success(request, f'تم تحديث بيانات المستخدم {user.username} بنجاح')
            return redirect('dashboard:user_detail', pk=user.id)
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    context = {
        'user_obj': user,
        'is_edit': True,
    }
    return render(request, 'dashboard/user_form.html', context)


@admin_required
def scopes_list(request):
    """List all scopes"""
    scopes = Scope.objects.annotate(
        subscription_count=Count('subscriptions'),
        message_count=Count('messages')
    ).order_by('category', 'name')

    # Category distribution data
    category_data = Scope.objects.values('category').annotate(
        count=Count('id')
    ).order_by('category')

    categories_labels = [dict(Scope.SCOPE_CATEGORIES).get(item['category'], item['category']) for item in category_data]
    categories_counts = [item['count'] for item in category_data]

    # Usage distribution (based on subscription counts)
    total_scopes = scopes.count()
    if total_scopes > 0:
        # High usage: > 10 subscriptions
        high_usage = scopes.filter(subscription_count__gt=10).count()
        # Medium usage: 1-10 subscriptions
        medium_usage = scopes.filter(subscription_count__gte=1, subscription_count__lte=10).count()
        # Low usage: 0 subscriptions
        low_usage = scopes.filter(subscription_count=0).count()
    else:
        high_usage = medium_usage = low_usage = 0

    context = {
        'scopes': scopes,
        'categories_labels': categories_labels,
        'categories_counts': categories_counts,
        'usage_data': [high_usage, medium_usage, low_usage],
    }

    return render(request, 'dashboard/scopes.html', context)


@admin_required
def analytics_api(request):
    """API endpoint for analytics data"""

    # Get date range
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)

    # Generate date range
    date_range = [start_date + timedelta(days=i) for i in range(days + 1)]

    # Users growth
    users_data = []
    for date in date_range:
        count = User.objects.filter(date_joined__date__lte=date.date()).count()
        users_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })

    # Revenue per day
    revenue_data = []
    for date in date_range:
        amount = PaymentTransaction.objects.filter(
            created_at__date=date.date(),
            status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        revenue_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'amount': float(amount)
        })

    # Messages per day
    messages_data = []
    for date in date_range:
        count = AIMessage.objects.filter(created_at__date=date.date()).count()
        messages_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })

    return JsonResponse({
        'users': users_data,
        'revenue': revenue_data,
        'messages': messages_data,
    })


# Package CRUD Views
@admin_required
def package_create(request):
    """Create a new package"""
    if request.method == 'POST':
        try:
            package = Package.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                price=request.POST.get('price'),
                duration=request.POST.get('duration'),
                duration_days=request.POST.get('duration_days'),
                max_scopes=request.POST.get('max_scopes'),
                messages_per_day=request.POST.get('messages_per_day'),
                custom_goals_enabled=request.POST.get('custom_goals_enabled') == 'on',
                priority_support=request.POST.get('priority_support') == 'on',
                is_active=request.POST.get('is_active', 'on') == 'on',
                is_featured=request.POST.get('is_featured') == 'on',
                display_order=request.POST.get('display_order', 0)
            )
            messages.success(request, f'تم إنشاء الباقة {package.name} بنجاح')
            return redirect('dashboard:packages')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    return render(request, 'dashboard/package_form.html', {'is_edit': False})


@admin_required
def package_edit(request, pk):
    """Edit package details"""
    package = get_object_or_404(Package, pk=pk)

    if request.method == 'POST':
        try:
            package.name = request.POST.get('name', package.name)
            package.description = request.POST.get('description', package.description)
            package.price = request.POST.get('price', package.price)
            package.duration = request.POST.get('duration', package.duration)
            package.duration_days = request.POST.get('duration_days', package.duration_days)
            package.max_scopes = request.POST.get('max_scopes', package.max_scopes)
            package.messages_per_day = request.POST.get('messages_per_day', package.messages_per_day)
            package.custom_goals_enabled = request.POST.get('custom_goals_enabled') == 'on'
            package.priority_support = request.POST.get('priority_support') == 'on'
            package.is_active = request.POST.get('is_active', 'on') == 'on'
            package.is_featured = request.POST.get('is_featured') == 'on'
            package.display_order = request.POST.get('display_order', package.display_order)

            package.save()
            messages.success(request, f'تم تحديث الباقة {package.name} بنجاح')
            return redirect('dashboard:packages')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    context = {
        'package': package,
        'is_edit': True,
    }
    return render(request, 'dashboard/package_form.html', context)


# Scope CRUD Views
@admin_required
def scope_create(request):
    """Create a new scope"""
    if request.method == 'POST':
        try:
            scope = Scope.objects.create(
                name=request.POST.get('name'),
                category=request.POST.get('category'),
                description=request.POST.get('description'),
                icon=request.POST.get('icon', ''),
                is_active=request.POST.get('is_active', 'on') == 'on'
            )
            messages.success(request, f'تم إنشاء المجال {scope.name} بنجاح')
            return redirect('dashboard:scopes')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    context = {
        'is_edit': False,
        'categories': Scope.SCOPE_CATEGORIES,
    }
    return render(request, 'dashboard/scope_form.html', context)


@admin_required
def scope_edit(request, pk):
    """Edit scope details"""
    scope = get_object_or_404(Scope, pk=pk)

    if request.method == 'POST':
        try:
            scope.name = request.POST.get('name', scope.name)
            scope.category = request.POST.get('category', scope.category)
            scope.description = request.POST.get('description', scope.description)
            scope.icon = request.POST.get('icon', scope.icon)
            scope.is_active = request.POST.get('is_active', 'on') == 'on'

            scope.save()
            messages.success(request, f'تم تحديث المجال {scope.name} بنجاح')
            return redirect('dashboard:scopes')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    context = {
        'scope': scope,
        'is_edit': True,
        'categories': Scope.SCOPE_CATEGORIES,
    }
    return render(request, 'dashboard/scope_form.html', context)


# Subscription Edit View
@admin_required
def subscription_edit(request, pk):
    """Edit subscription details"""
    subscription = get_object_or_404(Subscription, pk=pk)

    if request.method == 'POST':
        try:
            subscription.status = request.POST.get('status', subscription.status)
            subscription.auto_renew = request.POST.get('auto_renew') == 'on'

            # Update selected scopes
            scope_ids = request.POST.getlist('scopes')
            if scope_ids:
                subscription.selected_scopes.set(Scope.objects.filter(id__in=scope_ids))

            subscription.save()
            messages.success(request, 'تم تحديث الاشتراك بنجاح')
            return redirect('dashboard:subscription_detail', pk=subscription.id)
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

    context = {
        'subscription': subscription,
        'all_scopes': Scope.objects.filter(is_active=True),
        'status_choices': Subscription.STATUS_CHOICES,
    }
    return render(request, 'dashboard/subscription_edit.html', context)
