"""
Network statistics serializers
"""
from rest_framework import serializers


class UserNetworkStatsSerializer(serializers.Serializer):
    """
    Serializer for user network statistics
    """
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.BooleanField(read_only=True, required=False)
    is_follower = serializers.BooleanField(read_only=True, required=False)
