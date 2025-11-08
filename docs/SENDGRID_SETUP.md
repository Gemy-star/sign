# SendGrid Email Configuration Guide

This guide explains how to configure and use SendGrid for email delivery in the Sign SA application.

## Overview

The application uses SendGrid as the email delivery service in production, configured through Django's SMTP backend and managed via Django Constance for dynamic settings.

## Configuration

### 1. Environment Variables

Set the following environment variable in your production environment:

```bash
export SENDGRID_API_KEY="your_sendgrid_api_key_here"
export EMAIL_FROM_ADDRESS="noreply@sign-sa.net"
export SERVER_EMAIL="admin@sign-sa.net"
```

### 2. Django Constance Settings

The following settings are managed through Django Constance and can be updated via the Django admin panel at `/admin/constance/config/`:

- **SENDGRID_API_KEY**: Your SendGrid API key
- **EMAIL_FROM_ADDRESS**: Default sender email address (e.g., `noreply@sign-sa.net`)
- **EMAIL_FROM_NAME**: Friendly name for the sender (e.g., `Sign SA`)

### 3. Production Settings

The production settings (`core/settings/production.py`) are pre-configured to use SendGrid:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # This is literally the string 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', '')
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_FROM_ADDRESS', 'noreply@sign-sa.net')
```

## Getting a SendGrid API Key

1. Sign up for a SendGrid account at https://sendgrid.com/
2. Verify your sender email address or domain
3. Go to Settings → API Keys
4. Create a new API key with "Mail Send" permissions
5. Copy the API key (you'll only see it once)
6. Add it to your environment variables

## Domain Verification

For production use, you should verify your sending domain with SendGrid:

1. Go to Settings → Sender Authentication in SendGrid
2. Click "Verify a Single Sender" or "Authenticate Your Domain"
3. Follow the DNS setup instructions
4. Wait for DNS propagation (can take up to 48 hours)

## Using Email Utilities

The application provides helper functions in `api/email_utils.py`:

### Send a Simple Email

```python
from api.email_utils import send_notification_email

send_notification_email(
    subject="Test Email",
    message="This is a test email.",
    recipient_list=["user@example.com"],
    html_message="<p>This is a <strong>test</strong> email.</p>"
)
```

### Send an HTML Email

```python
from api.email_utils import send_html_email

send_html_email(
    subject="Welcome!",
    text_content="Welcome to Sign SA!",
    html_content="<h1>Welcome to Sign SA!</h1>",
    recipient_list=["user@example.com"]
)
```

### Send Welcome Email

```python
from api.email_utils import send_welcome_email

# Automatically sends a welcome email to the user
send_welcome_email(user)
```

### Send Subscription Notification

```python
from api.email_utils import send_subscription_notification

# Send notification about subscription status
send_subscription_notification(subscription, status='activated')
# Options: 'activated', 'expired', 'cancelled'
```

## Testing Email Locally

In local development (`core/settings/local.py`), emails are sent to the console instead of SendGrid:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

To test with actual SendGrid in development:

1. Set `SENDGRID_API_KEY` in your environment
2. Temporarily change the email backend in `local.py`:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.sendgrid.net'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'apikey'
   EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', '')
   ```

## Testing Email Sending

Test email functionality from Django shell:

```bash
poetry run python manage.py shell
```

```python
from django.core.mail import send_mail
from constance import config

send_mail(
    subject='Test Email',
    message='This is a test email from Django.',
    from_email=config.EMAIL_FROM_ADDRESS,
    recipient_list=['your-email@example.com'],
    fail_silently=False,
)
```

## Monitoring and Analytics

SendGrid provides detailed analytics:

1. Log in to your SendGrid dashboard
2. Go to Activity to see email delivery status
3. Check Stats for delivery rates, opens, clicks, etc.
4. Set up Email Activity Feed for detailed logs

## Best Practices

### 1. Sender Reputation
- Use a verified domain
- Maintain a low bounce rate
- Handle unsubscribes properly
- Avoid spam triggers in content

### 2. Email Templates
- Use responsive HTML templates
- Always provide plain text alternative
- Test emails across different clients
- Keep file sizes small

### 3. Error Handling
```python
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
import logging

logger = logging.getLogger(__name__)

try:
    send_mail(...)
except BadHeaderError:
    logger.error("Invalid header found in email")
except Exception as e:
    logger.error(f"Error sending email: {str(e)}")
```

### 4. Rate Limiting
SendGrid has rate limits based on your plan:
- Free: 100 emails/day
- Essentials: 100,000 emails/month
- Pro: Higher limits

Monitor your usage in the SendGrid dashboard.

## Troubleshooting

### Emails Not Sending

1. Check SendGrid API key is correct
2. Verify sender email is authenticated
3. Check Django logs for errors
4. Review SendGrid Activity feed

### Emails Going to Spam

1. Verify your domain with SendGrid
2. Set up SPF and DKIM records
3. Avoid spam trigger words
4. Include unsubscribe links
5. Maintain good sender reputation

### Common Errors

**Authentication Failed**
- Check `EMAIL_HOST_USER` is set to `'apikey'` (literal string)
- Verify `SENDGRID_API_KEY` is correct

**Connection Timeout**
- Check firewall allows outbound SMTP (port 587)
- Verify network connectivity

**Invalid Sender**
- Ensure sender email is verified in SendGrid
- Use domain authentication for production

## Email Templates Location

HTML email templates should be stored in `templates/emails/`:

```
templates/
  emails/
    base.html
    welcome.html
    subscription_activated.html
    subscription_expired.html
```

Example template structure:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    {% block content %}{% endblock %}
</body>
</html>
```

## Support

- SendGrid Documentation: https://docs.sendgrid.com/
- Django Email Documentation: https://docs.djangoproject.com/en/stable/topics/email/
- Sign SA Support: admin@sign-sa.net
