from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Scope(models.Model):
    """
    Represents different life domains for personal development
    """
    SCOPE_CATEGORIES = [
        ('mental', 'Mental and Emotional Growth'),
        ('physical', 'Physical Health and Wellness'),
        ('career', 'Career and Professional Development'),
        ('financial', 'Financial Growth'),
        ('relationships', 'Relationships and Social Life'),
        ('spiritual', 'Spiritual and Inner Fulfillment'),
        ('creativity', 'Creativity and Learning'),
        ('lifestyle', 'Lifestyle and Environment'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=SCOPE_CATEGORIES)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, null=True)  # emoji or icon class
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Scope'
        verbose_name_plural = 'Scopes'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Package(models.Model):
    """
    Subscription packages with different features and pricing
    """
    DURATION_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='monthly')
    duration_days = models.IntegerField(help_text="Number of days for this package")

    # Features
    max_scopes = models.IntegerField(default=3, help_text="Maximum number of scopes user can select")
    messages_per_day = models.IntegerField(default=1, help_text="Number of AI messages per day")
    custom_goals_enabled = models.BooleanField(default=False, help_text="Allow users to set custom goals")
    priority_support = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'price']
        verbose_name = 'Package'
        verbose_name_plural = 'Packages'

    def __str__(self):
        return f"{self.name} - ${self.price}/{self.duration}"


class Subscription(models.Model):
    """
    User subscriptions linked to packages
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
        ('failed', 'Payment Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(Package, on_delete=models.PROTECT, related_name='subscriptions')
    selected_scopes = models.ManyToManyField(Scope, related_name='subscriptions', blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Payment information
    payment_id = models.CharField(max_length=255, blank=True, null=True, help_text="Tap Payment ID")
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    auto_renew = models.BooleanField(default=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f"{self.user.username} - {self.package.name} ({self.status})"

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        if self.status != 'active':
            return False
        if self.end_date and timezone.now() > self.end_date:
            return False
        return True

    def activate(self):
        """Activate subscription after successful payment"""
        self.status = 'active'
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=self.package.duration_days)
        self.save()

    def cancel(self):
        """Cancel subscription"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.auto_renew = False
        self.save()


class UserGoal(models.Model):
    """
    Custom goals set by users (available in premium packages)
    """
    GOAL_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('archived', 'Archived'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='goals')
    scope = models.ForeignKey(Scope, on_delete=models.SET_NULL, null=True, related_name='user_goals')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=GOAL_STATUS, default='active')
    progress_percentage = models.IntegerField(default=0, help_text="0-100")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Goal'
        verbose_name_plural = 'User Goals'

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class AIMessage(models.Model):
    """
    AI-generated motivational messages based on scopes and goals
    """
    MESSAGE_TYPES = [
        ('daily', 'Daily Motivation'),
        ('goal_specific', 'Goal Specific'),
        ('scope_based', 'Scope Based'),
        ('custom', 'Custom Request'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_messages')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='messages')
    scope = models.ForeignKey(Scope, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    goal = models.ForeignKey(UserGoal, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')

    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='daily')
    prompt_used = models.TextField(help_text="The prompt sent to ChatGPT")
    content = models.TextField(help_text="AI-generated message content")

    is_read = models.BooleanField(default=False)
    is_favorited = models.BooleanField(default=False)
    user_rating = models.IntegerField(null=True, blank=True, help_text="1-5 rating")

    # AI metadata
    ai_model = models.CharField(max_length=50, default='gpt-3.5-turbo')
    tokens_used = models.IntegerField(null=True, blank=True)
    generation_time = models.FloatField(null=True, blank=True, help_text="Time in seconds")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Message'
        verbose_name_plural = 'AI Messages'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['subscription', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.message_type} - {self.created_at.strftime('%Y-%m-%d')}"


class PaymentTransaction(models.Model):
    """
    Track all payment transactions for audit and reconciliation
    """
    TRANSACTION_STATUS = [
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_transactions')

    # Tap Payment details
    tap_charge_id = models.CharField(max_length=255, unique=True)
    tap_transaction_url = models.URLField(blank=True, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='initiated')

    payment_method = models.CharField(max_length=100, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)

    # Response data
    raw_response = models.JSONField(null=True, blank=True, help_text="Full API response from Tap")
    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency} - {self.status}"
