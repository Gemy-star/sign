from django.contrib import admin
from .models import (
    Scope, Package, Subscription, UserGoal,
    AIMessage, PaymentTransaction
)


@admin.register(Scope)
class ScopeAdmin(admin.ModelAdmin):
    """Admin interface for Scope model"""
    list_display = ['name', 'category', 'icon', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    """Admin interface for Package model"""
    list_display = [
        'name', 'price', 'duration', 'max_scopes',
        'messages_per_day', 'custom_goals_enabled',
        'is_active', 'is_featured', 'display_order'
    ]
    list_filter = ['duration', 'is_active', 'is_featured', 'custom_goals_enabled']
    search_fields = ['name', 'description']
    ordering = ['display_order', 'price']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'display_order')
        }),
        ('Pricing', {
            'fields': ('price', 'duration', 'duration_days')
        }),
        ('Features', {
            'fields': (
                'max_scopes', 'messages_per_day',
                'custom_goals_enabled', 'priority_support'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription model"""
    list_display = [
        'user', 'package', 'status', 'start_date',
        'end_date', 'amount_paid', 'auto_renew'
    ]
    list_filter = ['status', 'auto_renew', 'package', 'start_date', 'created_at']
    search_fields = ['user__username', 'user__email', 'payment_id']
    readonly_fields = ['created_at', 'updated_at', 'cancelled_at']
    filter_horizontal = ['selected_scopes']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('User & Package', {
            'fields': ('user', 'package', 'selected_scopes')
        }),
        ('Status', {
            'fields': ('status', 'start_date', 'end_date', 'auto_renew')
        }),
        ('Payment Information', {
            'fields': ('payment_id', 'payment_method', 'amount_paid')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_subscriptions', 'cancel_subscriptions']

    def activate_subscriptions(self, request, queryset):
        """Bulk activate subscriptions"""
        for subscription in queryset:
            subscription.activate()
        self.message_user(request, f'{queryset.count()} subscriptions activated.')
    activate_subscriptions.short_description = "Activate selected subscriptions"

    def cancel_subscriptions(self, request, queryset):
        """Bulk cancel subscriptions"""
        for subscription in queryset:
            subscription.cancel()
        self.message_user(request, f'{queryset.count()} subscriptions cancelled.')
    cancel_subscriptions.short_description = "Cancel selected subscriptions"


@admin.register(UserGoal)
class UserGoalAdmin(admin.ModelAdmin):
    """Admin interface for UserGoal model"""
    list_display = [
        'title', 'user', 'scope', 'status',
        'progress_percentage', 'target_date', 'created_at'
    ]
    list_filter = ['status', 'scope', 'created_at', 'target_date']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Goal Information', {
            'fields': ('user', 'subscription', 'scope', 'title', 'description')
        }),
        ('Progress', {
            'fields': ('status', 'progress_percentage', 'target_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    """Admin interface for AIMessage model"""
    list_display = [
        'user', 'message_type', 'scope', 'is_read',
        'is_favorited', 'user_rating', 'created_at'
    ]
    list_filter = [
        'message_type', 'is_read', 'is_favorited',
        'user_rating', 'created_at', 'ai_model'
    ]
    search_fields = ['content', 'user__username', 'prompt_used']
    readonly_fields = [
        'created_at', 'user', 'subscription', 'prompt_used',
        'content', 'ai_model', 'tokens_used', 'generation_time'
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Message Details', {
            'fields': (
                'user', 'subscription', 'message_type',
                'scope', 'goal'
            )
        }),
        ('AI Content', {
            'fields': ('prompt_used', 'content', 'ai_model', 'tokens_used', 'generation_time')
        }),
        ('User Interaction', {
            'fields': ('is_read', 'is_favorited', 'user_rating')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """Admin interface for PaymentTransaction model"""
    list_display = [
        'tap_charge_id', 'user', 'amount', 'currency',
        'status', 'payment_method', 'created_at'
    ]
    list_filter = ['status', 'currency', 'payment_method', 'created_at']
    search_fields = [
        'tap_charge_id', 'user__username', 'user__email',
        'customer_email', 'customer_phone'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'completed_at',
        'tap_charge_id', 'raw_response'
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'subscription', 'user', 'tap_charge_id',
                'tap_transaction_url'
            )
        }),
        ('Payment Information', {
            'fields': (
                'amount', 'currency', 'status',
                'payment_method'
            )
        }),
        ('Customer Details', {
            'fields': ('customer_email', 'customer_phone')
        }),
        ('Response Data', {
            'fields': ('raw_response', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


# Customize admin site header and title
admin.site.site_header = "AiaY Admin"
admin.site.site_title = "AiaY"
admin.site.index_title = "Dashboard"
