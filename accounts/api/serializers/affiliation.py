from rest_framework import serializers
from accounts.models.affiliation import Affiliation


class AffiliationSerializer(serializers.ModelSerializer):
    """
    Serializer for Affiliation model.
    """
    class Meta:
        model = Affiliation
        fields = ['uuid', 'name', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class AffiliationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing affiliations.
    """
    class Meta:
        model = Affiliation
        fields = ['uuid', 'name']
