from django.core.management.base import BaseCommand
from api.models import Scope, Package


class Command(BaseCommand):
    help = 'Seeds the database with initial scopes and packages'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Create Scopes
        scopes_data = [
            {
                'name': 'Emotional Intelligence',
                'category': 'mental',
                'description': 'Understanding and managing emotions and relationships',
                'icon': '🧠'
            },
            {
                'name': 'Mindset and Resilience',
                'category': 'mental',
                'description': 'Developing growth mindset, adaptability, and stress management',
                'icon': '💪'
            },
            {
                'name': 'Exercise and Fitness',
                'category': 'physical',
                'description': 'Building strength, endurance, and flexibility',
                'icon': '🏃'
            },
            {
                'name': 'Nutrition and Diet',
                'category': 'physical',
                'description': 'Eating mindfully for energy and longevity',
                'icon': '🥗'
            },
            {
                'name': 'Skill Building',
                'category': 'career',
                'description': 'Developing technical or leadership skills',
                'icon': '📚'
            },
            {
                'name': 'Productivity',
                'category': 'career',
                'description': 'Working efficiently and prioritizing effectively',
                'icon': '⚡'
            },
            {
                'name': 'Budgeting and Saving',
                'category': 'financial',
                'description': 'Managing income and expenses responsibly',
                'icon': '💰'
            },
            {
                'name': 'Investing',
                'category': 'financial',
                'description': 'Creating long-term financial security',
                'icon': '📈'
            },
            {
                'name': 'Family and Friendships',
                'category': 'relationships',
                'description': 'Nurturing meaningful and supportive relationships',
                'icon': '❤️'
            },
            {
                'name': 'Communication',
                'category': 'relationships',
                'description': 'Enhancing interpersonal connections',
                'icon': '💬'
            },
            {
                'name': 'Mindfulness',
                'category': 'spiritual',
                'description': 'Cultivating presence and peace',
                'icon': '🕊️'
            },
            {
                'name': 'Purpose and Meaning',
                'category': 'spiritual',
                'description': 'Discovering values and direction in life',
                'icon': '✨'
            },
            {
                'name': 'Continuous Learning',
                'category': 'creativity',
                'description': 'Pursuing new knowledge and hobbies',
                'icon': '🎨'
            },
            {
                'name': 'Creative Expression',
                'category': 'creativity',
                'description': 'Engaging in art, music, writing, or innovation',
                'icon': '🎭'
            },
            {
                'name': 'Work-Life Balance',
                'category': 'lifestyle',
                'description': 'Aligning daily routines with personal priorities',
                'icon': '⚖️'
            },
            {
                'name': 'Organization',
                'category': 'lifestyle',
                'description': 'Simplifying space and commitments',
                'icon': '🗂️'
            },
        ]

        created_scopes = 0
        for scope_data in scopes_data:
            scope, created = Scope.objects.get_or_create(
                name=scope_data['name'],
                defaults=scope_data
            )
            if created:
                created_scopes += 1
                self.stdout.write(f'  Created scope: {scope.name}')

        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_scopes} scopes'))

        # Create Packages
        packages_data = [
            {
                'name': 'Starter',
                'description': 'Perfect for beginners starting their personal development journey',
                'price': 9.99,
                'duration': 'monthly',
                'duration_days': 30,
                'max_scopes': 2,
                'messages_per_day': 1,
                'custom_goals_enabled': False,
                'priority_support': False,
                'is_featured': False,
                'display_order': 1
            },
            {
                'name': 'Growth',
                'description': 'For committed individuals ready to accelerate their growth',
                'price': 24.99,
                'duration': 'monthly',
                'duration_days': 30,
                'max_scopes': 5,
                'messages_per_day': 3,
                'custom_goals_enabled': True,
                'priority_support': False,
                'is_featured': True,
                'display_order': 2
            },
            {
                'name': 'Elite',
                'description': 'Premium experience with unlimited access and priority support',
                'price': 49.99,
                'duration': 'monthly',
                'duration_days': 30,
                'max_scopes': 10,
                'messages_per_day': 10,
                'custom_goals_enabled': True,
                'priority_support': True,
                'is_featured': True,
                'display_order': 3
            },
            {
                'name': 'Growth Annual',
                'description': 'Annual Growth plan with 20% discount',
                'price': 239.99,
                'duration': 'yearly',
                'duration_days': 365,
                'max_scopes': 5,
                'messages_per_day': 3,
                'custom_goals_enabled': True,
                'priority_support': False,
                'is_featured': False,
                'display_order': 4
            },
            {
                'name': 'Elite Annual',
                'description': 'Annual Elite plan with 25% discount',
                'price': 449.99,
                'duration': 'yearly',
                'duration_days': 365,
                'max_scopes': 10,
                'messages_per_day': 10,
                'custom_goals_enabled': True,
                'priority_support': True,
                'is_featured': False,
                'display_order': 5
            },
        ]

        created_packages = 0
        for package_data in packages_data:
            package, created = Package.objects.get_or_create(
                name=package_data['name'],
                defaults=package_data
            )
            if created:
                created_packages += 1
                self.stdout.write(f'  Created package: {package.name} - ${package.price}')

        self.stdout.write(self.style.SUCCESS(f'✓ Created {created_packages} packages'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Database seeding completed successfully!'))
