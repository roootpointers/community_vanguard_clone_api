from rest_framework import serializers
from accounts.models.preferred_contribution_path import PreferredContributionPath


class PreferredContributionPathSerializer(serializers.ModelSerializer):
    """
    Serializer for PreferredContributionPath model.
    """
    class Meta:
        model = PreferredContributionPath
        fields = ['uuid', 'name', 'created_at', 'updated_at']
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class PreferredContributionPathListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing contribution paths.
    """
    class Meta:
        model = PreferredContributionPath
        fields = ['uuid', 'name']
