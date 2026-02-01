"""
Management command to test SendGrid email configuration.
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from constance import config
import os


class Command(BaseCommand):
    help = 'Test SendGrid email configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
            required=True,
        )

    def handle(self, *args, **options):
        recipient = options['to']

        self.stdout.write(self.style.WARNING('Testing SendGrid Email Configuration...'))
        self.stdout.write('')

        # Check configuration
        self.stdout.write('Checking configuration:')

        sendgrid_key = os.environ.get('SENDGRID_API_KEY', '')
        if sendgrid_key:
            self.stdout.write(self.style.SUCCESS(f'  ✓ SENDGRID_API_KEY is set (length: {len(sendgrid_key)})'))
        else:
            self.stdout.write(self.style.ERROR('  ✗ SENDGRID_API_KEY is not set'))
            self.stdout.write(self.style.WARNING('    Set it with: export SENDGRID_API_KEY="your_key_here"'))

        try:
            from_address = config.EMAIL_FROM_ADDRESS
            self.stdout.write(self.style.SUCCESS(f'  ✓ EMAIL_FROM_ADDRESS: {from_address}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ EMAIL_FROM_ADDRESS error: {e}'))
            from_address = 'noreply@sign-sa.net'

        try:
            from_name = config.EMAIL_FROM_NAME
            self.stdout.write(self.style.SUCCESS(f'  ✓ EMAIL_FROM_NAME: {from_name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ EMAIL_FROM_NAME error: {e}'))
            from_name = 'AiaY'

        self.stdout.write('')

        if not sendgrid_key:
            self.stdout.write(self.style.ERROR('Cannot send test email: SENDGRID_API_KEY is not set'))
            return

        # Send test email
        self.stdout.write(f'Sending test email to: {recipient}')

        subject = 'SendGrid Test Email from AiaY'

        text_message = f"""
Hello,

This is a test email from AiaY to verify SendGrid configuration.

If you're receiving this email, your SendGrid setup is working correctly!

Configuration Details:
- From Address: {from_address}
- From Name: {from_name}
- Site Name: {config.SITE_NAME}
- Support Email: {config.SUPPORT_EMAIL}

Best regards,
The AiaY Team
        """

        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
        <h1 style="margin: 0; font-size: 28px;">✉️ SendGrid Test Email</h1>
    </div>

    <div style="background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
        <p style="font-size: 16px; margin-bottom: 20px;">Hello,</p>

        <div style="background-color: white; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; margin-bottom: 20px;">
            <p style="margin: 0; font-size: 16px;">
                This is a test email from <strong>AiaY</strong> to verify SendGrid configuration.
            </p>
        </div>

        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <p style="margin: 0 0 10px 0; font-size: 18px; color: #2e7d32;">
                ✓ Success!
            </p>
            <p style="margin: 0; font-size: 14px; color: #555;">
                If you're receiving this email, your SendGrid setup is working correctly!
            </p>
        </div>

        <div style="background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <h3 style="margin-top: 0; color: #667eea;">Configuration Details:</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>From Address:</strong></td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{from_address}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>From Name:</strong></td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{from_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;"><strong>Site Name:</strong></td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">{config.SITE_NAME}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><strong>Support Email:</strong></td>
                    <td style="padding: 8px 0;">{config.SUPPORT_EMAIL}</td>
                </tr>
            </table>
        </div>

        <p style="font-size: 14px; color: #666; text-align: center; margin-top: 30px;">
            Best regards,<br>
            <strong>The AiaY Team</strong>
        </p>
    </div>

    <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #999;">
        <p>This is an automated test email from AiaY</p>
    </div>
</body>
</html>
        """

        try:
            num_sent = send_mail(
                subject=subject,
                message=text_message,
                from_email=f'{from_name} <{from_address}>',
                recipient_list=[recipient],
                html_message=html_message,
                fail_silently=False,
            )

            if num_sent > 0:
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('✓ Test email sent successfully!'))
                self.stdout.write(self.style.SUCCESS(f'  Check {recipient} for the test email'))
                self.stdout.write('')
                self.stdout.write('Note: It may take a few moments for the email to arrive.')
                self.stdout.write('Check spam folder if you don\'t see it in your inbox.')
            else:
                self.stdout.write(self.style.ERROR('✗ Email was not sent'))

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR(f'✗ Error sending email: {str(e)}'))
            self.stdout.write('')
            self.stdout.write('Common issues:')
            self.stdout.write('  1. Invalid SendGrid API key')
            self.stdout.write('  2. Sender email not verified in SendGrid')
            self.stdout.write('  3. Network/firewall blocking SMTP port 587')
            self.stdout.write('  4. SendGrid account suspended or limited')
