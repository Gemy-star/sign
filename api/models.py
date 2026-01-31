from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField


class CustomUser(AbstractUser):
    """
    Custom user model with additional fields for mobile phone and country
    """
    USER_ROLES = [
        ('admin', 'Admin'),
        ('subscriber', 'Subscriber'),
        ('normal', 'Normal'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='normal')
    mobile_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Mobile phone number with country code"
    )
    country = CountryField(
        blank=True,
        null=True,
        help_text="Country of residence"
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="Date of birth"
    )
    is_phone_verified = models.BooleanField(
        default=False,
        help_text="Whether the mobile phone number has been verified"
    )
    phone_verification_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text="Verification code for phone number"
    )
    phone_verification_expires = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Expiration time for phone verification code"
    )

    # Free trial fields
    trial_started_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the free trial started"
    )
    trial_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the free trial expires"
    )
    has_used_trial = models.BooleanField(
        default=False,
        help_text="Whether the user has used their free trial"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.email} ({self.username})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_display_name(self):
        if self.full_name:
            return self.full_name
        return self.username

    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'

    @property
    def is_normal(self):
        """Check if user is normal"""
        return self.role == 'normal'

    @property
    def is_subscriber(self):
        """Check if user is subscriber"""
        return self.role == 'subscriber'

    @property
    def has_active_trial(self):
        """Check if user has an active free trial"""
        if not self.trial_expires_at:
            return False
        return timezone.now() < self.trial_expires_at

    @property
    def trial_remaining_days(self):
        """Get remaining days in trial"""
        if not self.trial_expires_at:
            return 0
        delta = self.trial_expires_at - timezone.now()
        return max(0, delta.days)

    def start_free_trial(self, trial_days=7):
        """Start free trial for user"""
        if self.has_used_trial:
            return False, "User has already used their free trial"

        self.trial_started_at = timezone.now()
        self.trial_expires_at = self.trial_started_at + timedelta(days=trial_days)
        self.has_used_trial = True
        self.save()

        return True, f"Free trial started for {trial_days} days"

    def upgrade_to_subscriber(self):
        """Upgrade normal user to subscriber when they purchase subscription"""
        if self.role == 'normal':
            self.role = 'subscriber'
            self.save()
            return True, "User upgraded to subscriber"
        return False, "User is already a subscriber or admin"

    def downgrade_to_normal(self):
        """Downgrade subscriber back to normal (admin only)"""
        if self.role == 'subscriber':
            self.role = 'normal'
            self.save()
            return True, "User downgraded to normal"
        return False, "User is not a subscriber"

    def get_user_scopes(self):
        """Get user's available scopes based on subscription and trial"""
        scopes = []

        # Admin has access to all scopes
        if self.is_admin:
            scopes.extend(['admin', 'user_management', 'trial_management', 'all_content'])

        # Check for active subscription or trial
        has_access = False
        if self.has_active_trial:
            has_access = True
            scopes.append('trial')

        # Check for active subscriptions
        active_subscriptions = self.subscriptions.filter(
            status='active',
            end_date__gt=timezone.now()
        )

        if active_subscriptions.exists():
            has_access = True
            scopes.append('subscriber')

            # Add package-specific scopes
            for sub in active_subscriptions:
                if sub.package.custom_goals_enabled:
                    scopes.append('custom_goals')
                if sub.package.priority_support:
                    scopes.append('priority_support')
                if sub.package.messages_per_day > 0:
                    scopes.append(f'messages_{sub.package.messages_per_day}_per_day')

        # Basic scopes for all authenticated users
        if self.is_authenticated:
            scopes.extend(['profile', 'basic_access'])

        return list(set(scopes))  # Remove duplicates

    def get_user_permissions(self):
        """Get user's permissions based on role and subscription"""
        permissions = []

        # Role-based permissions
        if self.is_admin:
            permissions.extend([
                'create_users', 'delete_users', 'manage_trials',
                'view_all_users', 'manage_subscriptions'
            ])

        if self.is_subscriber or self.is_normal:
            permissions.extend([
                'view_profile', 'update_profile', 'create_goals',
                'view_own_subscriptions', 'manage_own_goals'
            ])

        # Trial-specific permissions
        if self.has_active_trial:
            permissions.extend(['trial_access', 'limited_features'])

        # Subscription-based permissions
        active_subscriptions = self.subscriptions.filter(
            status='active',
            end_date__gt=timezone.now()
        )

        for sub in active_subscriptions:
            if sub.package.custom_goals_enabled:
                permissions.append('create_custom_goals')
            if sub.package.priority_support:
                permissions.append('priority_support')
            if sub.package.messages_per_day > 1:
                permissions.append('multiple_messages')

        return list(set(permissions))  # Remove duplicates

    def has_scope(self, scope):
        """Check if user has a specific scope"""
        return scope in self.get_user_scopes()

    def has_permission(self, permission):
        """Check if user has a specific permission"""
        return permission in self.get_user_permissions()

    def can_access_feature(self, feature):
        """Check if user can access a specific feature"""
        # Check based on role, subscription, and trial
        if self.is_admin:
            return True

        if feature in ['basic_profile', 'view_content']:
            return True

        if feature == 'trial_features' and self.has_active_trial:
            return True

        if feature == 'subscriber_features':
            return self.is_subscriber and self.subscriptions.filter(
                status='active',
                end_date__gt=timezone.now()
            ).exists()

        if feature == 'custom_goals':
            return self.subscriptions.filter(
                status='active',
                end_date__gt=timezone.now(),
                package__custom_goals_enabled=True
            ).exists()

        return False

    def extend_trial(self, additional_days):
        """Extend existing trial (admin only)"""
        if not self.trial_expires_at:
            return False, "No active trial to extend"

        self.trial_expires_at += timedelta(days=additional_days)
        self.save()

        return True, f"Trial extended by {additional_days} days"

    def cancel_trial(self):
        """Cancel free trial (admin only)"""
        self.trial_expires_at = timezone.now()
        self.save()
        return True, "Trial cancelled"


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

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
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

        # Upgrade normal user to subscriber
        if self.user.is_normal:
            self.user.upgrade_to_subscriber()

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

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='goals')
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
    AI-generated messages based on scopes and goals
    """
    MESSAGE_TYPES = [
        ('daily', 'Daily Motivation'),
        ('goal_specific', 'Goal Specific'),
        ('scope_based', 'Scope Based'),
        ('custom', 'Custom Request'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ai_messages')
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_transactions')

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
