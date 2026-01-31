from rest_framework import serializers
from django.contrib.auth import authenticate
from django_countries.serializer_fields import CountryField
from .models import (
    CustomUser, Scope, Package, Subscription, UserGoal,
    AIMessage, PaymentTransaction
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model"""
    country = CountryField(read_only=True)
    full_name = serializers.ReadOnlyField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    has_active_trial = serializers.ReadOnlyField()
    trial_remaining_days = serializers.ReadOnlyField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'role_display', 'mobile_phone', 'country',
            'date_of_birth', 'is_phone_verified', 'trial_started_at',
            'trial_expires_at', 'has_used_trial', 'has_active_trial',
            'trial_remaining_days', 'date_joined'
        ]
        read_only_fields = [
            'id', 'date_joined', 'is_phone_verified', 'trial_started_at',
            'trial_expires_at', 'has_used_trial'
        ]


class ScopeSerializer(serializers.ModelSerializer):
    """Serializer for Scope model"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Scope
        fields = [
            'id', 'name', 'category', 'category_display',
            'description', 'icon', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PackageSerializer(serializers.ModelSerializer):
    """Serializer for Package model"""
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)

    class Meta:
        model = Package
        fields = [
            'id', 'name', 'description', 'price', 'duration',
            'duration_display', 'duration_days', 'max_scopes',
            'messages_per_day', 'custom_goals_enabled', 'priority_support',
            'is_active', 'is_featured', 'display_order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing subscriptions"""
    package_name = serializers.CharField(source='package.name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active_status = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'user_email', 'package', 'package_name',
            'status', 'status_display', 'is_active_status',
            'start_date', 'end_date', 'amount_paid',
            'auto_renew', 'created_at'
        ]


class SubscriptionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for subscription with all relationships"""
    package = PackageSerializer(read_only=True)
    package_id = serializers.PrimaryKeyRelatedField(
        queryset=Package.objects.all(),
        source='package',
        write_only=True
    )
    selected_scopes = ScopeSerializer(many=True, read_only=True)
    selected_scope_ids = serializers.PrimaryKeyRelatedField(
        queryset=Scope.objects.all(),
        many=True,
        source='selected_scopes',
        write_only=True,
        required=False
    )
    user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active_status = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'package', 'package_id',
            'selected_scopes', 'selected_scope_ids',
            'status', 'status_display', 'is_active_status',
            'start_date', 'end_date',
            'payment_id', 'payment_method', 'amount_paid',
            'auto_renew', 'cancelled_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'status', 'start_date', 'end_date',
            'payment_id', 'payment_method', 'amount_paid',
            'cancelled_at', 'created_at', 'updated_at'
        ]

    def validate_selected_scope_ids(self, value):
        """Validate that user doesn't select more scopes than allowed"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            package_id = self.initial_data.get('package_id')
            if package_id:
                try:
                    package = Package.objects.get(id=package_id)
                    if len(value) > package.max_scopes:
                        raise serializers.ValidationError(
                            f"You can only select up to {package.max_scopes} scopes for this package."
                        )
                except Package.DoesNotExist:
                    pass
        return value


class UserGoalSerializer(serializers.ModelSerializer):
    """Serializer for UserGoal model"""
    scope_name = serializers.CharField(source='scope.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = UserGoal
        fields = [
            'id', 'user', 'subscription', 'scope', 'scope_name',
            'title', 'description', 'target_date',
            'status', 'status_display', 'progress_percentage',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate that user has custom goals enabled in their subscription"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            subscription = data.get('subscription')
            if subscription and not subscription.package.custom_goals_enabled:
                raise serializers.ValidationError(
                    "Custom goals are not available in your current subscription package."
                )
        return data


class AIMessageSerializer(serializers.ModelSerializer):
    """Serializer for AI Message model"""
    scope_name = serializers.CharField(source='scope.name', read_only=True)
    goal_title = serializers.CharField(source='goal.title', read_only=True)
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)

    class Meta:
        model = AIMessage
        fields = [
            'id', 'user', 'subscription', 'scope', 'scope_name',
            'goal', 'goal_title', 'message_type', 'message_type_display',
            'prompt_used', 'content', 'is_read', 'is_favorited',
            'user_rating', 'ai_model', 'tokens_used', 'generation_time',
            'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'subscription', 'prompt_used', 'content',
            'ai_model', 'tokens_used', 'generation_time', 'created_at'
        ]


class AIMessageCreateSerializer(serializers.Serializer):
    """Serializer for creating AI messages"""
    scope_id = serializers.IntegerField(required=False, allow_null=True)
    goal_id = serializers.IntegerField(required=False, allow_null=True)
    message_type = serializers.ChoiceField(
        choices=AIMessage.MESSAGE_TYPES,
        default='daily'
    )
    custom_prompt = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Additional context or specific request"
    )

    def validate(self, data):
        """Validate scope and goal exist if provided"""
        if data.get('scope_id'):
            try:
                Scope.objects.get(id=data['scope_id'])
            except Scope.DoesNotExist:
                raise serializers.ValidationError({"scope_id": "Invalid scope ID"})

        if data.get('goal_id'):
            try:
                UserGoal.objects.get(id=data['goal_id'])
            except UserGoal.DoesNotExist:
                raise serializers.ValidationError({"goal_id": "Invalid goal ID"})

        return data


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for Payment Transaction model"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    subscription_package = serializers.CharField(source='subscription.package.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'subscription', 'subscription_package', 'user', 'user_email',
            'tap_charge_id', 'tap_transaction_url', 'amount', 'currency',
            'status', 'status_display', 'payment_method',
            'customer_email', 'customer_phone', 'error_message',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'tap_charge_id', 'status',
            'created_at', 'updated_at', 'completed_at'
        ]


class SubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for initiating a subscription with payment"""
    package_id = serializers.IntegerField()
    selected_scope_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )

    # Customer details for payment
    customer_email = serializers.EmailField(required=False)
    customer_phone = serializers.CharField(max_length=20, required=False)

    # Payment redirect URLs
    redirect_url = serializers.URLField(required=False)
    post_url = serializers.URLField(required=False)

    def validate_package_id(self, value):
        """Validate package exists and is active"""
        try:
            package = Package.objects.get(id=value, is_active=True)
            self.context['package'] = package
            return value
        except Package.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive package ID")

    def validate_selected_scope_ids(self, value):
        """Validate scopes exist and limit not exceeded"""
        if not value:
            return []

        # Check all scopes exist
        scopes = Scope.objects.filter(id__in=value, is_active=True)
        if scopes.count() != len(value):
            raise serializers.ValidationError("One or more invalid scope IDs")

        # Check against package limit (if package validated)
        package = self.context.get('package')
        if package and len(value) > package.max_scopes:
            raise serializers.ValidationError(
                f"You can only select up to {package.max_scopes} scopes for this package"
            )

        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    country = CountryField(required=False)
    start_trial = serializers.BooleanField(default=True, write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'mobile_phone',
            'country', 'date_of_birth', 'start_trial'
        ]
        extra_kwargs = {
            'role': {'default': 'normal'}
        }

    def validate_email(self, value):
        """Validate email is unique"""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Validate username is unique"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate(self, data):
        """Validate passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return data

    def create(self, validated_data):
        """Create user with encrypted password and optional trial"""
        validated_data.pop('password_confirm')
        start_trial = validated_data.pop('start_trial', True)

        user = CustomUser.objects.create_user(
            password=validated_data.pop('password'),
            **validated_data
        )

        # Auto-start free trial for normal users and subscribers
        if start_trial and user.role in ['normal', 'subscriber']:
            user.start_free_trial()

        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(
        help_text="Username or email address"
    )
    password = serializers.CharField()

    def validate(self, data):
        """Validate username/email and password"""
        username = data.get('username')
        password = data.get('password')

        if username and password:
            # Try to authenticate with username or email
            user = None

            # First, try to find user by username
            try:
                user_obj = CustomUser.objects.get(username=username)
                user = authenticate(
                    request=self.context.get('request'),
                    username=user_obj.email,
                    password=password
                )
            except CustomUser.DoesNotExist:
                # If not found by username, try as email directly
                user = authenticate(
                    request=self.context.get('request'),
                    username=username,
                    password=password
                )

            if not user:
                raise serializers.ValidationError("Invalid credentials.")

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")

            data['user'] = user
            return data
        else:
            raise serializers.ValidationError("Must include username/email and password.")


class TrialManagementSerializer(serializers.Serializer):
    """Serializer for admin trial management"""
    user_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['start', 'extend', 'cancel'])
    days = serializers.IntegerField(required=False, min_value=1, max_value=365)

    def validate_user_id(self, value):
        """Validate user exists"""
        if not CustomUser.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found.")
        return value

    def validate(self, data):
        """Validate action-specific requirements"""
        action = data['action']

        if action == 'extend' and 'days' not in data:
            raise serializers.ValidationError("Days field is required for extend action.")

        return data


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for admin user list"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    has_active_trial = serializers.ReadOnlyField()
    trial_remaining_days = serializers.ReadOnlyField()
    active_subscription_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'role_display', 'is_active', 'date_joined',
            'has_active_trial', 'trial_remaining_days', 'active_subscription_count'
        ]

    def get_active_subscription_count(self, obj):
        """Get count of active subscriptions"""
        return obj.subscriptions.filter(status='active').count()
