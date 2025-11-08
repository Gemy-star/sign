# Toast Notifications & Page Loader Guide

**Date:** 2025-11-09
**Summary:** Django messages as toast notifications + animated logo loader

## Features Added

### 1. Toast Notifications

**Location:** `templates/base.html`

Django messages now automatically display as Bootstrap toast notifications in the top-right corner.

**Supported Message Types:**
- `success` - Green with check icon
- `error` / `danger` - Red with exclamation icon
- `warning` - Orange with warning icon
- `info` - Blue with info icon
- Default - Primary color with bell icon

**Auto-hide:** Toasts automatically disappear after 5 seconds

**Example Usage in Views:**
```python
from django.contrib import messages

# Success message
messages.success(request, 'تم حفظ البيانات بنجاح')

# Error message
messages.error(request, 'حدث خطأ أثناء الحفظ')

# Warning message
messages.warning(request, 'تحذير: البيانات غير مكتملة')

# Info message
messages.info(request, 'معلومة: يرجى التحقق من البريد الإلكتروني')
```

**Programmatic Usage (JavaScript):**
```javascript
// Show toast from JavaScript
DashboardUtils.showToast('تمت العملية بنجاح', 'success');
DashboardUtils.showToast('حدث خطأ', 'error');
DashboardUtils.showToast('تحذير', 'warning');
DashboardUtils.showToast('معلومة', 'info');
```

### 2. Page Loader

**Location:** `templates/base.html`

Animated loader using `logo.png` with multiple CSS animations.

**Features:**
- Shows automatically on page load
- Hides when page fully loads (300ms delay)
- Shows again during navigation (beforeunload)
- Gradient background (orange to purple)
- Multiple animation effects on logo

**Loader Animations:**

**Default (Combined):**
- Float effect (moves up and down)
- Rotate effect (360° rotation)
- Text pulse effect

**Alternative Animations:**

You can change the loader style by adding a class to the logo in `base.html`:

1. **Bounce Effect:**
   ```html
   <img src="{% static 'images/logo.png' %}" alt="Loading..." class="loader-logo bounce">
   ```

2. **Pulse Effect:**
   ```html
   <img src="{% static 'images/logo.png' %}" alt="Loading..." class="loader-logo pulse">
   ```

3. **Spin Only:**
   ```html
   <img src="{% static 'images/logo.png' %}" alt="Loading..." class="loader-logo spin">
   ```

**Manual Control (JavaScript):**
```javascript
// Show loader
DashboardUtils.PageLoader.show();

// Hide loader
DashboardUtils.PageLoader.hide();

// Example: Show loader during AJAX request
fetch('/api/data')
    .then(response => {
        DashboardUtils.PageLoader.show();
        return response.json();
    })
    .then(data => {
        // Process data
        DashboardUtils.PageLoader.hide();
    });
```

## CSS Customization

### Toast Styles

**File:** `static/css/main.css`

```css
/* Customize toast appearance */
.toast {
    min-width: 300px;        /* Minimum width */
    max-width: 500px;        /* Maximum width */
    backdrop-filter: blur(10px); /* Blur effect */
    box-shadow: var(--shadow-lg);
}

/* Customize toast body */
.toast-body {
    padding: 1rem;
    font-size: 0.95rem;
    font-weight: 500;
}
```

### Loader Styles

**File:** `static/css/main.css`

```css
/* Customize loader background */
.page-loader {
    background: linear-gradient(135deg, rgba(235, 103, 42, 0.95), rgba(129, 91, 164, 0.95));
}

/* Customize logo size */
.loader-logo {
    width: 120px;
    height: 120px;
}

/* Customize loader text */
.loader-text {
    color: white;
    font-size: 1.25rem;
    font-weight: 600;
}
```

## Animation Details

### Logo Animations

**Float Animation (2s):**
```css
@keyframes logoFloat {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-20px) scale(1.05); }
}
```

**Rotate Animation (3s):**
```css
@keyframes logoRotate {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
```

**Bounce Animation (1s):**
```css
@keyframes logoBounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-30px); }
}
```

**Pulse Animation (1.5s):**
```css
@keyframes logoPulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.8; }
}
```

### Toast Animations

**Slide In (0.3s):**
```css
@keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
```

**Slide Out (0.3s):**
```css
@keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}
```

## Responsive Design

### Mobile Adjustments

**Toast:**
- Maintains min-width 300px
- Max-width 500px on all devices
- Position: top-right corner

**Loader:**
- Logo: 120px → 80px on mobile
- Text: 1.25rem → 1rem on mobile

```css
@media (max-width: 768px) {
    .loader-logo {
        width: 80px;
        height: 80px;
    }

    .loader-text {
        font-size: 1rem;
    }
}
```

## Integration Examples

### Example 1: Form Submission
```python
def package_create(request):
    if request.method == 'POST':
        try:
            package = Package.objects.create(...)
            messages.success(request, f'تم إنشاء الباقة {package.name} بنجاح')
            return redirect('dashboard:packages')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
```

**Result:** Success toast appears top-right, auto-hides after 5s

### Example 2: Multiple Messages
```python
def process_data(request):
    messages.info(request, 'بدأت معالجة البيانات...')
    messages.warning(request, 'تحذير: بعض البيانات ناقصة')
    messages.success(request, 'تمت المعالجة بنجاح')
```

**Result:** 3 toasts appear staggered (200ms delay between each)

### Example 3: AJAX with Loader
```javascript
// Show loader before request
DashboardUtils.PageLoader.show();

fetch('/api/subscriptions/', {
    method: 'POST',
    body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => {
    DashboardUtils.PageLoader.hide();
    DashboardUtils.showToast('تم الحفظ بنجاح', 'success');
})
.catch(error => {
    DashboardUtils.PageLoader.hide();
    DashboardUtils.showToast('حدث خطأ', 'error');
});
```

## Configuration Options

### Toast Configuration

Edit `static/js/main.js`:

```javascript
const toast = new bootstrap.Toast(toastElement, {
    autohide: true,    // Auto-hide after delay
    delay: 5000        // 5 seconds (change as needed)
});
```

### Loader Hide Delay

Edit `static/js/main.js`:

```javascript
hide() {
    setTimeout(() => {
        this.loader.classList.add('hidden');
    }, 300); // Change delay (ms)
}
```

## Files Modified

1. `templates/base.html` - Added toast container and loader HTML
2. `static/css/main.css` - Added toast and loader styles + animations
3. `static/js/main.js` - Added toast initialization and loader control

## Browser Support

**CSS Animations:** All modern browsers (IE11+)
**backdrop-filter:** Chrome 76+, Safari 9+, Firefox 103+
**Bootstrap Toast:** Bootstrap 5.3+ required

## Testing Checklist

- [ ] Success message displays green toast
- [ ] Error message displays red toast
- [ ] Warning message displays orange toast
- [ ] Info message displays blue toast
- [ ] Toasts auto-hide after 5 seconds
- [ ] Close button works on toasts
- [ ] Multiple toasts stack properly
- [ ] Loader shows on page load
- [ ] Loader hides when page fully loaded
- [ ] Loader shows during navigation
- [ ] Logo animations working (float + rotate)
- [ ] Loader text pulses
- [ ] Mobile responsive (smaller logo)
- [ ] RTL support (toasts on right side)

## Tips

1. **Prevent loader on specific pages:** Add `PageLoader.hide()` in page-specific scripts
2. **Custom toast duration:** Change `delay: 5000` in JavaScript
3. **Disable loader:** Remove or comment out loader div in base.html
4. **Change loader animation:** Add class to `.loader-logo` (bounce/pulse/spin)
5. **Custom colors:** Modify gradient in `.page-loader` CSS

## Performance

- **Toast:** Minimal impact, uses native Bootstrap 5 components
- **Loader:** No performance impact, hidden after page load
- **Animations:** GPU-accelerated (transform, opacity)
- **No external dependencies:** Uses only Bootstrap 5 + custom CSS

## Accessibility

- **Toast:** `role="alert"`, `aria-live="assertive"`, `aria-atomic="true"`
- **Close button:** `aria-label="Close"`
- **Keyboard support:** Bootstrap native keyboard handling
- **Screen readers:** Messages announced automatically
- **High contrast:** Works with Windows high contrast mode
