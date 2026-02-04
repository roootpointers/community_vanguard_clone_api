from rest_framework import serializers
from donation.models import DonationTarget


class DonationTargetSerializer(serializers.ModelSerializer):
    """Serializer for DonationTarget model"""
    
    month_name = serializers.SerializerMethodField()
    collected_amount = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = DonationTarget
        fields = [
            'uuid',
            'month',
            'year',
            'month_name',
            'target_amount',
            'currency',
            'description',
            'collected_amount',
            'progress_percentage',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'uuid',
            'month_name',
            'collected_amount',
            'progress_percentage',
            'created_at',
            'updated_at',
        ]
    
    def get_month_name(self, obj):
        """Get the name of the month"""
        return obj.get_month_name()
    
    def get_collected_amount(self, obj):
        """Get the total collected amount for this target"""
        return float(obj.get_collected_amount())
    
    def get_progress_percentage(self, obj):
        """Get the progress percentage"""
        return round(obj.get_progress_percentage(), 2)
    
    def validate_month(self, value):
        """Validate month is between 1 and 12"""
        if value < 1 or value > 12:
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value
    
    def validate_year(self, value):
        """Validate year is reasonable"""
        if value < 2000 or value > 2100:
            raise serializers.ValidationError("Year must be between 2000 and 2100.")
        return value
    
    def validate_target_amount(self, value):
        """Validate that target amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Target amount must be greater than zero.")
        return value
