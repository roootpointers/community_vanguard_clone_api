from rest_framework import serializers

class ExistenceCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True, max_length=255)
    social_id = serializers.CharField(required=False, allow_blank=True, max_length=255)


    def validate(self, data):
        if not data.get('email') or not data.get('social_id'):
            raise serializers.ValidationError({'error': "At least one of 'email' or 'social_id' must be provided."})
        return data
