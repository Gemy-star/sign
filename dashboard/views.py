from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from api.models import (
    Scope, Package, Subscription, UserGoal,
    AIMessage, PaymentTransaction
)
from django.contrib.auth.models import User


@staff_member_required
def dashboard_home(request):
    """Dashboard home page with statistics and charts"""

    # Calculate statistics
    total_users = User.objects.count()
    total_subscriptions = Subscription.objects.filter(status='active').count()
    total_revenue = PaymentTransaction.objects.filter(
        status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_messages = AIMessage.objects.count()

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
        count = User.objects.filter(
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
        'recent_subscriptions': recent_subscriptions,
        'recent_messages': recent_messages,
        'users_per_day': users_per_day,
        'revenue_per_day': revenue_per_day,
        'packages_data': list(packages_data),
        'days_labels': [day.strftime('%A') for day in last_7_days],
    }

    return render(request, 'dashboard/home.html', context)


@staff_member_required
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


@staff_member_required
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

    context = {
        'subscriptions': subscriptions,
        'status_filter': status_filter,
        'status_counts': {item['status']: item['count'] for item in status_counts},
    }

    return render(request, 'dashboard/subscriptions.html', context)


@staff_member_required
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


@staff_member_required
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


@staff_member_required
def users_list(request):
    """List all users"""
    users = User.objects.annotate(
        active_subs=Count('subscriptions', filter=Q(subscriptions__status='active')),
        total_messages=Count('ai_messages')
    ).order_by('-date_joined')[:50]

    context = {
        'users': users,
    }

    return render(request, 'dashboard/users.html', context)


@staff_member_required
def scopes_list(request):
    """List all scopes"""
    scopes = Scope.objects.annotate(
        subscription_count=Count('subscriptions'),
        message_count=Count('messages')
    ).order_by('category', 'name')

    context = {
        'scopes': scopes,
    }

    return render(request, 'dashboard/scopes.html', context)


@staff_member_required
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
