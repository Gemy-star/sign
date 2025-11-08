# Quick Reference Card - Mobile Responsive Dashboard

## Bootstrap 5 Grid Quick Reference

### Common Column Patterns
```html
<!-- 1→2→4 columns (mobile→tablet→desktop) -->
<div class="row g-3">
  <div class="col-12 col-sm-6 col-lg-3">Content</div>
</div>

<!-- 1→2→3 columns -->
<div class="row g-3">
  <div class="col-12 col-sm-6 col-lg-4">Content</div>
</div>

<!-- 1→1→2 columns (8-4 split on desktop) -->
<div class="row g-3">
  <div class="col-12 col-lg-8">Main content</div>
  <div class="col-12 col-lg-4">Sidebar</div>
</div>
```

### Responsive Utilities
```html
<!-- Hide on mobile, show on desktop -->
<div class="d-none d-md-block">Desktop only</div>

<!-- Show on mobile, hide on desktop -->
<div class="d-md-none">Mobile only</div>

<!-- Different content for mobile vs desktop -->
<div class="d-md-none">Mobile view</div>
<div class="d-none d-md-block">Desktop view</div>
```

---

## Bootstrap Select Quick Reference

### Basic Implementation
```html
<!-- HTML -->
<select class="selectpicker form-select" data-live-search="true">
  <option value="1">Option 1</option>
  <option value="2">Option 2</option>
</select>

<!-- JavaScript -->
<script>
$(document).ready(function() {
  $('.selectpicker').selectpicker({
    noneSelectedText: 'لم يتم الاختيار',
    liveSearchPlaceholder: 'بحث...'
  });
});
</script>
```

### With Icons
```html
<select class="selectpicker">
  <option data-icon="fas fa-check-circle">Active</option>
  <option data-icon="fas fa-times-circle">Inactive</option>
</select>
```

### Data Attributes
- `data-live-search="true"` - Enable search
- `data-style="btn-outline-primary"` - Button style
- `data-size="8"` - Max visible items
- `data-icon="fas fa-icon"` - Font Awesome icon

### Methods
```javascript
// Refresh after DOM change
$('.selectpicker').selectpicker('refresh');

// Set value
$('.selectpicker').selectpicker('val', 'value');

// Destroy
$('.selectpicker').selectpicker('destroy');
```

---

## Swiper Quick Reference

### Basic Carousel
```html
<!-- HTML -->
<div class="swiper mySwiper">
  <div class="swiper-wrapper">
    <div class="swiper-slide">Slide 1</div>
    <div class="swiper-slide">Slide 2</div>
  </div>
  <div class="swiper-pagination"></div>
</div>

<!-- JavaScript -->
<script>
const swiper = new Swiper('.mySwiper', {
  slidesPerView: 1,
  spaceBetween: 20,
  pagination: {
    el: '.swiper-pagination',
    clickable: true,
  },
});
</script>
```

### Common Options
```javascript
new Swiper('.swiper', {
  // Basic
  slidesPerView: 1,           // Slides visible
  spaceBetween: 20,            // Gap between slides
  loop: true,                  // Infinite loop

  // Autoplay
  autoplay: {
    delay: 3000,               // 3 seconds
    disableOnInteraction: false,
  },

  // Pagination
  pagination: {
    el: '.swiper-pagination',
    clickable: true,
    dynamicBullets: true,
  },

  // Navigation
  navigation: {
    nextEl: '.swiper-button-next',
    prevEl: '.swiper-button-prev',
  },

  // Effects
  effect: 'slide',            // 'slide', 'fade', 'cube', 'coverflow', 'flip'
  speed: 600,                 // Transition speed

  // Responsive
  breakpoints: {
    640: { slidesPerView: 2 },
    768: { slidesPerView: 3 },
    1024: { slidesPerView: 4 },
  }
});
```

### Methods
```javascript
// Control
swiper.slideNext();          // Next slide
swiper.slidePrev();          // Previous slide
swiper.slideTo(index);       // Go to slide

// Autoplay
swiper.autoplay.start();
swiper.autoplay.stop();

// Destroy
swiper.destroy();

// Update
swiper.update();
```

---

## Responsive Table Quick Reference

### HTML Structure
```html
<div class="table-responsive-wrapper">
  <table class="table data-table">
    <thead>...</thead>
    <tbody>...</tbody>
  </table>
</div>
```

### CSS (Already in main.css)
```css
.table-responsive-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  touch-action: pan-x;
}

.data-table {
  min-width: 1000px !important;
  width: max-content;
}
```

---

## RTL Support Quick Reference

### Bootstrap Select RTL
```css
.bootstrap-select {
  direction: rtl;
}
```

### Swiper RTL
```javascript
new Swiper('.swiper', {
  direction: 'horizontal',  // Automatic RTL support
  // Swiper auto-detects RTL from CSS direction
});
```

### Custom RTL Navigation
```css
.swiper-rtl .swiper-button-next {
  left: 10px;
  right: auto;
}

.swiper-rtl .swiper-button-prev {
  right: 10px;
  left: auto;
}
```

---

## CSS Custom Properties (Variables)

### Colors
```css
--color-primary: #eb672a;
--color-accent: #f09d6e;
--color-white: #ffffff;
--color-text: #334155;
```

### Spacing
```css
--border-radius-sm: 8px;
--border-radius-md: 12px;
--border-radius-lg: 16px;
--border-radius-full: 50%;
```

### Transitions
```css
--transition-fast: 0.2s ease;
--transition-base: 0.3s ease;
```

### Shadows
```css
--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
```

### Usage
```css
.my-element {
  background: var(--color-primary);
  border-radius: var(--border-radius-md);
  transition: var(--transition-base);
  box-shadow: var(--shadow-md);
}
```

---

## Breakpoints Quick Reference

### Bootstrap 5 Breakpoints
| Breakpoint | Class Infix | Dimensions |
|------------|-------------|------------|
| Extra small | *None* | <576px |
| Small | `sm` | ≥576px |
| Medium | `md` | ≥768px |
| Large | `lg` | ≥992px |
| Extra large | `xl` | ≥1200px |
| Extra extra large | `xxl` | ≥1400px |

### Media Query Examples
```css
/* Mobile first (default) */
.element { width: 100%; }

/* Tablet and up */
@media (min-width: 768px) {
  .element { width: 50%; }
}

/* Desktop and up */
@media (min-width: 992px) {
  .element { width: 33.333%; }
}
```

### Display Utilities
```html
<!-- Responsive display -->
<div class="d-none">Hidden on all</div>
<div class="d-block">Shown on all</div>
<div class="d-none d-md-block">Hidden mobile, shown tablet+</div>
<div class="d-md-none">Shown mobile, hidden tablet+</div>

<!-- Responsive flex -->
<div class="d-flex">Flex on all</div>
<div class="d-none d-md-flex">Flex tablet+</div>
```

---

## Common Tasks Cheat Sheet

### Add New Page with Responsive Grid
```html
{% extends 'base.html' %}

{% block content %}
<div class="container-fluid py-4">
  <!-- Stats Cards -->
  <div class="row g-3 mb-4">
    <div class="col-12 col-sm-6 col-lg-3">
      <div class="stat-card">...</div>
    </div>
    <!-- Repeat 3 more times -->
  </div>

  <!-- Content -->
  <div class="row g-3">
    <div class="col-12 col-lg-8">
      <div class="card">Main content</div>
    </div>
    <div class="col-12 col-lg-4">
      <div class="card">Sidebar</div>
    </div>
  </div>
</div>
{% endblock %}
```

### Add Enhanced Dropdown to Form
```html
<!-- In form -->
<div class="mb-3">
  <label for="mySelect" class="form-label">Select Option</label>
  <select id="mySelect"
          name="my_field"
          class="selectpicker form-select"
          data-live-search="true"
          data-style="btn-outline-primary">
    <option value="">Choose...</option>
    <option value="1">Option 1</option>
  </select>
</div>

<!-- Before closing </body> -->
<script>
$(document).ready(function() {
  $('#mySelect').selectpicker({
    noneSelectedText: 'لم يتم الاختيار',
    liveSearchPlaceholder: 'بحث...'
  });
});
</script>
```

### Add Carousel to Page
```html
<!-- Mobile carousel -->
<div class="d-md-none mb-4">
  <div class="swiper myCarousel">
    <div class="swiper-wrapper">
      {% for item in items %}
      <div class="swiper-slide">
        <div class="card">{{ item.name }}</div>
      </div>
      {% endfor %}
    </div>
    <div class="swiper-pagination"></div>
  </div>
</div>

<!-- Desktop grid -->
<div class="row g-3 d-none d-md-flex">
  {% for item in items %}
  <div class="col-12 col-sm-6 col-lg-4">
    <div class="card">{{ item.name }}</div>
  </div>
  {% endfor %}
</div>

<!-- JavaScript -->
<script>
const myCarousel = new Swiper('.myCarousel', {
  slidesPerView: 1,
  spaceBetween: 20,
  pagination: {
    el: '.swiper-pagination',
    clickable: true,
  },
});
</script>
```

---

## Debugging Checklist

### Page not responsive?
- [ ] Check viewport meta tag in `base.html`
- [ ] Verify Bootstrap CSS loaded
- [ ] Check for `!important` overrides in custom CSS
- [ ] Use Chrome DevTools responsive mode
- [ ] Check browser console for CSS errors

### Bootstrap Select not working?
- [ ] jQuery loaded before Bootstrap Select?
- [ ] `.selectpicker` class on `<select>`?
- [ ] `selectpicker()` initialization called?
- [ ] Check console for JavaScript errors

### Swiper not working?
- [ ] Swiper CSS and JS loaded?
- [ ] Correct class structure?
- [ ] At least one slide exists?
- [ ] Initialization after DOM ready?

### Table not scrolling?
- [ ] `.table-responsive-wrapper` wrapper?
- [ ] Table has `min-width`?
- [ ] `overflow-x: auto` applied?
- [ ] Check on actual device, not just DevTools

---

## Quick Testing

### Chrome DevTools
```
1. F12 - Open DevTools
2. Ctrl+Shift+M - Toggle device toolbar
3. Test viewports: 375px, 768px, 992px, 1200px
4. Check console for errors
```

### Console Checks
```javascript
// Verify libraries
typeof jQuery !== 'undefined'
typeof Swiper !== 'undefined'
typeof $.fn.selectpicker !== 'undefined'

// Check Bootstrap version
bootstrap.Tooltip.VERSION  // Should be 5.x
```

---

## Resources

- **Bootstrap 5 Docs**: https://getbootstrap.com/docs/5.3/
- **Swiper Demos**: https://swiperjs.com/demos
- **Bootstrap Select Docs**: https://developer.snapappointments.com/bootstrap-select/

---

**Last Updated:** January 8, 2025
**Version:** 1.0.0
