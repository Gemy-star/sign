# صفحات سياسة الخصوصية والشروط والأحكام

## الملفات المُنشأة

تم إنشاء صفحتين قانونيتين باللغة العربية باستخدام نظام الترجمة في Django:

### 1. صفحة سياسة الخصوصية
- **المسار**: `/dashboard/privacy-policy/`
- **الملف**: `templates/dashboard/privacy_policy.html`
- **المحتوى**:
  - مقدمة عن التزام Sign SA بحماية الخصوصية
  - المعلومات التي يتم جمعها (حساب، استخدام، دفع)
  - كيفية استخدام المعلومات
  - التكامل مع OpenAI للذكاء الاصطناعي
  - مشاركة المعلومات مع أطراف ثالثة
  - إجراءات أمان البيانات (تشفير، JWT، حماية من الهجمات)
  - حقوق المستخدمين
  - سياسة ملفات تعريف الارتباط (Cookies)
  - الاحتفاظ بالبيانات وحذفها
  - خصوصية الأطفال
  - معلومات الاتصال

### 2. صفحة الشروط والأحكام
- **المسار**: `/dashboard/terms-conditions/`
- **الملف**: `templates/dashboard/terms_conditions.html`
- **المحتوى**:
  - قبول الشروط
  - وصف الخدمة والمجالات الثمانية للتطوير الشخصي
  - إنشاء الحسابات وأمانها
  - باقات الاشتراك والأسعار (جدول مقارنة)
  - سياسة الدفع والإلغاء والاسترداد عبر Tap Payment
  - استخدام الذكاء الاصطناعي (OpenAI ChatGPT)
  - الأهداف الشخصية وحدود الاستخدام
  - قواعد الاستخدام المقبول
  - الملكية الفكرية
  - إخلاء المسؤولية
  - تحديد المسؤولية
  - إنهاء الخدمة
  - التحديثات والتعديلات
  - القانون الحاكم (المملكة العربية السعودية)
  - معلومات الاتصال

## التصميم والأسلوب

### الميزات البصرية
- **تصميم RTL**: كامل الدعم للغة العربية
- **ألوان متدرجة**: بنفسجي (Purple gradient) مطابق لصفحة تسجيل الدخول
- **خط IBM Plex Sans Arabic**: خط احترافي للنصوص العربية
- **Font Awesome Icons**: أيقونات تعبيرية
- **Bootstrap 5 RTL**: نظام شبكة متجاوب
- **أنيميشن Slide Up**: حركة سلسة عند تحميل الصفحة
- **Responsive Design**: متجاوب مع جميع أحجام الشاشات

### الأقسام المميزة
- **صندوق التنبيه (Warning Box)**: بخلفية صفراء للتنبيهات المهمة
- **صندوق التمييز (Highlight Box)**: بخلفية رمادية للمعلومات الأساسية
- **جدول المقارنة**: لعرض باقات الاشتراك في صفحة الشروط
- **روابط ملونة**: للتنقل السهل

## التكامل

### إضافة الروابط في صفحة تسجيل الدخول
تم إضافة روابط لسياسة الخصوصية والشروط والأحكام في تذييل صفحة تسجيل الدخول:

```html
<div class="login-footer">
    <p class="mb-2">
        <a href="{% url 'dashboard:privacy_policy' %}">سياسة الخصوصية</a>
        •
        <a href="{% url 'dashboard:terms_conditions' %}">الشروط والأحكام</a>
    </p>
    <p class="mb-0">© 2025 Sign SA. جميع الحقوق محفوظة.</p>
</div>
```

### URL Patterns
تم إضافة المسارات في `dashboard/urls.py`:

```python
path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
```

### Views
تم إضافة الـ views في `dashboard/views.py`:

```python
def privacy_policy(request):
    """Privacy policy page"""
    return render(request, 'dashboard/privacy_policy.html')

def terms_conditions(request):
    """Terms and conditions page"""
    return render(request, 'dashboard/terms_conditions.html')
```

## نظام الترجمة (i18n)

### الإعدادات
تم تحديث `core/settings/base.py`:

```python
# Internationalization
LANGUAGE_CODE = 'ar'  # Arabic as default
TIME_ZONE = 'Asia/Riyadh'  # Saudi Arabia timezone
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
```

### Middleware
تم إضافة `LocaleMiddleware`:

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # For i18n
    'django.middleware.csrf.CsrfViewMiddleware',
    # ...
]
```

### استخدام التاجات (Tags)
في القوالب، يتم استخدام `{% load i18n %}` و `{% trans %}`:

```django
{% load i18n %}

<h2>{% trans "سياسة الخصوصية" %}</h2>
<p>{% trans "نحن في Sign SA نلتزم بحماية خصوصيتك..." %}</p>
```

## إنشاء ملفات الترجمة (اختياري)

إذا كنت تريد إضافة ترجمة إنجليزية في المستقبل:

```bash
# 1. إنشاء مجلد locale
mkdir locale

# 2. إنشاء ملفات الترجمة
poetry run python manage.py makemessages -l en

# 3. تعديل ملف locale/en/LC_MESSAGES/django.po
# وإضافة الترجمات الإنجليزية

# 4. تجميع الترجمات
poetry run python manage.py compilemessages
```

## المحتوى المستمد من README

تم استخدام معلومات من ملف `README.md` لإنشاء المحتوى:

### من README إلى سياسة الخصوصية:
- **Tech Stack** → قسم "التكامل مع الذكاء الاصطناعي" (OpenAI)
- **Payment Integration** → قسم "معلومات الدفع" (Tap Payment)
- **Security Features** → قسم "أمان البيانات" (JWT, CSRF, XSS, SQL Injection)
- **API Features** → قسم "كيفية استخدام المعلومات"

### من README إلى الشروط والأحكام:
- **Features** → قسم "وصف الخدمة"
- **Personal Development Scopes** → قسم "المجالات الحياتية الثمانية"
- **Subscription Packages** → جدول "باقات الاشتراك والأسعار"
- **Usage Examples** → قسم "الأهداف والمحتوى المخصص"
- **API Rate Limiting** → قسم "حدود الاستخدام"

## الوصول للصفحات

### مباشرة عبر المتصفح:
- **سياسة الخصوصية**: `http://localhost:8000/dashboard/privacy-policy/`
- **الشروط والأحكام**: `http://localhost:8000/dashboard/terms-conditions/`

### في الإنتاج:
- **سياسة الخصوصية**: `https://sign-sa.net/dashboard/privacy-policy/`
- **الشروط والأحكام**: `https://sign-sa.net/dashboard/terms-conditions/`

## التخصيص

### تعديل المحتوى
لتعديل المحتوى، قم بتحرير الملفات:
- `templates/dashboard/privacy_policy.html`
- `templates/dashboard/terms_conditions.html`

### تعديل التصميم
لتغيير الألوان أو الأنماط، عدّل CSS داخل تاج `<style>` في كل ملف.

### إضافة أقسام جديدة
استخدم نفس هيكل HTML:

```html
<div class="policy-section">
    <h2>{% trans "عنوان القسم" %}</h2>
    <p>{% trans "محتوى القسم..." %}</p>
    <ul>
        <li>{% trans "نقطة أولى" %}</li>
        <li>{% trans "نقطة ثانية" %}</li>
    </ul>
</div>
```

## الاعتبارات القانونية

⚠️ **تنبيه هام**: هذه الصفحات هي قوالب عامة. يُنصح بمراجعة محامٍ متخصص في:
- قوانين حماية البيانات في السعودية
- قانون التجارة الإلكترونية
- قانون الأنظمة التقنية
- متطلبات GDPR (إذا كان لديك مستخدمون أوروبيون)

## الصيانة

### تحديث التاريخ
عند تعديل السياسات، قم بتحديث تاريخ "آخر تحديث" في كلا الصفحتين:

```html
<p>{% trans "آخر تحديث: 8 نوفمبر 2025" %}</p>
```

### إخطار المستخدمين
عند تعديل جوهري، قم بـ:
1. تحديث تاريخ آخر تحديث
2. إرسال إشعار بريد إلكتروني للمستخدمين
3. عرض إشعار في لوحة التحكم

## التكامل المستقبلي

### إضافة موافقة المستخدم
يمكن إضافة نموذج موافقة عند التسجيل:

```python
class UserConsent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    accepted_privacy_policy = models.BooleanField(default=False)
    accepted_terms = models.BooleanField(default=False)
    consent_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
```

### إضافة PDF للتحميل
يمكن إضافة زر لتحميل نسخة PDF:

```python
from django.http import HttpResponse
from weasyprint import HTML

def privacy_policy_pdf(request):
    html = render_to_string('dashboard/privacy_policy.html')
    pdf = HTML(string=html).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="privacy_policy.pdf"'
    return response
```

## المراجع

- [Django Internationalization](https://docs.djangoproject.com/en/5.0/topics/i18n/)
- [Bootstrap 5 RTL](https://getbootstrap.com/docs/5.3/getting-started/rtl/)
- [Font Awesome Icons](https://fontawesome.com/)
- [IBM Plex Sans Arabic](https://fonts.google.com/specimen/IBM+Plex+Sans+Arabic)
