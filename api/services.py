import time
import openai
from constance import config
from .models import AIMessage, Scope, UserGoal, Subscription


class OpenAIService:
    """Service for generating motivational content using OpenAI ChatGPT"""

    def __init__(self):
        """Initialize OpenAI client with API key from django-constance"""
        # Use django-constance for dynamic configuration
        self.api_key = config.OPENAI_API_KEY
        if self.api_key:
            openai.api_key = self.api_key
        self.default_model = config.OPENAI_MODEL
        self.max_tokens = config.OPENAI_MAX_TOKENS
        self.temperature = config.OPENAI_TEMPERATURE

    def generate_motivational_message(
        self,
        user,
        subscription,
        scope=None,
        goal=None,
        message_type='daily',
        custom_prompt=None
    ):
        """
        Generate a motivational message based on user's scope and goals

        Args:
            user: User instance
            subscription: Subscription instance
            scope: Scope instance (optional)
            goal: UserGoal instance (optional)
            message_type: Type of message to generate
            custom_prompt: Additional user-provided context

        Returns:
            AIMessage instance
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        # Build the prompt based on context
        prompt = self._build_prompt(
            user=user,
            scope=scope,
            goal=goal,
            message_type=message_type,
            custom_prompt=custom_prompt
        )

        # Generate message using OpenAI
        start_time = time.time()
        try:
            response = openai.ChatCompletion.create(
                model=self.default_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional life coach and motivational speaker. "
                            "Your role is to provide personalized, inspiring, and actionable "
                            "motivational messages to help people achieve their personal development goals. "
                            "Be empathetic, encouraging, and specific in your advice."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            content = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens
            generation_time = time.time() - start_time

            # Create and save AI message
            ai_message = AIMessage.objects.create(
                user=user,
                subscription=subscription,
                scope=scope,
                goal=goal,
                message_type=message_type,
                prompt_used=prompt,
                content=content,
                ai_model=self.default_model,
                tokens_used=tokens_used,
                generation_time=generation_time
            )

            return ai_message

        except Exception as e:
            raise Exception(f"Failed to generate AI message: {str(e)}")

    def _build_prompt(self, user, scope=None, goal=None, message_type='daily', custom_prompt=None):
        """
        Build a contextual prompt for the AI based on user data

        Args:
            user: User instance
            scope: Scope instance
            goal: UserGoal instance
            message_type: Type of message
            custom_prompt: Additional context

        Returns:
            str: Formatted prompt
        """
        prompt_parts = []

        # Personalization
        if user.first_name:
            prompt_parts.append(f"Create a motivational message for {user.first_name}.")
        else:
            prompt_parts.append("Create a motivational message.")

        # Message type context
        if message_type == 'daily':
            prompt_parts.append("This is their daily motivation to start the day with purpose and energy.")
        elif message_type == 'goal_specific':
            prompt_parts.append("This message should specifically support their current goal.")
        elif message_type == 'scope_based':
            prompt_parts.append("This message should focus on a specific area of personal development.")

        # Scope context
        if scope:
            prompt_parts.append(
                f"\nFocus Area: {scope.name} ({scope.get_category_display()})"
            )
            prompt_parts.append(f"Context: {scope.description}")

        # Goal context
        if goal:
            goal_context = f"\nCurrent Goal: {goal.title}"
            if goal.description:
                goal_context += f"\nGoal Details: {goal.description}"
            if goal.target_date:
                goal_context += f"\nTarget Date: {goal.target_date}"
            goal_context += f"\nProgress: {goal.progress_percentage}%"
            prompt_parts.append(goal_context)

        # Custom user input
        if custom_prompt:
            prompt_parts.append(f"\nAdditional Context: {custom_prompt}")

        # Instructions
        prompt_parts.append(
            "\nProvide a motivational message that is:"
            "\n- Personalized and specific to the context above"
            "\n- Actionable with practical advice"
            "\n- Encouraging and empowering"
            "\n- 3-5 sentences long"
            "\n- Written in a warm, supportive tone"
        )

        return "\n".join(prompt_parts)

    def generate_scope_based_message(self, user, subscription, scope):
        """Generate a message focused on a specific scope"""
        return self.generate_motivational_message(
            user=user,
            subscription=subscription,
            scope=scope,
            message_type='scope_based'
        )

    def generate_goal_based_message(self, user, subscription, goal):
        """Generate a message focused on a specific goal"""
        return self.generate_motivational_message(
            user=user,
            subscription=subscription,
            scope=goal.scope,
            goal=goal,
            message_type='goal_specific'
        )

    def generate_daily_message(self, user, subscription):
        """
        Generate a daily motivational message based on user's active scopes

        This will randomly select from the user's selected scopes to provide variety
        """
        import random

        # Get user's selected scopes
        scopes = subscription.selected_scopes.filter(is_active=True)

        if scopes.exists():
            # Pick a random scope for variety
            scope = random.choice(scopes)
        else:
            scope = None

        return self.generate_motivational_message(
            user=user,
            subscription=subscription,
            scope=scope,
            message_type='daily'
        )


class TapPaymentService:
    """Service for handling Tap Payment gateway integration"""

    def __init__(self):
        """Initialize Tap Payment with credentials from django-constance"""
        # Use django-constance for dynamic configuration
        self.api_key = config.TAP_API_KEY
        self.secret_key = config.TAP_SECRET_KEY
        self.base_url = config.TAP_BASE_URL

    def create_charge(self, subscription, user, redirect_url=None, post_url=None):
        """
        Create a payment charge for a subscription

        Args:
            subscription: Subscription instance
            user: User instance
            redirect_url: URL to redirect after payment
            post_url: Webhook URL for payment confirmation

        Returns:
            dict: Payment response with charge_id and payment URL
        """
        import requests

        if not self.api_key:
            raise ValueError("Tap Payment API key not configured")

        # Prepare payment payload
        payload = {
            "amount": float(subscription.package.price),
            "currency": "USD",
            "threeDSecure": True,
            "save_card": False,
            "description": f"Subscription: {subscription.package.name}",
            "statement_descriptor": "Motivational App Subscription",
            "metadata": {
                "subscription_id": subscription.id,
                "user_id": user.id,
                "package_id": subscription.package.id,
            },
            "reference": {
                "transaction": f"SUB-{subscription.id}",
                "order": f"ORD-{subscription.id}-{int(time.time())}"
            },
            "receipt": {
                "email": True,
                "sms": False
            },
            "customer": {
                "first_name": user.first_name or user.username,
                "last_name": user.last_name or "",
                "email": user.email,
            },
            "source": {
                "id": "src_card"
            },
            "post": {
                "url": post_url or f"{config.SITE_URL}/api/payments/webhook/"
            },
            "redirect": {
                "url": redirect_url or f"{config.SITE_URL}/subscription/success/"
            }
        }

        # Make API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{self.base_url}/charges",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Tap Payment API error: {str(e)}")

    def verify_payment(self, charge_id):
        """
        Verify payment status with Tap Payment gateway

        Args:
            charge_id: Tap charge ID

        Returns:
            dict: Payment status information
        """
        import requests

        if not self.api_key:
            raise ValueError("Tap Payment API key not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            response = requests.get(
                f"{self.base_url}/charges/{charge_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to verify payment: {str(e)}")

    def process_webhook(self, webhook_data):
        """
        Process webhook callback from Tap Payment

        Args:
            webhook_data: Webhook payload from Tap

        Returns:
            bool: Success status
        """
        from .models import PaymentTransaction

        try:
            charge_id = webhook_data.get('id')
            status = webhook_data.get('status')

            # Find the transaction
            transaction = PaymentTransaction.objects.get(tap_charge_id=charge_id)

            if status == 'CAPTURED':
                transaction.status = 'completed'
                transaction.completed_at = time.timezone.now()

                # Activate subscription
                subscription = transaction.subscription
                subscription.activate()
                subscription.payment_id = charge_id
                subscription.amount_paid = transaction.amount
                subscription.payment_method = webhook_data.get('source', {}).get('payment_method')
                subscription.save()

            elif status == 'FAILED':
                transaction.status = 'failed'
                transaction.error_message = webhook_data.get('response', {}).get('message', 'Payment failed')
                transaction.subscription.status = 'failed'
                transaction.subscription.save()

            transaction.raw_response = webhook_data
            transaction.save()

            return True

        except PaymentTransaction.DoesNotExist:
            return False
        except Exception as e:
            print(f"Webhook processing error: {str(e)}")
            return False
