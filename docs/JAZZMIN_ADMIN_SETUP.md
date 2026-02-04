# Django Jazzmin Admin Setup Guide

## Overview

**Django Jazzmin** is a modern, elegant theme for Django admin that transforms the default admin interface into a beautiful, user-friendly experience. It's built on top of AdminLTE 3 and provides extensive customization options without modifying core Django logic.

**Benefits:**
- 🎨 Modern, responsive UI with dark mode support
- 📱 Mobile-friendly admin interface
- 🎯 Highly customizable (colors, icons, menus)
- 🚀 Zero performance overhead
- 🔧 Easy to maintain and update
- 📊 Better data visualization and UX

---

## Installation Steps

### 1. Install the Package

```bash
# Activate your virtual environment first
cd d:/rootpointers/op_vanguard_backend
.\venv\Scripts\activate

# Install django-jazzmin
pip install django-jazzmin
```

**Already installed:** ✅ `django-jazzmin==3.0.1`

### 2. Update `requirements.txt`

```txt
django-jazzmin==3.0.1
```

**Already added:** ✅

### 3. Add to `INSTALLED_APPS`

In `core/settings.py`, add `'jazzmin'` **before** `django.contrib.admin`:

```python
INSTALLED_APPS = [
    'jazzmin',  # ⚠️ Must be BEFORE django.contrib.admin
    
    'django.contrib.admin',
    'django.contrib.auth',
    # ... rest of your apps
]
```

**Already configured:** ✅

---

## Configuration

### Basic Configuration (Already Applied)

The following configuration has been added to `core/settings.py`:

```python
JAZZMIN_SETTINGS = {
    # Branding
    "site_title": "Vanguard Admin",
    "site_header": "Vanguard",
    "site_brand": "Vanguard Veterans Platform",
    "welcome_sign": "Welcome to Vanguard Admin Portal",
    "copyright": "Vanguard Veterans Platform",
    
    # Top Menu
    "topmenu_links": [
        {"name": "Home", "url": "admin:index"},
        {"name": "API Docs", "url": "/api/", "new_window": True},
        {"model": "accounts.User"},
        {"app": "intel"},
    ],
    
    # Menu Ordering
    "order_with_respect_to": [
        "accounts", "intel", "exchange", "network", "notification", "auth"
    ],
    
    # Custom Icons (Font Awesome 5)
    "icons": {
        "accounts.User": "fas fa-user-shield",
        "intel.Intel": "fas fa-lightbulb",
        "exchange.Exchange": "fas fa-exchange-alt",
        "network.Follow": "fas fa-user-friends",
        "notification.Notification": "fas fa-bell",
        # ... more icons
    },
    
    # UI Settings
    "show_ui_builder": True,  # Enable UI customizer
    "changeform_format": "horizontal_tabs",  # Tab layout for forms
}

JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-navy navbar-dark",  # Navy blue navbar
    "sidebar": "sidebar-dark-navy",       # Dark navy sidebar
    "accent": "accent-primary",            # Primary accent color
    "theme": "default",                    # AdminLTE theme
}
```

---

## Customization Options

### 1. Adding Your Logo

Place your logo in `static/images/` and update settings:

```python
JAZZMIN_SETTINGS = {
    "site_logo": "images/vanguard-logo.png",
    "site_logo_classes": "img-circle",  # Optional: circular logo
    "site_icon": "images/favicon.ico",   # Browser tab icon
}
```

### 2. Custom Color Schemes

Choose from predefined color combinations:

```python
JAZZMIN_UI_TWEAKS = {
    # Navy (Current - Professional)
    "navbar": "navbar-navy navbar-dark",
    "sidebar": "sidebar-dark-navy",
    
    # Alternative: Dark Mode
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
    
    # Alternative: Light & Modern
    "navbar": "navbar-white navbar-light",
    "sidebar": "sidebar-light-primary",
    
    # Alternative: Success Green
    "navbar": "navbar-success navbar-dark",
    "sidebar": "sidebar-dark-success",
}
```

Available navbar colors: `navy`, `primary`, `secondary`, `success`, `info`, `warning`, `danger`, `dark`, `white`

### 3. Custom Icons

Use Font Awesome 5 icons for your models:

```python
"icons": {
    "your_app.YourModel": "fas fa-icon-name",
}
```

**Icon Resources:**
- [Font Awesome 5 Icons](https://fontawesome.com/v5/search?m=free)
- [AdminLTE Icons Preview](https://adminlte.io/themes/v3/pages/UI/icons.html)

### 4. Search Configuration

Enable quick search across models:

```python
JAZZMIN_SETTINGS = {
    "search_model": [
        "auth.User",
        "accounts.User",
        "intel.Intel",
        "exchange.Exchange",
    ],
}
```

### 5. Custom CSS/JS

Add custom styling:

```python
JAZZMIN_SETTINGS = {
    "custom_css": "css/admin_custom.css",
    "custom_js": "js/admin_custom.js",
}
```

Create files in `static/css/` and `static/js/`

---

## Features Enabled

### ✅ Currently Active Features

1. **UI Builder** - Live theme customization (click "UI" button in admin)
2. **Horizontal Tabs** - Better form organization
3. **Custom Icons** - Visual model identification
4. **Menu Ordering** - Logical app grouping
5. **Quick Links** - Fast navigation to common tasks
6. **Modern Theme** - Navy blue professional look
7. **Responsive Design** - Mobile-friendly interface

### 🎯 Recommended Enhancements

#### 1. Dashboard Widgets

Add custom widgets to admin homepage in `admin.py`:

```python
from django.contrib import admin
from django.db.models import Count

@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['widget_data'] = {
            'total_users': User.objects.count(),
            'active_intel': Intel.objects.filter(status='active').count(),
        }
        return super().changelist_view(request, extra_context)
```

#### 2. Custom Filters

Enhance list views with better filters:

```python
class YourModelAdmin(admin.ModelAdmin):
    list_filter = ['created_at', 'status', 'category']
    date_hierarchy = 'created_at'
    list_per_page = 50
```

#### 3. Inline Editing

Enable related model editing:

```python
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class IntelAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
```

---

## Best Practices

### 1. Performance Optimization

```python
class YourModelAdmin(admin.ModelAdmin):
    # Use select_related for foreign keys
    list_select_related = ['user', 'category']
    
    # Use prefetch_related for many-to-many
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('tags')
    
    # Limit fields in list view
    list_display = ['id', 'title', 'status', 'created_at']
    
    # Add search fields
    search_fields = ['title', 'description']
```

### 2. Security

```python
class SensitiveModelAdmin(admin.ModelAdmin):
    # Hide sensitive fields
    exclude = ['password_hash', 'secret_token']
    
    # Read-only fields
    readonly_fields = ['created_at', 'updated_at', 'uuid']
    
    # Limit delete permissions
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
```

### 3. User Experience

```python
class UserFriendlyAdmin(admin.ModelAdmin):
    # Organize fields in fieldsets
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email')
        }),
        ('Advanced Options', {
            'classes': ('collapse',),  # Collapsible section
            'fields': ('is_active', 'permissions')
        }),
    )
    
    # Add helpful text
    def get_form(self, request, obj=None, **kwargs):
        help_texts = {
            'name': 'Enter the full name of the user',
            'email': 'Must be a valid email address',
        }
        kwargs.update({'help_texts': help_texts})
        return super().get_form(request, obj, **kwargs)
```

---

## Testing & Verification

### 1. Check Configuration

```bash
python manage.py check
```

**Status:** ✅ No issues detected

### 2. Collect Static Files (Production)

```bash
python manage.py collectstatic --noinput
```

### 3. Access Admin Panel

Navigate to: `http://localhost:8000/admin/`

**Expected:**
- Modern navy blue interface
- Custom Vanguard branding
- Organized sidebar menu
- Font Awesome icons
- UI customizer button (top-right)

---

## Troubleshooting

### Issue: Jazzmin not loading

**Solution:**
- Ensure `'jazzmin'` is **before** `'django.contrib.admin'`
- Clear browser cache (Ctrl+Shift+R)
- Run `python manage.py collectstatic`

### Issue: Icons not showing

**Solution:**
- Check Font Awesome icon names at [fontawesome.com](https://fontawesome.com/v5)
- Use format: `"fas fa-icon-name"` (Font Awesome Solid)
- Alternative: `"far fa-icon-name"` (Font Awesome Regular)

### Issue: Custom CSS not applying

**Solution:**
- Ensure files are in `static/` directory
- Run `python manage.py collectstatic`
- Clear browser cache
- Check `STATIC_URL` and `STATIC_ROOT` in settings

### Issue: UI Builder not saving

**Solution:**
- UI Builder changes are session-based (not permanent)
- To make permanent, copy settings from UI Builder to `JAZZMIN_UI_TWEAKS`

---

## Advanced Customization

### Custom Dashboard

Create `admin/index.html` in your templates:

```html
{% extends "admin/index.html" %}
{% load static %}

{% block content %}
<div class="row">
    <div class="col-lg-3 col-6">
        <div class="small-box bg-info">
            <div class="inner">
                <h3>{{ total_users }}</h3>
                <p>Total Users</p>
            </div>
            <div class="icon">
                <i class="fas fa-users"></i>
            </div>
        </div>
    </div>
    <!-- Add more widgets -->
</div>
{{ block.super }}
{% endblock %}
```

### Custom Actions

Add bulk actions to admin:

```python
@admin.action(description='Mark selected as published')
def make_published(modeladmin, request, queryset):
    queryset.update(status='published')
    
class YourModelAdmin(admin.ModelAdmin):
    actions = [make_published]
```

---

## Production Checklist

- [ ] Set `DEBUG = False` in production
- [ ] Configure proper `STATIC_ROOT` and `MEDIA_ROOT`
- [ ] Run `collectstatic` before deployment
- [ ] Add your logo and favicon
- [ ] Customize colors to match brand
- [ ] Test on different screen sizes
- [ ] Set proper admin permissions
- [ ] Add custom dashboard widgets
- [ ] Configure search fields
- [ ] Optimize list_display queries

---

## Resources

- **Documentation:** [django-jazzmin.readthedocs.io](https://django-jazzmin.readthedocs.io/)
- **GitHub:** [github.com/farridav/django-jazzmin](https://github.com/farridav/django-jazzmin)
- **AdminLTE Demo:** [adminlte.io/themes/v3/](https://adminlte.io/themes/v3/)
- **Font Awesome Icons:** [fontawesome.com/v5/search](https://fontawesome.com/v5/search?m=free)

---

## Summary

✅ **Installed:** `django-jazzmin==3.0.1`  
✅ **Configured:** Professional navy blue theme with custom branding  
✅ **Features:** UI builder, custom icons, organized menus, horizontal tabs  
✅ **Tested:** No configuration errors detected  

**Next Steps:**
1. Access admin at `http://localhost:8000/admin/`
2. Try the UI customizer (top-right button)
3. Add your logo to `static/images/`
4. Customize colors to your preference
5. Explore dashboard customization options

---

**Version:** 1.0  
**Last Updated:** November 7, 2025  
**Maintained by:** Vanguard Development Team
