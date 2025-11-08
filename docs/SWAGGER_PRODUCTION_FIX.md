# Swagger UI Production Fix

## Problem
Swagger UI was showing a blank page in production because of:

1. **Static file storage**: `ManifestStaticFilesStorage` was breaking Swagger's CDN resources
2. **X-Frame-Options**: Set to `DENY` which prevented Swagger UI from loading
3. **CSP headers**: Blocking external CDN resources needed by Swagger

## Solutions Applied

### 1. Static Files Configuration (`production.py`)
Changed from:
```python
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
```

To:
```python
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

This allows Swagger UI to load its assets from CDN without hashing issues.

### 2. X-Frame-Options (`production.py`)
Changed from:
```python
X_FRAME_OPTIONS = 'DENY'
```

To:
```python
X_FRAME_OPTIONS = 'SAMEORIGIN'
```

This allows Swagger UI to frame its content properly while maintaining security.

### 3. Added Swagger Settings (`production.py`)
```python
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'PERSIST_AUTH': True,
}
```

## After Deployment

1. **Collect static files**:
   ```bash
   poetry run python manage.py collectstatic --noinput
   ```

2. **Restart your application server**:
   ```bash
   systemctl restart gunicorn  # or your server command
   ```

3. **Clear browser cache** and visit:
   - `/swagger/` - Swagger UI
   - `/redoc/` - ReDoc UI
   - `/api-docs/` - Alternative Swagger endpoint

## Verification

Test these endpoints in production:
- `https://sign-sa.net/swagger/` ✓
- `https://sign-sa.net/redoc/` ✓
- `https://sign-sa.net/api-docs/` ✓
- `http://72.61.90.66/swagger/` ✓

All should now display the API documentation properly.

## Alternative: Local Swagger Assets (Optional)

If you prefer not to use CDN, you can serve Swagger assets locally:

1. Download Swagger UI static files
2. Place in `static/swagger/`
3. Update settings:
   ```python
   SWAGGER_SETTINGS = {
       'STATIC_URL': '/static/swagger/',
       # ... other settings
   }
   ```

## Security Notes

- `X_FRAME_OPTIONS = 'SAMEORIGIN'` still provides protection against clickjacking from external sites
- Swagger UI should ideally be restricted to admin/staff users in production
- Consider adding authentication to Swagger endpoints if needed

## Troubleshooting

### Still seeing blank page?
1. Check browser console for errors
2. Verify static files are collected: `ls staticfiles/`
3. Check web server (nginx/apache) serves static files correctly
4. Clear browser cache (Ctrl+Shift+R)

### 403 Forbidden errors?
- Check `ALLOWED_HOSTS` includes your domain
- Verify `CORS_ALLOWED_ORIGINS` is configured
- Check web server permissions on static files

### JavaScript not loading?
- Ensure CDN URLs are accessible (not blocked by firewall)
- Check browser console for CSP violations
- Verify `STATICFILES_STORAGE` is not using manifest mode
