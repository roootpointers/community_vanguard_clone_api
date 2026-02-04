from rest_framework import serializers
from intel.models import IntelCategory


class IntelCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for IntelCategory CRUD operations.
    """
    
    class Meta:
        model = IntelCategory
        fields = ['uuid', 'name', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate category name uniqueness."""
        # Check if updating
        if self.instance:
            if IntelCategory.objects.exclude(uuid=self.instance.uuid).filter(name__iexact=value).exists():
                raise serializers.ValidationError("Category with this name already exists.")
        else:
            if IntelCategory.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError("Category with this name already exists.")
        return value


class IntelCategoryDetailSerializer(serializers.ModelSerializer):
    """Nested serializer for IntelCategory in Intel posts."""
    class Meta:
        model = IntelCategory
        fields = ['uuid', 'name', 'created_at', 'updated_at']
