from rest_framework import serializers
from exchange.models import Category, SubCategory


class SubCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for SubCategory model.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = SubCategory
        fields = [
            'uuid',
            'category',
            'category_name',
            'name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate that name is not empty."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError({'error': "Name cannot be empty."})
        return value.strip()
    
    def validate(self, attrs):
        """Validate unique constraint for category and name."""
        category = attrs.get('category')
        name = attrs.get('name')
        
        if category and name:
            # Check for existing subcategory with same name in same category
            exists = SubCategory.objects.filter(
                category=category,
                name__iexact=name
            )
            
            # Exclude current instance if updating
            if self.instance:
                exists = exists.exclude(uuid=self.instance.uuid)
            
            if exists.exists():
                raise serializers.ValidationError({
                    'error': f"SubCategory '{name}' already exists in this category."
                })
        
        return attrs


class SubCategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing subcategories.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = SubCategory
        fields = ['uuid', 'category', 'category_name', 'name']


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model with nested subcategories.
    """
    subcategories = SubCategoryListSerializer(many=True, read_only=True)
    subcategories_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'uuid',
            'name',
            'subcategories_count',
            'subcategories',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def get_subcategories_count(self, obj):
        """Get count of subcategories."""
        return obj.subcategories.count()
    
    def validate_name(self, value):
        """Validate that name is not empty and unique."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError({'error': "Name cannot be empty."})
        
        # Check uniqueness
        exists = Category.objects.filter(name__iexact=value.strip())
        
        # Exclude current instance if updating
        if self.instance:
            exists = exists.exclude(uuid=self.instance.uuid)
        
        if exists.exists():
            raise serializers.ValidationError({
                'error': f"Category '{value}' already exists."
            })
        
        return value.strip()


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing categories.
    """
    subcategories_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['uuid', 'name', 'subcategories_count']
    
    def get_subcategories_count(self, obj):
        """Get count of subcategories."""
        return obj.subcategories.count()
