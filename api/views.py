from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.decorators import method_decorator

from .models import (
    CustomUser, Scope, Package, Subscription, UserGoal,
    AIMessage, PaymentTransaction
)
from .serializers import (
    ScopeSerializer, PackageSerializer,
    SubscriptionListSerializer, SubscriptionDetailSerializer,
    SubscriptionCreateSerializer, UserGoalSerializer,
    AIMessageSerializer, AIMessageCreateSerializer,
    PaymentTransactionSerializer, UserRegistrationSerializer,
    UserLoginSerializer, UserSerializer, TrialManagementSerializer,
    UserListSerializer
)
from .jwt_utils import get_user_token
from .services import OpenAIService, TapPaymentService
from .permissions import IsOwnerOrReadOnly, HasActiveSubscription
from .scope_permissions import (
    require_scope, require_permission, require_feature,
    AdminScopePermission, SubscriberScopePermission, TrialScopePermission,
    CustomGoalsPermission, check_subscription_or_trial
)
from .scope_utils import ScopeManager


class UserRegistrationView(APIView):
    """
    API endpoint for user registration
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=['auth'],
        operation_summary='Register a new user',
        operation_description=(
            'Create a new user account. Automatically starts a 7-day free trial '
            'for normal/subscriber roles when start_trial is true.'
        ),
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                'User registered successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT, description='Registered user data'),
                        'tokens': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
                                'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
                            }
                        ),
                    }
                )
            ),
            400: 'Validation error',
        }
    )
    def post(self, request):
        """Register a new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    API endpoint for user login
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=['auth'],
        operation_summary='Login user',
        operation_description=(
            'Authenticate with username or email and password. '
            'Returns JWT access and refresh tokens along with user info, scopes and permissions.'
        ),
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                'Login successful',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'token': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='JWT tokens with embedded user info',
                            properties={
                                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                                'access': openapi.Schema(type=openapi.TYPE_STRING),
                                'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                            }
                        ),
                        'user_info': openapi.Schema(type=openapi.TYPE_OBJECT, description='Detailed user information'),
                    }
                )
            ),
            400: 'Invalid credentials',
        }
    )
    def post(self, request):
        """Login user and return JWT token with scopes"""
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate custom token with scopes and permissions
            token_data = get_user_token(user)

            return Response({
                'message': 'Login successful',
                'token': token_data,
                'user_info': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'full_name': user.full_name,
                    'has_active_trial': user.has_active_trial,
                    'trial_remaining_days': user.trial_remaining_days,
                    'scopes': user.get_user_scopes(),
                    'permissions': user.get_user_permissions(),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    API endpoint for getting and updating user profile
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=['auth'],
        operation_summary='Get user profile',
        operation_description='Retrieve the authenticated user\'s profile details.',
        responses={200: openapi.Response('User profile', UserSerializer)}
    )
    def get(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['auth'],
        operation_summary='Update user profile',
        operation_description='Partially update the authenticated user\'s profile. All fields are optional.',
        request_body=UserSerializer,
        responses={
            200: openapi.Response('Updated user profile', UserSerializer),
            400: 'Validation error',
        }
    )
    def patch(self, request):
        """Update current user profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUserManagementView(APIView):
    """
    Admin endpoints for user management
    """
    permission_classes = [permissions.IsAuthenticated, AdminScopePermission]

    @swagger_auto_schema(
        tags=['admin'],
        operation_summary='List all users',
        operation_description='Returns a list of all registered users. Requires admin:user_management scope.',
        responses={200: openapi.Response('List of users', UserListSerializer(many=True))}
    )
    @require_scope('admin', 'user_management')
    def get(self, request):
        """List all users (admin only)"""
        users = CustomUser.objects.all().order_by('-date_joined')
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['admin'],
        operation_summary='Create admin user',
        operation_description='Create a new user with the admin role. Requires create_users permission. The role field is forced to admin regardless of the value provided.',
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response('Admin user created', UserSerializer),
            400: 'Validation error',
        }
    )
    @require_permission('create_users')
    def post(self, request):
        """Create admin user (admin only)"""
        data = request.data.copy()
        data['role'] = 'admin'
        serializer = UserRegistrationSerializer(data=data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrialManagementView(APIView):
    """
    Admin endpoint for trial management
    """
    permission_classes = [permissions.IsAuthenticated, AdminScopePermission]

    @swagger_auto_schema(
        tags=['admin'],
        operation_summary='Manage user trial',
        operation_description='Start, extend, or cancel a user\'s free trial. Requires manage_trials permission. The days field is only required when action is extend.',
        request_body=TrialManagementSerializer,
        responses={
            200: openapi.Response(
                'Trial action result',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT, description='Updated user data'),
                    }
                )
            ),
            400: 'Invalid action or validation error',
            404: 'User not found',
        }
    )
    @require_permission('manage_trials')
    def post(self, request):
        """Manage user trials (admin only)"""
        serializer = TrialManagementSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data['user_id']
        action = serializer.validated_data['action']
        days = serializer.validated_data.get('days', 7)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Perform trial action
        if action == 'start':
            success, message = user.start_free_trial(days)
        elif action == 'extend':
            success, message = user.extend_trial(days)
        elif action == 'cancel':
            success, message = user.cancel_trial()

        if success:
            return Response({
                "message": message,
                "user": UserSerializer(user).data
            })
        else:
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['scopes'],
    operation_summary='List all active scopes',
    operation_description='Returns all active scopes. Filter by category using the category query parameter.',
    manual_parameters=[
        openapi.Parameter(
            'category', openapi.IN_QUERY,
            description='Filter by category',
            type=openapi.TYPE_STRING,
            enum=['mental', 'physical', 'career', 'financial', 'relationships', 'spiritual', 'creativity', 'lifestyle'],
            required=False,
        ),
    ],
    responses={200: openapi.Response('List of scopes', ScopeSerializer(many=True))}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    tags=['scopes'],
    operation_summary='Retrieve a scope by ID',
    responses={
        200: openapi.Response('Scope detail', ScopeSerializer),
        404: 'Not found',
    }
))
class ScopeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing scopes (life domains)

    list: Get all active scopes (anonymous allowed)
    retrieve: Get a specific scope by ID (anonymous allowed)
    create: Create a new scope (login required)
    update: Update a scope (login required)
    partial_update: Partially update a scope (login required)
    destroy: Delete a scope (login required)
    """
    queryset = Scope.objects.filter(is_active=True)
    serializer_class = ScopeSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'categories'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """Filter scopes by category if provided"""
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    @swagger_auto_schema(
        tags=['scopes'],
        operation_summary='Get scope categories',
        operation_description='Returns all available scope category options as value/label pairs.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'value': openapi.Schema(type=openapi.TYPE_STRING, description='Category key'),
                        'label': openapi.Schema(type=openapi.TYPE_STRING, description='Category display name'),
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all available scope categories"""
        categories = [
            {"value": cat[0], "label": cat[1]}
            for cat in Scope.SCOPE_CATEGORIES
        ]
        return Response(categories)


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['packages'],
    operation_summary='List all active packages',
    operation_description='Returns all active packages ordered by display_order and price. Pass featured=true to filter featured packages only.',
    manual_parameters=[
        openapi.Parameter(
            'featured', openapi.IN_QUERY,
            description='Set to true to return featured packages only',
            type=openapi.TYPE_BOOLEAN,
            required=False,
        ),
    ],
    responses={200: openapi.Response('List of packages', PackageSerializer(many=True))}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    tags=['packages'],
    operation_summary='Retrieve a package by ID',
    responses={
        200: openapi.Response('Package detail', PackageSerializer),
        404: 'Not found',
    }
))
class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing subscription packages

    list: Get all available packages
    retrieve: Get a specific package by ID
    featured: Get featured packages
    """
    queryset = Package.objects.filter(is_active=True)
    serializer_class = PackageSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Order by display_order and filter featured if requested"""
        queryset = super().get_queryset()
        if self.request.query_params.get('featured') == 'true':
            queryset = queryset.filter(is_featured=True)
        return queryset.order_by('display_order', 'price')

    @swagger_auto_schema(
        tags=['packages'],
        operation_summary='Get featured packages',
        operation_description='Returns only packages marked as featured.',
        responses={200: openapi.Response('Featured packages', PackageSerializer(many=True))}
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured packages only"""
        packages = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(packages, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['packages'],
        operation_summary='Package comparison',
        operation_description='Returns the selected package alongside all available packages for comparison.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'selected_package': openapi.Schema(type=openapi.TYPE_OBJECT, description='The selected package'),
                    'all_packages': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT),
                        description='All available packages'
                    ),
                }
            ),
            404: 'Package not found',
        }
    )
    @action(detail=True, methods=['get'])
    def comparison(self, request, pk=None):
        """Compare package features with others"""
        package = self.get_object()
        all_packages = self.queryset.all()
        serializer = self.get_serializer(all_packages, many=True)
        return Response({
            'selected_package': PackageSerializer(package).data,
            'all_packages': serializer.data
        })


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['subscriptions'],
    operation_summary='List user subscriptions',
    operation_description='Returns all subscriptions belonging to the authenticated user.',
    responses={200: openapi.Response('List of subscriptions', SubscriptionListSerializer(many=True))}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    tags=['subscriptions'],
    operation_summary='Retrieve subscription detail',
    responses={
        200: openapi.Response('Subscription detail', SubscriptionDetailSerializer),
        404: 'Not found',
    }
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    tags=['subscriptions'],
    operation_summary='Create subscription and initiate payment',
    operation_description='Creates a new subscription and initiates a payment via Tap Payment gateway. Returns a payment URL to redirect the user to.',
    request_body=SubscriptionCreateSerializer,
    responses={
        201: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'subscription_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'payment_url': openapi.Schema(type=openapi.TYPE_STRING, description='Tap Payment redirect URL'),
                'charge_id': openapi.Schema(type=openapi.TYPE_STRING),
                'status': openapi.Schema(type=openapi.TYPE_STRING, example='payment_initiated'),
            }
        ),
        400: 'Payment initialization failed',
    }
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    tags=['subscriptions'],
    operation_summary='Update subscription',
    responses={200: openapi.Response('Updated subscription', SubscriptionDetailSerializer)}
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    tags=['subscriptions'],
    operation_summary='Partially update subscription',
    responses={200: openapi.Response('Updated subscription', SubscriptionDetailSerializer)}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    tags=['subscriptions'],
    operation_summary='Delete subscription',
    responses={204: 'Deleted successfully'}
))
class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user subscriptions

    list: Get user's subscriptions
    retrieve: Get a specific subscription
    create: Create a new subscription (initiates payment)
    update: Update subscription scopes
    cancel: Cancel a subscription
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Users can only see their own subscriptions"""
        return Subscription.objects.filter(user=self.request.user).select_related(
            'package', 'user'
        ).prefetch_related('selected_scopes')

    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'list':
            return SubscriptionListSerializer
        elif self.action == 'create':
            return SubscriptionCreateSerializer
        return SubscriptionDetailSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new subscription and initiate payment
        """
        serializer = SubscriptionCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        package_id = serializer.validated_data['package_id']
        selected_scope_ids = serializer.validated_data.get('selected_scope_ids', [])

        # Get package
        package = Package.objects.get(id=package_id)

        # Create subscription (pending payment)
        subscription = Subscription.objects.create(
            user=request.user,
            package=package,
            status='pending'
        )

        # Add selected scopes
        if selected_scope_ids:
            subscription.selected_scopes.set(selected_scope_ids)

        # Initialize payment
        try:
            payment_service = TapPaymentService()
            payment_response = payment_service.create_charge(
                subscription=subscription,
                user=request.user,
                redirect_url=serializer.validated_data.get('redirect_url'),
                post_url=serializer.validated_data.get('post_url')
            )

            # Create payment transaction record
            transaction = PaymentTransaction.objects.create(
                subscription=subscription,
                user=request.user,
                tap_charge_id=payment_response['id'],
                tap_transaction_url=payment_response.get('transaction', {}).get('url'),
                amount=package.price,
                currency='USD',
                status='initiated',
                customer_email=serializer.validated_data.get('customer_email', request.user.email),
                customer_phone=serializer.validated_data.get('customer_phone'),
                raw_response=payment_response
            )

            return Response({
                'subscription_id': subscription.id,
                'payment_url': payment_response.get('transaction', {}).get('url'),
                'charge_id': payment_response['id'],
                'status': 'payment_initiated'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            subscription.status = 'failed'
            subscription.save()
            return Response({
                'error': 'Payment initialization failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['subscriptions'],
        operation_summary='Cancel subscription',
        operation_description='Cancel an active or pending subscription.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'subscription': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
            400: 'Subscription is not active or pending',
        }
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an active subscription"""
        subscription = self.get_object()

        if subscription.status not in ['active', 'pending']:
            return Response(
                {'error': 'Only active or pending subscriptions can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.cancel()

        return Response({
            'message': 'Subscription cancelled successfully',
            'subscription': SubscriptionDetailSerializer(subscription).data
        })

    @swagger_auto_schema(
        tags=['subscriptions'],
        operation_summary='Update subscription scopes',
        operation_description='Replace the selected scopes for an active subscription. Number of scopes must not exceed the package maximum.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['scope_ids'],
            properties={
                'scope_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='List of scope IDs to assign (replaces existing selection)',
                ),
            }
        ),
        responses={
            200: openapi.Response('Scopes updated', SubscriptionDetailSerializer),
            400: 'Subscription not active or too many scopes selected',
        }
    )
    @action(detail=True, methods=['patch'])
    def update_scopes(self, request, pk=None):
        """Update selected scopes for a subscription"""
        subscription = self.get_object()

        if not subscription.is_active:
            return Response(
                {'error': 'Cannot update scopes for inactive subscription'},
                status=status.HTTP_400_BAD_REQUEST
            )

        scope_ids = request.data.get('scope_ids', [])

        # Validate scope count
        if len(scope_ids) > subscription.package.max_scopes:
            return Response(
                {'error': f'Maximum {subscription.package.max_scopes} scopes allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update scopes
        subscription.selected_scopes.set(scope_ids)

        return Response({
            'message': 'Scopes updated successfully',
            'subscription': SubscriptionDetailSerializer(subscription).data
        })

    @swagger_auto_schema(
        tags=['subscriptions'],
        operation_summary='Get active subscription',
        operation_description='Returns the authenticated user\'s currently active, non-expired subscription.',
        responses={
            200: openapi.Response('Active subscription', SubscriptionDetailSerializer),
            404: 'No active subscription found',
        }
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get user's active subscription"""
        active_subscription = self.get_queryset().filter(
            status='active',
            end_date__gt=timezone.now()
        ).first()

        if active_subscription:
            serializer = SubscriptionDetailSerializer(active_subscription)
            return Response(serializer.data)

        return Response({'message': 'No active subscription'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['goals'],
    operation_summary='List user goals',
    operation_description='Returns all goals for the authenticated user. Requires an active subscription.',
    responses={200: openapi.Response('List of goals', UserGoalSerializer(many=True))}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    tags=['goals'],
    operation_summary='Retrieve a goal',
    responses={
        200: openapi.Response('Goal detail', UserGoalSerializer),
        404: 'Not found',
    }
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    tags=['goals'],
    operation_summary='Create a goal',
    operation_description='Create a new goal linked to an active subscription. Requires an active subscription with custom_goals_enabled.',
    request_body=UserGoalSerializer,
    responses={
        201: openapi.Response('Goal created', UserGoalSerializer),
        400: 'Validation error',
    }
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    tags=['goals'],
    operation_summary='Update a goal',
    request_body=UserGoalSerializer,
    responses={200: openapi.Response('Updated goal', UserGoalSerializer)}
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    tags=['goals'],
    operation_summary='Partially update a goal',
    request_body=UserGoalSerializer,
    responses={200: openapi.Response('Updated goal', UserGoalSerializer)}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    tags=['goals'],
    operation_summary='Delete a goal',
    responses={204: 'Deleted successfully'}
))
class UserGoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user goals

    list: Get user's goals
    create: Create a new goal (requires premium subscription)
    update: Update goal details
    delete: Delete a goal
    complete: Mark goal as completed
    """
    serializer_class = UserGoalSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def get_queryset(self):
        """Users can only see their own goals"""
        return UserGoal.objects.filter(user=self.request.user).select_related(
            'scope', 'subscription'
        )

    def perform_create(self, serializer):
        """Automatically set the user when creating a goal"""
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=['goals'],
        operation_summary='Mark goal as completed',
        operation_description='Sets the goal status to completed and progress_percentage to 100.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'goal': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
        }
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a goal as completed"""
        goal = self.get_object()
        goal.status = 'completed'
        goal.progress_percentage = 100
        goal.completed_at = timezone.now()
        goal.save()

        return Response({
            'message': 'Goal marked as completed',
            'goal': UserGoalSerializer(goal).data
        })

    @swagger_auto_schema(
        tags=['goals'],
        operation_summary='Update goal progress',
        operation_description='Update the progress_percentage of a goal. Automatically marks the goal as completed when progress reaches 100.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['progress_percentage'],
            properties={
                'progress_percentage': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Progress value between 0 and 100',
                    minimum=0,
                    maximum=100,
                ),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'goal': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
            400: 'Invalid progress value',
        }
    )
    @action(detail=True, methods=['patch'])
    def update_progress(self, request, pk=None):
        """Update goal progress percentage"""
        goal = self.get_object()
        progress = request.data.get('progress_percentage')

        if progress is None or not (0 <= progress <= 100):
            return Response(
                {'error': 'Progress must be between 0 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )

        goal.progress_percentage = progress
        if progress == 100 and goal.status != 'completed':
            goal.status = 'completed'
            goal.completed_at = timezone.now()

        goal.save()

        return Response({
            'message': 'Progress updated',
            'goal': UserGoalSerializer(goal).data
        })

    @swagger_auto_schema(
        tags=['goals'],
        operation_summary='List active goals',
        operation_description='Returns only goals with status=active for the authenticated user.',
        responses={200: openapi.Response('Active goals', UserGoalSerializer(many=True))}
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active goals"""
        active_goals = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active_goals, many=True)
        return Response(serializer.data)


@method_decorator(name='list', decorator=swagger_auto_schema(
    tags=['messages'],
    operation_summary='List AI messages',
    operation_description='Returns all AI-generated messages for the authenticated user. Supports filtering by read status, favorite status, and message type.',
    manual_parameters=[
        openapi.Parameter('is_read', openapi.IN_QUERY, description='Filter by read status', type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('is_favorited', openapi.IN_QUERY, description='Filter by favorite status', type=openapi.TYPE_BOOLEAN, required=False),
        openapi.Parameter('message_type', openapi.IN_QUERY, description='Filter by message type', type=openapi.TYPE_STRING,
                          enum=['daily', 'goal_specific', 'scope_based', 'custom'], required=False),
    ],
    responses={200: openapi.Response('List of AI messages', AIMessageSerializer(many=True))}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    tags=['messages'],
    operation_summary='Retrieve a message',
    responses={
        200: openapi.Response('Message detail', AIMessageSerializer),
        404: 'Not found',
    }
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    tags=['messages'],
    operation_summary='Generate an AI message',
    operation_description='Generates a new AI motivational message. Returns HTTP 429 if the daily message limit is reached.',
    request_body=AIMessageCreateSerializer,
    responses={
        201: openapi.Response('AI message generated', AIMessageSerializer),
        400: 'No active subscription',
        429: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'error': openapi.Schema(type=openapi.TYPE_STRING),
                'messages_used': openapi.Schema(type=openapi.TYPE_INTEGER),
                'messages_limit': openapi.Schema(type=openapi.TYPE_INTEGER),
            }
        ),
    }
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    tags=['messages'],
    operation_summary='Update a message',
    responses={200: openapi.Response('Updated message', AIMessageSerializer)}
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    tags=['messages'],
    operation_summary='Partially update a message',
    responses={200: openapi.Response('Updated message', AIMessageSerializer)}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    tags=['messages'],
    operation_summary='Delete a message',
    responses={204: 'Deleted successfully'}
))
class AIMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AI-generated motivational messages

    list: Get user's messages
    retrieve: Get a specific message
    create: Generate a new AI message
    mark_read: Mark message as read
    favorite: Toggle favorite status
    rate: Rate a message
    """
    serializer_class = AIMessageSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def get_queryset(self):
        """Users can only see their own messages"""
        queryset = AIMessage.objects.filter(user=self.request.user).select_related(
            'scope', 'goal', 'subscription'
        )

        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')

        # Filter by favorited
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited is not None:
            queryset = queryset.filter(is_favorited=is_favorited.lower() == 'true')

        # Filter by message type
        message_type = self.request.query_params.get('message_type')
        if message_type:
            queryset = queryset.filter(message_type=message_type)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Generate a new AI motivational message
        """
        serializer = AIMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get user's active subscription
        active_subscription = Subscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).first()

        if not active_subscription:
            return Response(
                {'error': 'No active subscription found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check daily message limit
        today = timezone.now().date()
        messages_today = AIMessage.objects.filter(
            user=request.user,
            created_at__date=today
        ).count()

        if messages_today >= active_subscription.package.messages_per_day:
            return Response({
                'error': f'Daily message limit reached ({active_subscription.package.messages_per_day} messages per day)',
                'messages_used': messages_today,
                'messages_limit': active_subscription.package.messages_per_day
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Get scope and goal if provided
        scope = None
        goal = None

        if serializer.validated_data.get('scope_id'):
            try:
                scope = Scope.objects.get(id=serializer.validated_data['scope_id'])
            except Scope.DoesNotExist:
                pass

        if serializer.validated_data.get('goal_id'):
            try:
                goal = UserGoal.objects.get(
                    id=serializer.validated_data['goal_id'],
                    user=request.user
                )
                scope = goal.scope  # Use goal's scope
            except UserGoal.DoesNotExist:
                pass

        # Generate AI message
        try:
            ai_service = OpenAIService()
            ai_message = ai_service.generate_motivational_message(
                user=request.user,
                subscription=active_subscription,
                scope=scope,
                goal=goal,
                message_type=serializer.validated_data.get('message_type', 'daily'),
                custom_prompt=serializer.validated_data.get('custom_prompt')
            )

            return Response(
                AIMessageSerializer(ai_message).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({
                'error': 'Failed to generate AI message',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        tags=['messages'],
        operation_summary='Mark message as read',
        operation_description='Sets is_read to true for the specified message.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'ai_message': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
        }
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a message as read"""
        message = self.get_object()
        message.is_read = True
        message.save()

        return Response({
            'message': 'Marked as read',
            'ai_message': AIMessageSerializer(message).data
        })

    @swagger_auto_schema(
        tags=['messages'],
        operation_summary='Toggle message favorite',
        operation_description='Toggles the is_favorited flag on the specified message.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_favorited': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'ai_message': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
        }
    )
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status of a message"""
        message = self.get_object()
        message.is_favorited = not message.is_favorited
        message.save()

        return Response({
            'message': 'Favorite toggled',
            'is_favorited': message.is_favorited,
            'ai_message': AIMessageSerializer(message).data
        })

    @swagger_auto_schema(
        tags=['messages'],
        operation_summary='Rate a message',
        operation_description='Set a star rating (1–5) for the specified message.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['rating'],
            properties={
                'rating': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Rating value between 1 and 5',
                    minimum=1,
                    maximum=5,
                ),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'rating': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'ai_message': openapi.Schema(type=openapi.TYPE_OBJECT),
                }
            ),
            400: 'Rating must be between 1 and 5',
        }
    )
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate a message (1-5 stars)"""
        message = self.get_object()
        rating = request.data.get('rating')

        if rating is None or not (1 <= rating <= 5):
            return Response(
                {'error': 'Rating must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )

        message.user_rating = rating
        message.save()

        return Response({
            'message': 'Rating saved',
            'rating': rating,
            'ai_message': AIMessageSerializer(message).data
        })

    @swagger_auto_schema(
        tags=['messages'],
        operation_summary='Get today\'s daily message',
        operation_description='Retrieve today\'s daily message. Automatically generates one if it does not exist yet for today.',
        responses={
            200: openapi.Response('Daily message', AIMessageSerializer),
        }
    )
    @action(detail=False, methods=['get'])
    def daily(self, request):
        """Get today's daily message or generate a new one"""
        today = timezone.now().date()

        # Check if daily message already exists
        existing_message = AIMessage.objects.filter(
            user=request.user,
            message_type='daily',
            created_at__date=today
        ).first()

        if existing_message:
            return Response(AIMessageSerializer(existing_message).data)

        # Generate new daily message
        return self.create(request, message_type='daily')

    @swagger_auto_schema(
        tags=['messages'],
        operation_summary='List favorited messages',
        operation_description='Returns all messages where is_favorited is true for the authenticated user.',
        responses={200: openapi.Response('Favorited messages', AIMessageSerializer(many=True))}
    )
    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Get all favorited messages"""
        favorites = self.get_queryset().filter(is_favorited=True)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)


class PaymentWebhookView(APIView):
    """
    Webhook endpoint for Tap Payment callbacks
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=['payments'],
        operation_summary='Tap Payment webhook',
        operation_description='Receives payment status callbacks from the Tap Payment gateway. This endpoint is called by Tap, not by your application.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Tap Payment webhook payload (sent by Tap gateway)',
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'status': openapi.Schema(type=openapi.TYPE_STRING, example='success')}
            ),
            400: 'Payment processing failed',
        }
    )
    def post(self, request):
        """Handle payment webhook from Tap Payment gateway"""
        try:
            payment_service = TapPaymentService()
            success = payment_service.process_webhook(request.data)

            if success:
                return Response({'status': 'success'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': 'error',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentVerificationView(APIView):
    """
    Endpoint for verifying payment status
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=['payments'],
        operation_summary='Verify payment status',
        operation_description='Verify the status of a payment using the Tap Payment charge ID.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'charge_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'status': openapi.Schema(type=openapi.TYPE_STRING, description='Tap Payment charge status (e.g. CAPTURED)'),
                    'details': openapi.Schema(type=openapi.TYPE_OBJECT, description='Full Tap Payment charge object'),
                }
            ),
            400: 'Failed to verify payment',
        }
    )
    def get(self, request, charge_id):
        """Verify payment status with Tap Payment gateway"""
        try:
            payment_service = TapPaymentService()
            payment_status = payment_service.verify_payment(charge_id)

            return Response({
                'charge_id': charge_id,
                'status': payment_status.get('status'),
                'details': payment_status
            })

        except Exception as e:
            return Response({
                'error': 'Failed to verify payment',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class DashboardStatsView(APIView):
    """
    Get user dashboard statistics
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=['dashboard'],
        operation_summary='Get dashboard statistics',
        operation_description='Returns aggregated statistics for the authenticated user\'s subscription, goals, and messages.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'subscription': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            'package_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'end_date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                            'messages_per_day': openapi.Schema(type=openapi.TYPE_INTEGER),
                        }
                    ),
                    'goals': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'active': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'completed': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'completion_rate': openapi.Schema(type=openapi.TYPE_NUMBER, description='Percentage 0-100'),
                        }
                    ),
                    'messages': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'unread': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'favorited': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'this_week': openapi.Schema(type=openapi.TYPE_INTEGER),
                        }
                    ),
                }
            ),
        }
    )
    def get(self, request):
        """Return user's dashboard stats"""
        user = request.user

        # Active subscription
        active_subscription = Subscription.objects.filter(
            user=user,
            status='active',
            end_date__gt=timezone.now()
        ).first()

        # Goal stats
        total_goals = UserGoal.objects.filter(user=user).count()
        completed_goals = UserGoal.objects.filter(user=user, status='completed').count()
        active_goals = UserGoal.objects.filter(user=user, status='active').count()

        # Message stats
        total_messages = AIMessage.objects.filter(user=user).count()
        unread_messages = AIMessage.objects.filter(user=user, is_read=False).count()
        favorited_messages = AIMessage.objects.filter(user=user, is_favorited=True).count()

        # Messages this week
        week_ago = timezone.now() - timedelta(days=7)
        messages_this_week = AIMessage.objects.filter(
            user=user,
            created_at__gte=week_ago
        ).count()

        return Response({
            'subscription': {
                'is_active': active_subscription is not None,
                'package_name': active_subscription.package.name if active_subscription else None,
                'end_date': active_subscription.end_date if active_subscription else None,
                'messages_per_day': active_subscription.package.messages_per_day if active_subscription else 0,
            },
            'goals': {
                'total': total_goals,
                'active': active_goals,
                'completed': completed_goals,
                'completion_rate': (completed_goals / total_goals * 100) if total_goals > 0 else 0
            },
            'messages': {
                'total': total_messages,
                'unread': unread_messages,
                'favorited': favorited_messages,
                'this_week': messages_this_week
            }
        })


class ScopeManagementView(APIView):
    """
    API endpoints for scope and permission management
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=['scopes'],
        operation_summary='Get user scopes and permissions',
        operation_description='Returns the authenticated user\'s current scopes, permissions, and feature access.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description='User scope and permission information',
            ),
        }
    )
    def get(self, request):
        """Get user's current scopes and permissions"""
        scope_info = ScopeManager.get_user_scope_info(request.user)
        return Response(scope_info)

    @swagger_auto_schema(
        tags=['scopes'],
        operation_summary='Check scope/permission access',
        operation_description='Check whether the authenticated user has access to specific scopes, permissions, or features.',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'scopes': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description='List of scopes to check access for',
                ),
                'permissions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description='List of permissions to check',
                ),
                'feature': openapi.Schema(type=openapi.TYPE_STRING, description='Feature name to check access for'),
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description='Access check results for requested scopes, permissions, and feature',
            ),
        }
    )
    def post(self, request):
        """Check if user has access to specific scopes or permissions"""
        scopes = request.data.get('scopes', [])
        permissions = request.data.get('permissions', [])
        feature = request.data.get('feature')

        result = {}

        if scopes:
            result['scope_check'] = ScopeManager.validate_scope_request(request.user, scopes)

        if permissions:
            result['permission_check'] = ScopeManager.validate_permission_request(request.user, permissions)

        if feature:
            result['feature_check'] = ScopeManager.get_feature_access_info(request.user, feature)

        return Response(result)


class FeatureTestView(APIView):
    """
    Test endpoints for different feature access levels
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=['features'],
        operation_summary='Test basic_profile feature access',
        operation_description='Tests access to the basic_profile feature. Available to all authenticated users.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'feature': openapi.Schema(type=openapi.TYPE_STRING),
                    'user_role': openapi.Schema(type=openapi.TYPE_STRING),
                }
            ),
            403: 'Feature access denied',
        }
    )
    @require_feature('basic_profile')
    def get(self, request):
        """Basic feature - available to all authenticated users"""
        return Response({
            'message': 'Basic feature accessed successfully',
            'feature': 'basic_profile',
            'user_role': request.user.role,
        })

    @swagger_auto_schema(
        tags=['features'],
        operation_summary='Test trial_features access',
        operation_description='Tests access to the trial_features feature. Requires an active free trial.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'feature': openapi.Schema(type=openapi.TYPE_STRING),
                    'trial_remaining_days': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            ),
            403: 'Feature access denied - active trial required',
        }
    )
    @require_feature('trial_features')
    def post(self, request):
        """Trial feature - requires active trial"""
        return Response({
            'message': 'Trial feature accessed successfully',
            'feature': 'trial_features',
            'trial_remaining_days': request.user.trial_remaining_days,
        })

    @swagger_auto_schema(
        tags=['features'],
        operation_summary='Test subscriber_features access',
        operation_description='Tests access to the subscriber_features feature. Requires an active subscription.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'feature': openapi.Schema(type=openapi.TYPE_STRING),
                    'active_subscriptions': openapi.Schema(type=openapi.TYPE_INTEGER),
                }
            ),
            403: 'Feature access denied - active subscription required',
        }
    )
    @require_feature('subscriber_features')
    def patch(self, request):
        """Subscriber feature - requires active subscription"""
        return Response({
            'message': 'Subscriber feature accessed successfully',
            'feature': 'subscriber_features',
            'active_subscriptions': request.user.subscriptions.filter(
                status='active',
                end_date__gt=timezone.now()
            ).count(),
        })

    @swagger_auto_schema(
        tags=['features'],
        operation_summary='Test custom_goals feature access',
        operation_description='Tests access to the custom_goals feature. Requires an active subscription with custom_goals_enabled.',
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'feature': openapi.Schema(type=openapi.TYPE_STRING),
                    'has_custom_goals_access': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                }
            ),
            403: 'Feature access denied - subscription with custom goals required',
        }
    )
    @require_feature('custom_goals')
    def delete(self, request):
        """Custom goals feature - requires subscription with custom goals"""
        return Response({
            'message': 'Custom goals feature accessed successfully',
            'feature': 'custom_goals',
            'has_custom_goals_access': request.user.subscriptions.filter(
                status='active',
                end_date__gt=timezone.now(),
                package__custom_goals_enabled=True
            ).exists(),
        })
