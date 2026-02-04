import uuid
from django.db import models


class Category(models.Model):
    """
    Category model for organizing exchanges.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        ordering = ['name']
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """
    SubCategory model for detailed categorization within categories.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=255)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sub_categories'
        ordering = ['category__name', 'name']
        verbose_name_plural = 'SubCategories'
        unique_together = [['category', 'name']]
        indexes = [
            models.Index(fields=['category', 'name']),
        ]
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"
