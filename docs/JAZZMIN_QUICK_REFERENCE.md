# Jazzmin Quick Reference

## 🎨 Color Themes

### Navbar Options
```python
"navbar": "navbar-{color} navbar-{mode}"
```
- **Colors:** `navy`, `primary`, `success`, `info`, `warning`, `danger`, `dark`, `white`
- **Modes:** `dark`, `light`

**Examples:**
- `"navbar-navy navbar-dark"` - Navy blue (current)
- `"navbar-white navbar-light"` - Light mode
- `"navbar-success navbar-dark"` - Green theme

### Sidebar Options
```python
"sidebar": "sidebar-{mode}-{color}"
```
- **Modes:** `dark`, `light`
- **Colors:** `navy`, `primary`, `success`, `info`, `warning`, `danger`

**Examples:**
- `"sidebar-dark-navy"` - Dark navy (current)
- `"sidebar-light-primary"` - Light blue
- `"sidebar-dark-success"` - Dark green

---

## 🎯 Common Icons

```python
"icons": {
    # Users & Authentication
    "auth.User": "fas fa-user",
    "accounts.User": "fas fa-user-shield",
    "accounts.Profile": "fas fa-id-card",
    "accounts.Role": "fas fa-user-tag",
    
    # Content
    "app.Post": "fas fa-file-alt",
    "app.Article": "fas fa-newspaper",
    "app.Page": "fas fa-file",
    "app.Comment": "fas fa-comments",
    
    # Media
    "app.Image": "fas fa-image",
    "app.Video": "fas fa-video",
    "app.File": "fas fa-file-download",
    
    # Organization
    "app.Category": "fas fa-folder",
    "app.Tag": "fas fa-tags",
    "app.Collection": "fas fa-layer-group",
    
    # Social
    "app.Like": "fas fa-heart",
    "app.Follow": "fas fa-user-friends",
    "app.Share": "fas fa-share-alt",
    
    # Communication
    "app.Notification": "fas fa-bell",
    "app.Message": "fas fa-envelope",
    "app.Chat": "fas fa-comment-dots",
    
    # E-commerce
    "app.Product": "fas fa-shopping-bag",
    "app.Order": "fas fa-shopping-cart",
    "app.Payment": "fas fa-credit-card",
    
    # Analytics
    "app.Analytics": "fas fa-chart-line",
    "app.Report": "fas fa-file-chart",
    "app.Stats": "fas fa-chart-bar",
    
    # Settings
    "app.Settings": "fas fa-cog",
    "app.Config": "fas fa-sliders-h",
    "app.Permission": "fas fa-key",
}
```

---

## 📱 Form Layouts

```python
"changeform_format": "horizontal_tabs"  # Tabs across top
"changeform_format": "vertical_tabs"    # Tabs on left side
"changeform_format": "collapsible"      # Accordion style
"changeform_format": "carousel"         # Slider style
"changeform_format": "single"           # Default single form
```

---

## 🔧 Quick Settings

### Minimal Configuration
```python
JAZZMIN_SETTINGS = {
    "site_title": "My Admin",
    "site_header": "My Site",
}
```

### Full Professional Setup
```python
JAZZMIN_SETTINGS = {
    # Branding
    "site_title": "Vanguard Admin",
    "site_header": "Vanguard",
    "site_brand": "Vanguard Veterans Platform",
    "site_logo": "images/logo.png",
    "welcome_sign": "Welcome Back",
    "copyright": "Your Company © 2025",
    
    # Features
    "show_sidebar": True,
    "navigation_expanded": True,
    "show_ui_builder": True,
    
    # Menu
    "order_with_respect_to": ["accounts", "core", "auth"],
    "icons": {
        "auth.User": "fas fa-user",
    },
    
    # UI
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-navy navbar-dark",
    "sidebar": "sidebar-dark-navy",
    "accent": "accent-primary",
    "theme": "default",
}
```

---

## 🚀 Performance Tips

```python
class OptimizedAdmin(admin.ModelAdmin):
    # Reduce DB queries
    list_select_related = ['user', 'category']
    
    # Limit list view
    list_per_page = 50
    
    # Only show needed fields
    list_display = ['id', 'title', 'status']
    
    # Add search
    search_fields = ['title', 'description']
    
    # Add filters
    list_filter = ['status', 'created_at']
    
    # Optimize change view
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
```

---

## 📋 Common Tasks

### Add Logo
1. Place `logo.png` in `static/images/`
2. Add to settings: `"site_logo": "images/logo.png"`
3. Run: `python manage.py collectstatic`

### Change Colors
1. Click "UI" button in admin (top-right)
2. Try different combinations
3. Copy settings you like
4. Add to `JAZZMIN_UI_TWEAKS` in settings.py

### Add Custom Menu Link
```python
"topmenu_links": [
    {"name": "Home", "url": "admin:index"},
    {"name": "Support", "url": "/support/", "new_window": True},
    {"model": "auth.User"},
    {"app": "yourapp"},
]
```

### Customize Search
```python
"search_model": [
    "auth.User",
    "yourapp.YourModel",
]
```

---

## 🐛 Troubleshooting

**Problem:** Styles not loading  
**Fix:** Clear cache, run `collectstatic`, hard refresh (Ctrl+Shift+R)

**Problem:** Icons not showing  
**Fix:** Check icon name at fontawesome.com, ensure format is `"fas fa-icon-name"`

**Problem:** Changes not saved  
**Fix:** UI Builder is session-only. Copy settings to `settings.py` to make permanent

**Problem:** Jazzmin not appearing  
**Fix:** Ensure `'jazzmin'` is **before** `'django.contrib.admin'` in `INSTALLED_APPS`

---

## 📚 Resources

- Docs: https://django-jazzmin.readthedocs.io/
- Icons: https://fontawesome.com/v5/search?m=free
- Theme: https://adminlte.io/themes/v3/
- GitHub: https://github.com/farridav/django-jazzmin

---

**Current Setup:** Navy blue professional theme with custom Vanguard branding ✅
