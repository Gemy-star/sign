# Authentication System Setup - Sign SA

## Summary of Changes

### 1. URL Configuration (`core/urls.py`)
- **Root URL (`/`)**: Now redirects to dashboard or login based on authentication status
- **Login URL (`/login/`)**: Custom login page with Arabic RTL interface
- **Logout URL (`/logout/`)**: Handles user logout and redirects to login
- **Swagger moved**: API documentation moved from `/` to `/api-docs/`

### 2. Authentication Views (`dashboard/views.py`)
Added three new views:

#### `home_redirect(request)`
- Redirects authenticated staff users to dashboard
- Redirects unauthenticated users to login page

#### `login_view(request)`
- Custom login with Arabic interface
- Validates staff-only access
- Shows error messages in Arabic
- Redirects to dashboard on successful login

#### `logout_view(request)`
- Logs out user
- Shows success message in Arabic
- Redirects to login page

### 3. Login Template (`templates/dashboard/login.html`)
Beautiful modern login page with:
- **RTL Arabic layout** using Bootstrap 5 RTL
- **Gradient background** (purple to blue)
- **Logo support** for `logo-dark.png`
- **Password toggle** (show/hide password)
- **Remember me** checkbox
- **Loading state** on form submission
- **Error messages** in Arabic
- **Responsive design** for mobile devices
- **Smooth animations** (slide up, fade in)

### 4. Base Template Updates (`templates/base.html`)
- Changed title from "نظام الرسائل التحفيزية" to "Sign SA"
- Changed brand name from "الرسائل التحفيزية" to "Sign SA"
- Updated logout link to use new logout view URL

### 5. JavaScript Updates (`static/js/main.js`)
- Changed header comment from "MOTIVATIONAL MESSAGES DASHBOARD" to "SIGN SA DASHBOARD"

### 6. Settings Updates

#### `core/settings/base.py`
Added authentication URLs:
```python
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
```

#### `core/settings/production.py`
Added same authentication URLs for production environment

### 7. Logo Files
Created README for logo setup at `static/images/README.md`

Required files:
- `static/images/logo.png` - Sidebar logo
- `static/images/logo-dark.png` - Login page logo

## User Flow

### Unauthenticated User:
1. Visits `/` → Redirected to `/login/`
2. Enters credentials
3. If valid staff user → Redirected to `/dashboard/`
4. If invalid → Error message shown

### Authenticated Staff User:
1. Visits `/` → Redirected to `/dashboard/`
2. Can access all dashboard pages
3. Clicks logout → Redirected to `/login/`

### Non-Staff User:
1. Even if authenticated, redirected to login
2. Shows message: "يجب أن تكون موظفًا للوصول إلى لوحة التحكم"

## Security Features

1. **Staff-only access**: Only staff users can access dashboard
2. **CSRF protection**: All forms include CSRF token
3. **Secure sessions**: Session cookies configured for production
4. **HTTPS redirect**: Production forces HTTPS
5. **Password requirements**: Django default password validation

## Translation

All user-facing messages are in Arabic:
- "تسجيل الدخول" - Login
- "تسجيل الخروج" - Logout
- "اسم المستخدم" - Username
- "كلمة المرور" - Password
- "تذكرني" - Remember me
- "يجب أن تكون موظفًا للوصول إلى لوحة التحكم" - Must be staff to access dashboard
- "اسم المستخدم أو كلمة المرور غير صحيحة" - Invalid credentials
- "تم تسجيل الخروج بنجاح" - Logged out successfully

## Testing

To test the authentication system:

1. **Create superuser** (if not exists):
   ```bash
   poetry run python manage.py createsuperuser
   ```

2. **Run server**:
   ```bash
   poetry run python manage.py runserver
   ```

3. **Test URLs**:
   - `/` - Should redirect to `/login/` or `/dashboard/`
   - `/login/` - Login page
   - `/dashboard/` - Dashboard (requires authentication)
   - `/logout/` - Logout
   - `/admin/` - Django admin
   - `/api-docs/` - Swagger API documentation

## Production Deployment

1. Add logo files to `static/images/`
2. Run collectstatic:
   ```bash
   poetry run python manage.py collectstatic
   ```
3. Ensure ALLOWED_HOSTS includes your domain
4. Set up HTTPS certificate
5. Configure SESSION_COOKIE_SECURE and CSRF_COOKIE_SECURE (already set in production.py)

## Customization

### Change Login Page Colors:
Edit `templates/dashboard/login.html`, find:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Change Logo:
Replace files in `static/images/`:
- `logo.png`
- `logo-dark.png`

### Change Messages Language:
Edit the messages in `dashboard/views.py` functions:
- `login_view()`
- `logout_view()`

## Troubleshooting

### Blank page at `/`:
- Ensure views are imported in `core/urls.py`
- Check that `home_redirect` function exists in `dashboard/views.py`

### Login redirect not working:
- Verify LOGIN_REDIRECT_URL in settings
- Check user has is_staff=True

### Logo not showing:
- Ensure logo files exist in `static/images/`
- Run `python manage.py collectstatic` in production
- Check browser console for 404 errors

### CSS not loading:
- Check STATIC_URL and STATIC_ROOT settings
- Run collectstatic in production
- Verify file paths in templates
