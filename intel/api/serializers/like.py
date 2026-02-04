from rest_framework import serializers
from intel.models import IntelLike


class IntelLikeSerializer(serializers.ModelSerializer):
    """
    Serializer for Intel likes.
    """
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = IntelLike
        fields = ['uuid', 'user', 'intel', 'created_at']
        read_only_fields = ['uuid', 'user', 'created_at']
    
    def get_user(self, obj):
        """Return basic user info."""
        return {
            'uuid': str(obj.user.uuid),
            'full_name': obj.user.full_name,
            'email': obj.user.email,
        }
