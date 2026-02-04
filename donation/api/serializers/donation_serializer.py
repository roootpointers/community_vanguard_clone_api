from rest_framework import serializers
from donation.models import Donation


class DonationSerializer(serializers.ModelSerializer):
    """Serializer for Donation model with full details"""
    
    formatted_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Donation
        fields = [
            'uuid',
            'donor_name',
            'donor_email',
            'amount',
            'currency',
            'method',
            'month',
            'year',
            'notes',
            'formatted_amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at', 'formatted_amount']
    
    def validate_amount(self, value):
        """Validate that amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value
    
    def validate_month(self, value):
        """Validate month is between 1 and 12"""
        if value is not None and (value < 1 or value > 12):
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value
    
    def validate_year(self, value):
        """Validate year is reasonable"""
        if value is not None and (value < 2000 or value > 2100):
            raise serializers.ValidationError("Year must be between 2000 and 2100.")
        return value


class DonationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing donations"""
    
    formatted_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = Donation
        fields = [
            'uuid',
            'donor_name',
            'amount',
            'currency',
            'method',
            'formatted_amount',
            'created_at',
        ]
        read_only_fields = fields
