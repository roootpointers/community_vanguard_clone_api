from rest_framework import serializers
from exchange.models import Exchange, ExchangeVerification, ExchangePreviewImage, Category, SubCategory, ExchangeReview, BusinessHours
from accounts.api.serializers.user import UserSerializer
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Avg, Count, Q
from datetime import datetime


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Nested serializer for Category in Exchange."""
    class Meta:
        model = Category
        fields = ['uuid', 'name', 'created_at', 'updated_at']


class SubCategoryDetailSerializer(serializers.ModelSerializer):
    """Nested serializer for SubCategory in Exchange."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = SubCategory
        fields = ['uuid', 'category', 'category_name', 'name', 'created_at', 'updated_at']


class ExchangeVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for exchange verification files (URL-based).
    """
    
    class Meta:
        model = ExchangeVerification
        fields = ['uuid', 'verification_file', 'file_type', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def validate_verification_file(self, value):
        """Validate verification file URL if provided."""
        if value:
            validator = URLValidator()
            try:
                validator(value)
            except DjangoValidationError:
                raise serializers.ValidationError({'error':"Invalid URL format for verification file."})
        return value


class ExchangePreviewImageSerializer(serializers.ModelSerializer):
    """
    Serializer for exchange preview images.
    """
    
    class Meta:
        model = ExchangePreviewImage
        fields = ['uuid', 'image_url', 'order', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def validate_image_url(self, value):
        """Validate image URL if provided."""
        if value:
            validator = URLValidator()
            try:
                validator(value)
            except DjangoValidationError:
                raise serializers.ValidationError({'error':"Invalid URL format for preview image."})
        return value


class BusinessHoursReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for BusinessHours (nested in Exchange)."""
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BusinessHours
        fields = [
            'uuid',
            'day_of_week',
            'day_name',
            'open_time',
            'close_time',
            'is_closed',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']
    
    def get_day_name(self, obj):
        """Get the readable day name."""
        days = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday', 7: 'Sunday'}
        return days.get(obj.day_of_week, '')


class ExchangeSerializer(serializers.ModelSerializer):
    """
    Serializer for Exchange model matching the new screen design.
    """
    verifications = ExchangeVerificationSerializer(many=True, read_only=True)
    preview_images = ExchangePreviewImageSerializer(many=True, read_only=True)
    latest_reviews = serializers.SerializerMethodField()
    exchange_stats = serializers.SerializerMethodField()
    
    # Write-only fields for bulk operations
    verification_urls = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="List of verification file URLs"
    )
    preview_image_urls = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="List of preview image URLs"
    )
    
    # Business hours - accepts list for writing, returns related objects for reading
    operating_hours = BusinessHoursReadSerializer(many=True, read_only=True)
    
    # ForeignKey fields
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    sub_category = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all(), required=False, allow_null=True)
    
    def to_internal_value(self, data):
        """Handle operating_hours input for creation."""
        # Extract operating_hours before validation (since it's read_only in the field definition)
        self._operating_hours_data = data.pop('operating_hours', None) if isinstance(data, dict) else None
        return super().to_internal_value(data)
    
    def to_representation(self, instance):
        """Customize representation to return full user, category and sub_category objects."""
        representation = super().to_representation(instance)
        
        # Replace user UUID with full object
        if instance.user:
            representation['user'] = UserSerializer(instance.user).data
        
        # Replace category UUID with full object
        if instance.category:
            representation['category'] = CategoryDetailSerializer(instance.category).data
        
        # Replace sub_category UUID with full object
        if instance.sub_category:
            representation['sub_category'] = SubCategoryDetailSerializer(instance.sub_category).data
        
        return representation
    
    class Meta:
        model = Exchange
        fields = [
            'uuid',
            'user',
            # Business Information
            'business_name',
            'business_ein',
            'seller_type',
            'category',
            'sub_category',
            # Verification
            'id_me_verified',
            'manual_verification_doc',
            # Business Media
            'business_logo',
            'business_background_image',
            # Mission Statement
            'mission_statement',
            # Contact & Location
            'address',
            'phone',
            'email',
            'website',
            # Offers & Benefits
            'offers_benefits',
            # Social Media
            'facebook',
            'facebook_enabled',
            'twitter',
            'twitter_enabled',
            'instagram',
            'instagram_enabled',
            'linkedin',
            'linkedin_enabled',
            # Status
            'status',
            # Related objects
            'verifications',
            'verification_urls',
            'preview_images',
            'preview_image_urls',
            'operating_hours',
            # Reviews and Stats
            'latest_reviews',
            'exchange_stats',
            'is_active',
            # Timestamps
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'user', 'created_at', 'updated_at']
    
    def validate_email(self, value):
        """Validate email format."""
        if value:
            return value.lower()
        return value
    
    def validate_phone(self, value):
        """Validate phone number."""
        if value:
            # Remove non-numeric characters for validation
            numeric_phone = ''.join(filter(str.isdigit, value))
            if len(numeric_phone) < 10:
                raise serializers.ValidationError({'error': "Phone number must have at least 10 digits."})
        return value
    
    def validate_website(self, value):
        """Validate website URL if provided."""
        if value:
            validator = URLValidator()
            try:
                validator(value)
            except DjangoValidationError:
                raise serializers.ValidationError({'error': "Invalid URL format for website."})
        return value
    
    def validate_business_logo(self, value):
        """Validate business logo URL if provided."""
        if value:
            validator = URLValidator()
            try:
                validator(value)
            except DjangoValidationError:
                raise serializers.ValidationError({'error': "Invalid URL format for business logo."})
        return value
    
    def validate_business_background_image(self, value):
        """Validate business background image URL if provided."""
        if value:
            validator = URLValidator()
            try:
                validator(value)
            except DjangoValidationError:
                raise serializers.ValidationError({'error': "Invalid URL format for background image."})
        return value
    
    def validate_seller_type(self, value):
        """Validate seller type."""
        if value:
            valid_types = [choice[0] for choice in Exchange.SELLER_TYPE_CHOICES]
            if value not in valid_types:
                raise serializers.ValidationError(
                    {'error': f"Invalid seller type. Must be one of: {', '.join(valid_types)}"}
                )
        return value
    
    def validate_mission_statement(self, value):
        """Validate mission statement length."""
        if value and len(value) > 500:
            raise serializers.ValidationError({'error': "Mission statement cannot exceed 500 characters."})
        return value
    
    def validate_offers_benefits(self, value):
        """Validate offers and benefits length."""
        if value and len(value) > 500:
            raise serializers.ValidationError({'error': "Offers and benefits cannot exceed 500 characters."})
        return value
    
    def validate_business_hours(self, value):
        """Validate business hours JSON structure."""
        if value:
            required_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            if not isinstance(value, dict):
                raise serializers.ValidationError({'error': "Business hours must be a JSON object."})
            
            for day in required_days:
                if day in value:
                    day_data = value[day]
                    if not isinstance(day_data, dict):
                        continue
                    
                    # Validate time format if provided
                    if 'open_time' in day_data or 'close_time' in day_data:
                        # Basic validation - can be enhanced
                        pass
        return value
    
    def validate(self, attrs):
        """Object-level validation for category, sub_category, and operating_hours."""
        # Validate operating_hours if provided
        if hasattr(self, '_operating_hours_data') and self._operating_hours_data:
            self._validate_operating_hours(self._operating_hours_data)
        
        category = attrs.get('category')
        sub_category = attrs.get('sub_category')
        
        # If updating, get existing values if not provided
        if self.instance:
            category = category or self.instance.category
            sub_category = sub_category or self.instance.sub_category
        
        # Validate that sub_category belongs to the selected category
        if sub_category and category:
            if sub_category.category != category:
                raise serializers.ValidationError({
                    'error': f"Sub-category '{sub_category.name}' does not belong to category '{category.name}'."
                })
        
        return attrs
    
    def validate_verification_urls(self, value):
        """Validate verification file URLs."""
        if value:
            max_urls = 10
            if len(value) > max_urls:
                raise serializers.ValidationError(
                    {'error': f"Maximum {max_urls} verification URLs allowed."}
                )
            
            # Validate each URL
            validator = URLValidator()
            for url in value:
                try:
                    validator(url)
                except DjangoValidationError:
                    raise serializers.ValidationError(
                        {'error': f"Invalid URL format: {url}"}
                    )
        return value
    
    def validate_preview_image_urls(self, value):
        """Validate preview image URLs."""
        if value:
            max_images = 10
            if len(value) > max_images:
                raise serializers.ValidationError(
                    {'error': f"Maximum {max_images} preview images allowed."}
                )
            
            # Validate each URL
            validator = URLValidator()
            for url in value:
                try:
                    validator(url)
                except DjangoValidationError:
                    raise serializers.ValidationError(
                        {'error': f"Invalid URL format: {url}"}
                    )
        return value
    
    def _validate_operating_hours(self, value):
        """Validate operating hours data."""
        if value:
            for hours in value:
                # Validate required fields
                if 'day_of_week' not in hours:
                    raise serializers.ValidationError(
                        "Each business hour entry must have 'day_of_week' field."
                    )
                
                day_of_week = hours.get('day_of_week')
                is_closed = hours.get('is_closed', False)
                
                # Validate day_of_week
                if not isinstance(day_of_week, int) or day_of_week < 1 or day_of_week > 7:
                    raise serializers.ValidationError(
                        f"Invalid day_of_week: {day_of_week}. Must be 1-7 (1=Monday, 7=Sunday)."
                    )
                
                # If not closed, validate times
                if not is_closed:
                    if 'open_time' not in hours or 'close_time' not in hours:
                        raise serializers.ValidationError(
                            f"Day {day_of_week} (1=Mon, 7=Sun): open_time and close_time are required when not closed."
                        )
                    
                    # Validate time format (HH:MM or HH:MM:SS)
                    open_time = hours.get('open_time')
                    close_time = hours.get('close_time')
                    
                    try:
                        if isinstance(open_time, str):
                            datetime.strptime(open_time, '%H:%M' if len(open_time) <= 5 else '%H:%M:%S')
                        if isinstance(close_time, str):
                            datetime.strptime(close_time, '%H:%M' if len(close_time) <= 5 else '%H:%M:%S')
                    except ValueError as e:
                        raise serializers.ValidationError(
                            f"Invalid time format. Use HH:MM or HH:MM:SS. Error: {str(e)}"
                        )
        
        return value
    
    def create(self, validated_data):
        """Create exchange and associated verification URLs and preview images."""
        verification_urls = validated_data.pop('verification_urls', [])
        preview_image_urls = validated_data.pop('preview_image_urls', [])
        
        # Get operating_hours from the temporary attribute
        operating_hours_data = getattr(self, '_operating_hours_data', None) or []
        
        # Set user from request context if authenticated
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['user'] = request.user
        
        # Set default status to 'under_review' if not provided
        if 'status' not in validated_data:
            validated_data['status'] = 'under_review'
        
        # Create the exchange
        exchange = Exchange.objects.create(**validated_data)
        
        # Create verification entries for each URL
        for url in verification_urls:
            # Determine file type based on URL extension
            file_type = 'photo' if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']) else 'document'
            
            ExchangeVerification.objects.create(
                exchange=exchange,
                verification_file=url,
                file_type=file_type
            )
        
        # Create preview image entries
        for index, url in enumerate(preview_image_urls):
            ExchangePreviewImage.objects.create(
                exchange=exchange,
                image_url=url,
                order=index
            )
        
        # Create business hours entries
        for hours_data in operating_hours_data:
            BusinessHours.objects.create(
                exchange=exchange,
                day_of_week=hours_data['day_of_week'],
                open_time=hours_data.get('open_time'),
                close_time=hours_data.get('close_time'),
                is_closed=hours_data.get('is_closed', False)
            )
        
        return exchange
    
    def update(self, instance, validated_data):
        """Update exchange and optionally add new verification URLs and preview images."""
        verification_urls = validated_data.pop('verification_urls', [])
        preview_image_urls = validated_data.pop('preview_image_urls', [])
        
        # Get operating_hours from the temporary attribute
        operating_hours_data = getattr(self, '_operating_hours_data', None)
        
        # Update exchange fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Add new verification URLs if provided
        for url in verification_urls:
            file_type = 'photo' if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']) else 'document'
            
            ExchangeVerification.objects.create(
                exchange=instance,
                verification_file=url,
                file_type=file_type
            )
        
        # Add new preview images if provided
        if preview_image_urls:
            # Get current max order
            current_max = instance.preview_images.count()
            
            for index, url in enumerate(preview_image_urls):
                ExchangePreviewImage.objects.create(
                    exchange=instance,
                    image_url=url,
                    order=current_max + index
                )
        
        # Update operating hours if provided
        if operating_hours_data is not None:
            # Update or create business hours for each day
            for hours_data in operating_hours_data:
                day_of_week = hours_data['day_of_week']
                
                # Find existing business hours for this day
                existing_hours = instance.operating_hours.filter(day_of_week=day_of_week).first()
                
                if existing_hours:
                    # Update existing record
                    existing_hours.open_time = hours_data.get('open_time')
                    existing_hours.close_time = hours_data.get('close_time')
                    existing_hours.is_closed = hours_data.get('is_closed', False)
                    existing_hours.save()
                else:
                    # Create new record
                    BusinessHours.objects.create(
                        exchange=instance,
                        day_of_week=day_of_week,
                        open_time=hours_data.get('open_time'),
                        close_time=hours_data.get('close_time'),
                        is_closed=hours_data.get('is_closed', False)
                    )
        
        return instance
    
    def get_latest_reviews(self, obj):
        """Return latest 5 reviews for this exchange."""
        from exchange.api.serializers.review import ExchangeReviewListSerializer
        
        latest_reviews = ExchangeReview.objects.filter(
            exchange=obj
        ).select_related('user').order_by('-created_at')[:5]
        
        return ExchangeReviewListSerializer(latest_reviews, many=True).data
    
    def get_exchange_stats(self, obj):
        """Calculate and return exchange review statistics."""
        reviews = ExchangeReview.objects.filter(exchange=obj)
        
        if not reviews.exists():
            return {
                'average_rating': 0,
                'total_reviews': 0,
                'rating_breakdown': {
                    '5': 0,
                    '4': 0,
                    '3': 0,
                    '2': 0,
                    '1': 0
                }
            }
        
        stats = reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('uuid'),
            five_star=Count('uuid', filter=Q(rating=5)),
            four_star=Count('uuid', filter=Q(rating=4)),
            three_star=Count('uuid', filter=Q(rating=3)),
            two_star=Count('uuid', filter=Q(rating=2)),
            one_star=Count('uuid', filter=Q(rating=1))
        )
        
        return {
            'average_rating': round(stats['average_rating'], 2) if stats['average_rating'] else 0,
            'total_reviews': stats['total_reviews'],
            'rating_breakdown': {
                '5': stats['five_star'],
                '4': stats['four_star'],
                '3': stats['three_star'],
                '2': stats['two_star'],
                '1': stats['one_star']
            }
        }


class ExchangeListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing exchanges with latest reviews and stats.
    """
    user = UserSerializer(read_only=True)
    verification = serializers.SerializerMethodField()
    preview_images = ExchangePreviewImageSerializer(many=True, read_only=True)
    category = CategoryDetailSerializer(read_only=True)
    sub_category = SubCategoryDetailSerializer(read_only=True)
    latest_reviews = serializers.SerializerMethodField()
    exchange_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Exchange
        fields = [
            'uuid',
            'user',
            'business_name',
            'business_ein',
            'seller_type',
            'email',
            'phone',
            'address',
            'offers_benefits',
            'category',
            'sub_category',
            'business_logo',
            'business_background_image',
            'mission_statement',
            'status',
            'verification',
            'preview_images',
            'latest_reviews',
            'exchange_stats',
            'is_active',
            'created_at',
            'updated_at',
        ]
    
    def get_verification(self, obj):
        """Return verification files."""
        verifications = obj.verifications.all()
        serializer = ExchangeVerificationSerializer(verifications, many=True)
        return serializer.data
    
    def get_latest_reviews(self, obj):
        """Return latest 5 reviews for this exchange."""
        from exchange.api.serializers.review import ExchangeReviewListSerializer
        
        latest_reviews = ExchangeReview.objects.filter(
            exchange=obj
        ).select_related('user').order_by('-created_at')[:5]
        
        return ExchangeReviewListSerializer(latest_reviews, many=True).data
    
    def get_exchange_stats(self, obj):
        """Calculate and return exchange review statistics."""
        reviews = ExchangeReview.objects.filter(exchange=obj)
        
        if not reviews.exists():
            return {
                'average_rating': 0,
                'total_reviews': 0,
                'rating_breakdown': {
                    '5': 0,
                    '4': 0,
                    '3': 0,
                    '2': 0,
                    '1': 0
                }
            }
        
        stats = reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('uuid'),
            five_star=Count('uuid', filter=Q(rating=5)),
            four_star=Count('uuid', filter=Q(rating=4)),
            three_star=Count('uuid', filter=Q(rating=3)),
            two_star=Count('uuid', filter=Q(rating=2)),
            one_star=Count('uuid', filter=Q(rating=1))
        )
        
        return {
            'average_rating': round(stats['average_rating'], 2) if stats['average_rating'] else 0,
            'total_reviews': stats['total_reviews'],
            'rating_breakdown': {
                '5': stats['five_star'],
                '4': stats['four_star'],
                '3': stats['three_star'],
                '2': stats['two_star'],
                '1': stats['one_star']
            }
        }
