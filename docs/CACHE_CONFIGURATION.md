# Cache Configuration Guide

## Overview

The application uses different caching strategies for different environments:

### 🔧 Local Development (local.py)
- **Backend**: `LocMemCache` (Local Memory Cache)
- **Features**:
  - Fast in-memory caching
  - No external dependencies
  - Perfect for development
  - Data clears on server restart
  - Max 1000 entries
- **Session**: Database-backed sessions

### 🚀 Production (production.py)
- **Backend**: `django-redis` (Redis Cache)
- **Features**:
  - High-performance distributed cache
  - Persistent across restarts
  - Shared cache for multiple servers
  - Advanced compression (zlib)
  - Connection pooling
  - Automatic fallback to database cache if Redis is unavailable
- **Session**: Redis-backed sessions for better performance

---

## Redis Configuration (Production)

### Environment Variables

Set these in your production environment:

```bash
# Redis URL (required)
REDIS_URL=redis://localhost:6379/1

# Or for Redis with password
REDIS_URL=redis://:password@localhost:6379/1

# For Redis Sentinel
REDIS_URL=redis://sentinel1:26379,sentinel2:26379/mymaster/1

# For Redis Cluster
REDIS_URL=redis://node1:6379,node2:6379,node3:6379/1
```

### Redis Settings

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,          # Max connections to Redis
                'retry_on_timeout': True,       # Retry on timeout
            },
            'SOCKET_CONNECT_TIMEOUT': 5,        # Connection timeout
            'SOCKET_TIMEOUT': 5,                # Socket timeout
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,          # Don't crash if Redis is down
        },
        'KEY_PREFIX': 'motivational_app',
        'TIMEOUT': 300,                         # 5 minutes default
    }
}
```

### Benefits

1. **Performance**: 10-100x faster than database queries
2. **Scalability**: Shared cache across multiple app servers
3. **Session Management**: Fast session storage and retrieval
4. **Rate Limiting**: Efficient rate limiting implementation
5. **Real-time Features**: Support for pub/sub patterns

---

## Setup Instructions

### Development (SQLite + Local Memory Cache)

No additional setup needed! Just run:

```bash
python manage.py runserver
```

### Production (PostgreSQL + Redis)

#### 1. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

#### 2. Install Python Dependencies

Already included in your pyproject.toml:
```bash
poetry install --with prod
```

#### 3. Configure Environment Variables

Create a `.env` file or set environment variables:
```bash
export REDIS_URL=redis://localhost:6379/1
export DATABASE_URL=postgresql://user:pass@localhost/dbname
```

#### 4. Test Redis Connection

```bash
python manage.py setup_cache
```

#### 5. Create Cache Table (Fallback)

If Redis fails, the system falls back to database cache:
```bash
python manage.py createcachetable
```

---

## Cache Usage Examples

### Basic Cache Operations

```python
from django.core.cache import cache

# Set cache
cache.set('my_key', 'my_value', timeout=300)  # 5 minutes

# Get cache
value = cache.get('my_key')
value = cache.get('my_key', default='default_value')

# Delete cache
cache.delete('my_key')

# Clear all cache
cache.clear()

# Set multiple
cache.set_many({'key1': 'value1', 'key2': 'value2'}, timeout=300)

# Get multiple
values = cache.get_many(['key1', 'key2'])
```

### View Caching

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache for 15 minutes
def my_view(request):
    # Expensive operation
    return render(request, 'template.html', context)
```

### Template Fragment Caching

```django
{% load cache %}
{% cache 500 sidebar request.user.username %}
    .. expensive sidebar rendering ..
{% endcache %}
```

### Low-level Cache API

```python
from django.core.cache import caches

# Use specific cache
default_cache = caches['default']
default_cache.set('key', 'value')
```

---

## Monitoring & Maintenance

### Check Cache Status

```bash
# Run our custom command
python manage.py setup_cache

# Or use Redis CLI
redis-cli
> INFO
> DBSIZE
> KEYS motivational_app:*
```

### Clear Cache

```bash
# Django command
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Or Redis CLI
redis-cli
> FLUSHDB
```

### Monitor Redis

```bash
# Real-time monitoring
redis-cli --stat

# Monitor commands
redis-cli MONITOR

# Get memory usage
redis-cli INFO memory
```

---

## Performance Tips

1. **Use appropriate timeouts**: Don't cache forever
   ```python
   cache.set('key', value, timeout=60*60*24)  # 24 hours
   ```

2. **Cache expensive queries**:
   ```python
   def get_expensive_data():
       data = cache.get('expensive_data')
       if data is None:
           data = ExpensiveModel.objects.all().select_related('related')
           cache.set('expensive_data', data, timeout=300)
       return data
   ```

3. **Use cache versioning**:
   ```python
   cache.set('key', value, version=2)
   cache.get('key', version=2)
   ```

4. **Invalidate strategically**:
   ```python
   # In save method
   def save(self, *args, **kwargs):
       super().save(*args, **kwargs)
       cache.delete(f'model_{self.pk}')
   ```

---

## Troubleshooting

### Redis Connection Issues

**Error**: `ConnectionError: Error connecting to Redis`

**Solutions**:
1. Check if Redis is running: `redis-cli ping`
2. Verify REDIS_URL environment variable
3. Check firewall rules
4. System will auto-fallback to database cache

### Memory Issues

**Error**: `OOM command not allowed when used memory > 'maxmemory'`

**Solutions**:
1. Increase Redis max memory: `redis-cli CONFIG SET maxmemory 2gb`
2. Set eviction policy: `redis-cli CONFIG SET maxmemory-policy allkeys-lru`
3. Clear old data: `cache.clear()`

### Slow Cache Performance

**Solutions**:
1. Check Redis memory: `redis-cli INFO memory`
2. Enable compression (already enabled)
3. Use connection pooling (already enabled)
4. Monitor with: `redis-cli --latency`

---

## Security Considerations

### Production Checklist

- ✅ Use password-protected Redis: `redis://:password@host:6379/1`
- ✅ Enable Redis AUTH: `requirepass yourpassword` in redis.conf
- ✅ Bind to localhost only if on same server: `bind 127.0.0.1`
- ✅ Use SSL/TLS for remote connections: `rediss://` protocol
- ✅ Implement network-level security (VPC, firewall)
- ✅ Regular backups with Redis persistence (RDB/AOF)
- ✅ Monitor for suspicious activity

---

## Cache Backends Comparison

| Feature | LocMemCache | DatabaseCache | Redis |
|---------|-------------|---------------|-------|
| Speed | ⚡⚡⚡ | ⚡ | ⚡⚡⚡ |
| Persistence | ❌ | ✅ | ✅ |
| Multi-server | ❌ | ✅ | ✅ |
| Memory Usage | Low | Medium | Medium |
| Setup Complexity | None | Low | Medium |
| Best For | Development | Small apps | Production |

---

## Additional Resources

- [Django Cache Framework](https://docs.djangoproject.com/en/stable/topics/cache/)
- [django-redis Documentation](https://github.com/jazzband/django-redis)
- [Redis Documentation](https://redis.io/documentation)
- [Redis Best Practices](https://redis.io/topics/best-practices)

---

**Status**: ✅ Configured and Ready
**Development**: Local Memory Cache
**Production**: Redis with Database Fallback
