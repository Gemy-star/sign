"""
Utilities for managing user scopes and permissions
"""

from django.utils import timezone
from datetime import timedelta


class ScopeManager:
    """Manager class for handling user scopes and permissions"""

    # Define available scopes
    AVAILABLE_SCOPES = {
        'admin': 'Full administrative access',
        'user_management': 'Manage other users',
        'trial_management': 'Manage user trials',
        'subscriber': 'Subscriber features',
        'trial': 'Trial features',
        'custom_goals': 'Create custom goals',
        'priority_support': 'Priority customer support',
        'basic_access': 'Basic authenticated access',
        'profile': 'Profile management',
        'all_content': 'Access to all content',
    }

    # Define available permissions
    AVAILABLE_PERMISSIONS = {
        'create_users': 'Create new users',
        'delete_users': 'Delete users',
        'manage_trials': 'Manage user trials',
        'view_all_users': 'View all users',
        'manage_subscriptions': 'Manage subscriptions',
        'view_profile': 'View own profile',
        'update_profile': 'Update own profile',
        'create_goals': 'Create goals',
        'view_own_subscriptions': 'View own subscriptions',
        'manage_own_goals': 'Manage own goals',
        'trial_access': 'Access trial features',
        'limited_features': 'Access limited features',
        'create_custom_goals': 'Create custom goals',
        'priority_support': 'Get priority support',
        'multiple_messages': 'Send multiple messages per day',
    }

    @staticmethod
    def get_user_scope_info(user):
        """Get comprehensive scope information for a user"""
        return {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'scopes': user.get_user_scopes(),
            'permissions': user.get_user_permissions(),
            'has_active_trial': user.has_active_trial,
            'trial_remaining_days': user.trial_remaining_days,
            'active_subscriptions': user.subscriptions.filter(
                status='active',
                end_date__gt=timezone.now()
            ).count(),
            'last_updated': timezone.now(),
        }

    @staticmethod
    def validate_scope_request(user, required_scopes):
        """Validate if user has required scopes and return detailed info"""
        user_scopes = user.get_user_scopes()
        missing_scopes = [scope for scope in required_scopes if scope not in user_scopes]

        return {
            'has_access': len(missing_scopes) == 0,
            'user_scopes': user_scopes,
            'required_scopes': required_scopes,
            'missing_scopes': missing_scopes,
            'user_role': user.role,
            'has_active_trial': user.has_active_trial,
            'trial_remaining_days': user.trial_remaining_days,
        }

    @staticmethod
    def validate_permission_request(user, required_permissions):
        """Validate if user has required permissions and return detailed info"""
        user_permissions = user.get_user_permissions()
        missing_permissions = [perm for perm in required_permissions if perm not in user_permissions]

        return {
            'has_access': len(missing_permissions) == 0,
            'user_permissions': user_permissions,
            'required_permissions': required_permissions,
            'missing_permissions': missing_permissions,
            'user_role': user.role,
        }

    @staticmethod
    def get_feature_access_info(user, feature):
        """Get detailed feature access information"""
        can_access = user.can_access_feature(feature)

        # Determine why user can or cannot access
        reason = "Unknown"
        upgrade_options = []

        if user.is_admin:
            reason = "Admin has access to all features"
        elif feature in ['basic_profile', 'view_content']:
            reason = "Basic feature available to all users"
        elif feature == 'trial_features' and user.has_active_trial:
            reason = "Active trial provides access"
        elif feature == 'trial_features' and not user.has_active_trial:
            reason = "No active trial"
            if not user.has_used_trial:
                upgrade_options.append("Start free trial")
        elif feature == 'subscriber_features':
            if user.is_subscriber:
                active_subs = user.subscriptions.filter(
                    status='active',
                    end_date__gt=timezone.now()
                )
                if active_subs.exists():
                    reason = "Active subscription provides access"
                else:
                    reason = "Subscription expired or inactive"
                    upgrade_options.append("Renew subscription")
            else:
                reason = "Not a subscriber"
                upgrade_options.append("Subscribe to a plan")
        elif feature == 'custom_goals':
            custom_goal_subs = user.subscriptions.filter(
                status='active',
                end_date__gt=timezone.now(),
                package__custom_goals_enabled=True
            )
            if custom_goal_subs.exists():
                reason = "Subscription includes custom goals"
            else:
                reason = "Current plan doesn't include custom goals"
                upgrade_options.append("Upgrade to plan with custom goals")

        return {
            'can_access': can_access,
            'feature': feature,
            'reason': reason,
            'upgrade_options': upgrade_options,
            'user_role': user.role,
            'has_active_trial': user.has_active_trial,
            'trial_remaining_days': user.trial_remaining_days,
        }

    @staticmethod
    def get_subscription_recommendations(user):
        """Get subscription recommendations based on user's current status"""
        recommendations = []

        if user.is_normal:
            if not user.has_used_trial:
                recommendations.append({
                    'type': 'trial',
                    'title': 'Start Your Free Trial',
                    'description': 'Try all premium features for 7 days',
                    'action': 'start_trial'
                })
            else:
                recommendations.append({
                    'type': 'subscription',
                    'title': 'Subscribe to Unlock Features',
                    'description': 'Get unlimited access to all features',
                    'action': 'view_plans'
                })

        if user.is_subscriber:
            # Check if user has basic plan
            active_sub = user.subscriptions.filter(
                status='active',
                end_date__gt=timezone.now()
            ).first()

            if active_sub and not active_sub.package.custom_goals_enabled:
                recommendations.append({
                    'type': 'upgrade',
                    'title': 'Upgrade for Custom Goals',
                    'description': 'Unlock custom goal creation and more',
                    'action': 'upgrade_plan'
                })

        return recommendations

    @staticmethod
    def get_access_summary(user):
        """Get comprehensive access summary for user"""
        return {
            'user_info': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'full_name': user.full_name,
            },
            'access_info': {
                'scopes': user.get_user_scopes(),
                'permissions': user.get_user_permissions(),
                'has_active_trial': user.has_active_trial,
                'trial_remaining_days': user.trial_remaining_days,
            },
            'subscription_info': {
                'active_subscriptions': user.subscriptions.filter(
                    status='active',
                    end_date__gt=timezone.now()
                ).count(),
                'has_used_trial': user.has_used_trial,
                'can_start_trial': not user.has_used_trial,
            },
            'recommendations': ScopeManager.get_subscription_recommendations(user),
            'last_updated': timezone.now(),
        }
