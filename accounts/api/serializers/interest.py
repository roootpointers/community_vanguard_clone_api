from rest_framework import serializers
from accounts.models.interest import Interest


class InterestSerializer(serializers.ModelSerializer):
    """
    Serializer for Interest model.
    Used for listing and creating interests.
    """
    class Meta:
        model = Interest
        fields = ['uuid', 'name', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class InterestListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing interests.
    Only includes essential fields.
    """
    class Meta:
        model = Interest
        fields = ['uuid', 'name']
