from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import CustomUser


class Command(BaseCommand):
    help = 'Create users with different roles (admin, subscriber, normal)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['admin', 'subscriber', 'normal'],
            required=True,
            help='Type of user to create'
        )
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username for the user'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email for the user'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='',
            help='First name for the user'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='',
            help='Last name for the user'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123456',
            help='Password for the user (default: admin123456)'
        )
        parser.add_argument(
            '--start-trial',
            action='store_true',
            help='Start free trial for normal users and subscribers'
        )
        parser.add_argument(
            '--trial-days',
            type=int,
            default=7,
            help='Number of days for trial (default: 7)'
        )
        parser.add_argument(
            '--batch',
            type=int,
            help='Create multiple users with sequential usernames'
        )

    def handle(self, *args, **options):
        user_type = options['type']
        base_username = options['username']
        email = options['email']
        first_name = options['first_name']
        last_name = options['last_name']
        password = options['password']
        start_trial = options['start_trial']
        trial_days = options['trial_days']
        batch_count = options.get('batch')

        if batch_count:
            self.create_batch_users(
                user_type, base_username, email, first_name, last_name,
                password, start_trial, trial_days, batch_count
            )
        else:
            self.create_single_user(
                user_type, base_username, email, first_name, last_name,
                password, start_trial, trial_days
            )

    def create_single_user(self, user_type, username, email, first_name, last_name,
                          password, start_trial, trial_days):
        """Create a single user"""
        try:
            with transaction.atomic():
                # Check if user already exists
                if CustomUser.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User "{username}" already exists')
                    )
                    return

                if CustomUser.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Email "{email}" already exists')
                    )
                    return

                # Create user
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )

                # Set role
                if user_type == 'admin':
                    user.role = 'admin'
                    user.is_staff = True
                    user.is_superuser = True
                elif user_type == 'subscriber':
                    user.role = 'subscriber'
                else:  # normal user
                    user.role = 'normal'

                user.save()

                # Start trial if requested and user is normal or subscriber
                if start_trial and user.role in ['normal', 'subscriber']:
                    success, message = user.start_free_trial(trial_days)
                    if success:
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Trial started: {message}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⚠ Trial not started: {message}')
                        )

                # Display user info
                self.display_user_info(user, user_type, start_trial)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating user: {str(e)}')
            )

    def create_batch_users(self, user_type, base_username, email, first_name, last_name,
                          password, start_trial, trial_days, batch_count):
        """Create multiple users in batch"""
        self.stdout.write(f'Creating {batch_count} {user_type} users...')

        for i in range(1, batch_count + 1):
            username = f"{base_username}{i:03d}" if batch_count > 1 else base_username
            batch_email = email.replace('@', f'{i}@') if '@' in email else f"{email}{i}@example.com"

            self.create_single_user(
                user_type, username, batch_email, first_name, last_name,
                password, start_trial, trial_days
            )

    def display_user_info(self, user, user_type, start_trial):
        """Display created user information"""
        info = [
            f'✓ {user_type.title()} user created:',
            f'  Username: {user.username}',
            f'  Email: {user.email}',
            f'  Role: {user.role}',
            f'  Password: admin123456',
        ]

        if user.first_name or user.last_name:
            info.append(f'  Name: {user.first_name} {user.last_name}'.strip())

        if start_trial and user.role == 'subscriber':
            info.append(f'  Trial: {user.trial_remaining_days} days remaining')

        self.stdout.write(self.style.SUCCESS('\n'.join(info)))

    def create_sample_users(self):
        """Create sample users for testing"""
        sample_configs = [
            {
                'type': 'admin',
                'username': 'admin',
                'email': 'admin@example.com',
                'first_name': 'Super',
                'last_name': 'Admin',
                'start_trial': False
            },
            {
                'type': 'subscriber',
                'username': 'subscriber1',
                'email': 'subscriber1@example.com',
                'first_name': 'Test',
                'last_name': 'Subscriber',
                'start_trial': True
            },
            {
                'type': 'normal',
                'username': 'user1',
                'email': 'user1@example.com',
                'first_name': 'Normal',
                'last_name': 'User',
                'start_trial': False
            }
        ]

        self.stdout.write('Creating sample users...')
        for config in sample_configs:
            self.create_single_user(
                config['type'],
                config['username'],
                config['email'],
                config['first_name'],
                config['last_name'],
                'admin123456',
                config['start_trial'],
                7
            )
