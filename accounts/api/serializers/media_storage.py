from rest_framework import serializers
from accounts.models import MediaStorage
import base64
import re
import uuid
from django.core.files.base import ContentFile


class Base64MediaUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading media files via base64 encoding.
    """
    media = serializers.CharField(required=True, help_text="Base64-encoded data URL (e.g., data:image/png;base64,...)")
    media_type = serializers.ChoiceField(
        choices=['photo', 'document'],
        required=True,
        help_text="Type of media: 'photo' or 'document'"
    )

    # MIME type mappings for validation
    ALLOWED_PHOTO_MIMES = {
        'image/png': '.png',
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/webp': '.webp',
        'image/gif': '.gif',
    }

    ALLOWED_DOCUMENT_MIMES = {
        'application/pdf': '.pdf',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    }

    # Unsafe MIME types to reject
    UNSAFE_MIMES = {
        'application/x-executable',
        'application/x-msdownload',
        'application/x-sh',
        'application/x-shellscript',
        'text/javascript',
        'application/javascript',
        'text/html',
        'application/x-httpd-php',
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def validate_media(self, value):
        """
        Validate the base64 data URL format.
        """
        if not value.startswith('data:'):
            raise serializers.ValidationError("Invalid data URL format. Must start with 'data:'")
        
        return value

    def validate(self, attrs):
        """
        Cross-field validation for media data and type.
        """
        media_data = attrs.get('media')
        media_type = attrs.get('media_type')

        # Parse the data URL
        try:
            # Extract header and base64 data
            if ';base64,' not in media_data:
                raise serializers.ValidationError({
                    'media': "Invalid data URL format. Must contain ';base64,'"
                })

            header, base64_data = media_data.split(';base64,', 1)
            mime_type = header.replace('data:', '')

            # Security check: reject unsafe MIME types
            if mime_type in self.UNSAFE_MIMES:
                raise serializers.ValidationError({
                    'media': f"Unsafe MIME type '{mime_type}' is not allowed"
                })

            # Validate MIME type based on media_type
            if media_type == 'photo':
                if mime_type not in self.ALLOWED_PHOTO_MIMES:
                    allowed = ', '.join(self.ALLOWED_PHOTO_MIMES.keys())
                    raise serializers.ValidationError({
                        'media': f"Invalid MIME type for photo. Allowed types: {allowed}"
                    })
                file_extension = self.ALLOWED_PHOTO_MIMES[mime_type]
            elif media_type == 'document':
                if mime_type not in self.ALLOWED_DOCUMENT_MIMES:
                    allowed = ', '.join(self.ALLOWED_DOCUMENT_MIMES.keys())
                    raise serializers.ValidationError({
                        'media': f"Invalid MIME type for document. Allowed types: {allowed}"
                    })
                file_extension = self.ALLOWED_DOCUMENT_MIMES[mime_type]
            else:
                raise serializers.ValidationError({
                    'media_type': "Invalid media type. Must be 'photo' or 'document'"
                })

            # Decode base64 data
            try:
                decoded_data = base64.b64decode(base64_data, validate=True)
            except Exception as e:
                raise serializers.ValidationError({
                    'media': f"Invalid base64 data: {str(e)}"
                })

            # Check file size
            file_size = len(decoded_data)
            if file_size > self.MAX_FILE_SIZE:
                max_size_mb = self.MAX_FILE_SIZE / (1024 * 1024)
                actual_size_mb = file_size / (1024 * 1024)
                raise serializers.ValidationError({
                    'media': f"File size ({actual_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)"
                })

            # Store parsed data for use in create()
            attrs['_parsed_data'] = {
                'decoded_data': decoded_data,
                'mime_type': mime_type,
                'file_extension': file_extension,
                'file_size': file_size
            }

        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError({
                'media': f"Failed to parse media data: {str(e)}"
            })

        return attrs

    def create(self, validated_data):
        """
        Create a MediaStorage instance from validated base64 data.
        """
        parsed_data = validated_data['_parsed_data']
        media_type = validated_data['media_type']

        # Generate a unique filename
        unique_id = uuid.uuid4().hex[:12]
        filename = f"{media_type}_{unique_id}{parsed_data['file_extension']}"

        # Create a ContentFile from decoded data
        file_content = ContentFile(parsed_data['decoded_data'], name=filename)

        # Create MediaStorage instance
        instance = MediaStorage.objects.create(
            media=file_content,
            media_type=media_type
        )

        return {
            'instance': instance,
            'mime_type': parsed_data['mime_type'],
            'size_bytes': parsed_data['file_size']
        }


class Base64MediaResponseSerializer(serializers.Serializer):
    """
    Serializer for successful media upload response.
    """
    media_type = serializers.CharField()
    mime_type = serializers.CharField()
    size_bytes = serializers.IntegerField()
    url = serializers.URLField()
    status = serializers.CharField(default='saved')


class Base64MediaErrorSerializer(serializers.Serializer):
    """
    Serializer for failed media upload response.
    """
    media_type = serializers.CharField(required=False, allow_null=True)
    error = serializers.CharField()
    status = serializers.CharField(default='failed')
