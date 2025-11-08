"""
Management command to set up cache infrastructure.

This command helps set up the necessary cache tables and checks Redis connectivity.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings


class Command(BaseCommand):
    help = 'Set up cache infrastructure and verify connectivity'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up cache infrastructure...'))

        # Get cache backend
        cache_backend = settings.CACHES['default']['BACKEND']
        self.stdout.write(f'Cache Backend: {cache_backend}')

        # Test cache connectivity
        try:
            cache.set('test_key', 'test_value', 30)
            value = cache.get('test_key')

            if value == 'test_value':
                self.stdout.write(self.style.SUCCESS('✓ Cache is working correctly'))
                cache.delete('test_key')
            else:
                self.stdout.write(self.style.ERROR('✗ Cache test failed'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Cache error: {e}'))

        # Check if using Redis
        if 'redis' in cache_backend.lower():
            self.stdout.write('\nRedis Configuration:')
            self.stdout.write(f"  Location: {settings.CACHES['default']['LOCATION']}")

            try:
                from django_redis import get_redis_connection
                redis_conn = get_redis_connection("default")

                # Get Redis info
                info = redis_conn.info()
                self.stdout.write(self.style.SUCCESS(f"  ✓ Redis Version: {info.get('redis_version', 'Unknown')}"))
                self.stdout.write(self.style.SUCCESS(f"  ✓ Connected Clients: {info.get('connected_clients', 'Unknown')}"))
                self.stdout.write(self.style.SUCCESS(f"  ✓ Used Memory: {info.get('used_memory_human', 'Unknown')}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Redis connection failed: {e}'))

        # Check if using database cache
        elif 'DatabaseCache' in cache_backend:
            self.stdout.write('\nDatabase Cache Configuration:')
            self.stdout.write(f"  Table: {settings.CACHES['default']['LOCATION']}")
            self.stdout.write(self.style.WARNING('\n  Run: python manage.py createcachetable'))

        # Check if using local memory cache
        elif 'LocMemCache' in cache_backend:
            self.stdout.write(self.style.SUCCESS('\n✓ Using local memory cache (development mode)'))

        # Dummy cache
        elif 'DummyCache' in cache_backend:
            self.stdout.write(self.style.WARNING('\n⚠ Using dummy cache (no caching)'))

        self.stdout.write(self.style.SUCCESS('\n✓ Cache setup check complete'))
