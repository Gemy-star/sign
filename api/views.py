from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta

from .models import (
    Scope, Package, Subscription, UserGoal,
    AIMessage, PaymentTransaction
)
from .serializers import (
    ScopeSerializer, PackageSerializer,
    SubscriptionListSerializer, SubscriptionDetailSerializer,
    SubscriptionCreateSerializer, UserGoalSerializer,
    AIMessageSerializer, AIMessageCreateSerializer,
    PaymentTransactionSerializer
)
from .services import OpenAIService, TapPaymentService
from .permissions import IsOwnerOrReadOnly, HasActiveSubscription


class ScopeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing scopes (life domains)

    list: Get all active scopes
    retrieve: Get a specific scope by ID
    """
    queryset = Scope.objects.filter(is_active=True)
    serializer_class = ScopeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Filter scopes by category if provided"""
        queryset = super().get_queryset()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all available scope categories"""
        categories = [
            {"value": cat[0], "label": cat[1]}
            for cat in Scope.SCOPE_CATEGORIES
        ]
        return Response(categories)


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

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured packages only"""
        packages = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(packages, many=True)
        return Response(serializer.data)

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

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active goals"""
        active_goals = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active_goals, many=True)
        return Response(serializer.data)


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
