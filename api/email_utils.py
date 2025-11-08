"""
Email utilities for sending emails using SendGrid via Django's email backend.
Uses Django Constance for dynamic configuration.
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from constance import config
from django.conf import settings


def get_from_email():
    """
    Get the from email address with optional friendly name.
    Uses Constance config for dynamic settings.
    """
    try:
        from_name = config.EMAIL_FROM_NAME
        from_address = config.EMAIL_FROM_ADDRESS
        return f'{from_name} <{from_address}>'
    except Exception:
        return settings.DEFAULT_FROM_EMAIL


def send_notification_email(subject, message, recipient_list, html_message=None):
    """
    Send a notification email using SendGrid.

    Args:
        subject (str): Email subject
        message (str): Plain text message
        recipient_list (list): List of recipient email addresses
        html_message (str, optional): HTML version of the message

    Returns:
        int: Number of emails sent successfully
    """
    from_email = get_from_email()

    return send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )


def send_html_email(subject, text_content, html_content, recipient_list, from_email=None):
    """
    Send an HTML email with plain text fallback.

    Args:
        subject (str): Email subject
        text_content (str): Plain text version
        html_content (str): HTML version
        recipient_list (list): List of recipient email addresses
        from_email (str, optional): From email address

    Returns:
        int: Number of emails sent successfully
    """
    if from_email is None:
        from_email = get_from_email()

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipient_list,
    )
    email.attach_alternative(html_content, "text/html")
    return email.send()


def send_welcome_email(user):
    """
    Send a welcome email to a new user.

    Args:
        user: User instance

    Returns:
        int: Number of emails sent successfully
    """
    subject = f'Welcome to {config.SITE_NAME}!'

    text_content = f"""
    Hi {user.username},

    Welcome to {config.SITE_NAME}!

    We're excited to have you on board.

    If you have any questions, feel free to contact us at {config.SUPPORT_EMAIL}.

    Best regards,
    The {config.SITE_NAME} Team
    """

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #4A90E2;">Welcome to {config.SITE_NAME}!</h2>
            <p>Hi <strong>{user.username}</strong>,</p>
            <p>We're excited to have you on board.</p>
            <p>If you have any questions, feel free to contact us at
               <a href="mailto:{config.SUPPORT_EMAIL}">{config.SUPPORT_EMAIL}</a>.
            </p>
            <p>Best regards,<br>
            The {config.SITE_NAME} Team</p>
        </body>
    </html>
    """

    return send_html_email(
        subject=subject,
        text_content=text_content,
        html_content=html_content,
        recipient_list=[user.email],
    )


def send_subscription_notification(subscription, status='activated'):
    """
    Send a subscription status notification email.

    Args:
        subscription: Subscription instance
        status (str): Status of the subscription (activated, expired, cancelled)

    Returns:
        int: Number of emails sent successfully
    """
    user = subscription.user
    package = subscription.package

    status_messages = {
        'activated': 'has been activated',
        'expired': 'has expired',
        'cancelled': 'has been cancelled',
    }

    subject = f'Your {package.name} Subscription {status_messages.get(status, "updated")}'

    text_content = f"""
    Hi {user.username},

    Your {package.name} subscription {status_messages.get(status, "has been updated")}.

    Subscription Details:
    - Package: {package.name}
    - Price: {package.price} {package.currency}
    - Duration: {package.duration_days} days

    For any questions, contact us at {config.SUPPORT_EMAIL}.

    Best regards,
    The {config.SITE_NAME} Team
    """

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #4A90E2;">Subscription {status.title()}</h2>
            <p>Hi <strong>{user.username}</strong>,</p>
            <p>Your <strong>{package.name}</strong> subscription {status_messages.get(status, "has been updated")}.</p>

            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Subscription Details:</h3>
                <ul style="list-style: none; padding: 0;">
                    <li><strong>Package:</strong> {package.name}</li>
                    <li><strong>Price:</strong> {package.price} {package.currency}</li>
                    <li><strong>Duration:</strong> {package.duration_days} days</li>
                </ul>
            </div>

            <p>For any questions, contact us at
               <a href="mailto:{config.SUPPORT_EMAIL}">{config.SUPPORT_EMAIL}</a>.
            </p>
            <p>Best regards,<br>
            The {config.SITE_NAME} Team</p>
        </body>
    </html>
    """

    return send_html_email(
        subject=subject,
        text_content=text_content,
        html_content=html_content,
        recipient_list=[user.email],
    )
