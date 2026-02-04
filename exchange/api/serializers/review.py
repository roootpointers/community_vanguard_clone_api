from rest_framework import serializers
from exchange.models import ExchangeReview
from accounts.api.serializers.user import UserSerializer


class ExchangeReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating exchange reviews.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ExchangeReview
        fields = [
            'uuid',
            'exchange',
            'user',
            'rating',
            'review_text',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'user', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError({'error': 'Rating must be between 1 and 5 stars.'})
        return value
    
    def validate_review_text(self, value):
        """Validate review text length."""
        if value and len(value) > 500:
            raise serializers.ValidationError({'error': 'Review text cannot exceed 500 characters.'})
        return value
    
    def validate(self, attrs):
        """Check if user already reviewed this exchange."""
        request = self.context.get('request')
        exchange = attrs.get('exchange')
        
        # Only check for duplicates on create (not update)
        if not self.instance and request and exchange:
            existing_review = ExchangeReview.objects.filter(
                exchange=exchange,
                user=request.user
            ).exists()
            
            if existing_review:
                raise serializers.ValidationError({
                    'error': 'You have already submitted a review for this exchange.'
                })
        
        return attrs


class ExchangeReviewListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing reviews.
    """
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = ExchangeReview
        fields = [
            'uuid',
            'user',
            'rating',
            'review_text',
            'created_at',
            'updated_at',
        ]
    
    def get_user(self, obj):
        """Return limited user info for privacy."""
        return {
            'uuid': str(obj.user.uuid),
            'full_name': obj.user.full_name or 'Anonymous',
            'email': obj.user.email[:3] + '***@' + obj.user.email.split('@')[1] if obj.user.email else None
        }
