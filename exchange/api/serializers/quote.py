from rest_framework import serializers
from exchange.models import ExchangeQuote, Exchange


class ExchangeQuoteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and managing quote requests.
    """
    
    class Meta:
        model = ExchangeQuote
        fields = [
            'uuid',
            'exchange',
            'user',
            'name',
            'email',
            'description',
            'mini_range',
            'maxi_range',
            'uploaded_files',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'user', 'status', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError({'error': 'Name is required.'})
        return value.strip()
    
    def validate_email(self, value):
        """Validate and normalize email."""
        if not value:
            raise serializers.ValidationError({'error': 'Email is required.'})
        return value.lower()
    
    def validate_description(self, value):
        """Validate description."""
        if not value or not value.strip():
            raise serializers.ValidationError({'error': 'Description is required. Please describe what you need.'})
        
        if len(value) > 500:
            raise serializers.ValidationError({'error': 'Description cannot exceed 500 characters.'})
        
        return value.strip()
    
    def validate_uploaded_files(self, value):
        """Validate uploaded files structure."""
        if value is None:
            return []
        
        if not isinstance(value, list):
            raise serializers.ValidationError({
                'error': 'Uploaded files must be a list.'
            })
        
        # Optional: Validate each file URL
        for file_url in value:
            if not isinstance(file_url, str):
                raise serializers.ValidationError({
                    'error': 'Each file must be a URL string.'
                })
        
        return value


class ExchangeQuoteListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing quote requests.
    """
    exchange_name = serializers.CharField(source='exchange.business_name', read_only=True)
    exchange_logo = serializers.CharField(source='exchange.business_logo', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = ExchangeQuote
        fields = [
            'uuid',
            'exchange',
            'exchange_name',
            'exchange_logo',
            'user',
            'user_name',
            'name',
            'email',
            'description',
            'mini_range',
            'maxi_range',
            'status',
            'created_at',
        ]


class ExchangeQuoteResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for exchange owners to respond to quote requests.
    """
    
    class Meta:
        model = ExchangeQuote
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status."""
        valid_statuses = ['pending', 'approved', 'rejected']
        if value not in valid_statuses:
            raise serializers.ValidationError({
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            })
        return value
