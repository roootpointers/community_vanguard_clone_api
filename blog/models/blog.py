import uuid
from django.db import models
from django.utils.text import slugify


class Blog(models.Model):
    """
    Model representing a blog post.
    """
    
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Published', 'Published'),
        ('Archived', 'Archived'),
    ]
    
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text="Blog title")
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="URL-friendly version of title")
    content = models.TextField(help_text="Blog content")
    author = models.CharField(max_length=255, help_text="Author name")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Published',
        help_text="Publication status"
    )
    featured_image = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL to featured image"
    )
    is_mission_genesis = models.BooleanField(
        default=False,
        help_text="Mark as Mission Genesis blog (only one can be active)"
    )
    views_count = models.IntegerField(default=0, help_text="Number of views")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_mission_genesis']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            original_slug = self.slug
            counter = 1
            while Blog.objects.filter(slug=self.slug).exclude(uuid=self.uuid).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Ensure only one Mission Genesis blog
        if self.is_mission_genesis:
            Blog.objects.filter(is_mission_genesis=True).exclude(uuid=self.uuid).update(is_mission_genesis=False)
        
        super().save(*args, **kwargs)
    
    def increment_views(self):
        """Increment the view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    @property
    def excerpt(self):
        """Return first 200 characters of content"""
        if len(self.content) > 200:
            return self.content[:200] + '...'
        return self.content
