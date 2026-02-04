from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.conf import settings
import logging

from accounts.api.serializers.media_storage import (
    Base64MediaUploadSerializer,
    Base64MediaResponseSerializer,
    Base64MediaErrorSerializer
)

logger = logging.getLogger(__name__)


class Base64MediaUploadViewSet(viewsets.ViewSet):
    """
    ViewSet for uploading media files via base64 encoding.
    Accepts a list of base64-encoded files and returns upload results.
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='uploads')
    def bulk_upload(self, request):
        """
        Upload multiple media files from base64-encoded data.
        
        Expects a JSON array of objects with 'media' (base64 data URL) and 'media_type'.
        Returns an array of results with status for each file.
        """
        try:
            # Validate that request data is a list
            if not isinstance(request.data, list):
                return Response({
                    'success': False,
                    'message': 'Request body must be a JSON array',
                    'error': 'Expected a list of media objects'
                }, status=status.HTTP_400_BAD_REQUEST)

            if len(request.data) == 0:
                return Response({
                    'success': False,
                    'message': 'No media files provided',
                    'error': 'Request array is empty'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Process each item in the list
            results = []
            success_count = 0
            failed_count = 0

            for idx, item in enumerate(request.data):
                try:
                    # Validate and process the item
                    serializer = Base64MediaUploadSerializer(data=item)
                    
                    if not serializer.is_valid():
                        # Item validation failed
                        error_messages = []
                        for field, errors in serializer.errors.items():
                            for error in errors:
                                error_messages.append(f"{field}: {error}")
                        
                        results.append({
                            'media_type': item.get('media_type'),
                            'error': '; '.join(error_messages),
                            'status': 'failed'
                        })
                        failed_count += 1
                        logger.warning(f"Validation failed for item {idx}: {serializer.errors}")
                        continue

                    # Create the media storage instance
                    created_data = serializer.save()
                    instance = created_data['instance']
                    
                    # Build the full URL
                    request_obj = request
                    if hasattr(instance.media, 'url'):
                        media_url = instance.media.url
                        if request_obj and not media_url.startswith('http'):
                            media_url = request_obj.build_absolute_uri(media_url)
                    else:
                        media_url = None

                    # Successful upload
                    results.append({
                        'media_type': instance.media_type,
                        'mime_type': created_data['mime_type'],
                        'size_bytes': created_data['size_bytes'],
                        'url': media_url,
                        'uuid': str(instance.uuid),
                        'status': 'saved'
                    })
                    success_count += 1
                    logger.info(f"Successfully uploaded media item {idx}: {media_url}")

                except Exception as e:
                    # Unexpected error during item processing
                    results.append({
                        'media_type': item.get('media_type'),
                        'error': f"Unexpected error: {str(e)}",
                        'status': 'failed'
                    })
                    failed_count += 1
                    logger.error(f"Error processing item {idx}: {str(e)}", exc_info=True)

            # Determine response status code
            if success_count > 0 and failed_count > 0:
                # Mixed results - some succeeded, some failed
                response_status = status.HTTP_207_MULTI_STATUS
                response_message = f"{success_count} file(s) uploaded successfully, {failed_count} failed"
            elif success_count > 0 and failed_count == 0:
                # All succeeded
                response_status = status.HTTP_201_CREATED
                response_message = f"All {success_count} file(s) uploaded successfully"
            else:
                # All failed
                response_status = status.HTTP_400_BAD_REQUEST
                response_message = f"All {failed_count} file(s) failed to upload"

            return Response({
                'success': success_count > 0,
                'message': response_message,
                'summary': {
                    'total': len(request.data),
                    'succeeded': success_count,
                    'failed': failed_count
                },
                'results': results
            }, status=response_status)

        except Exception as e:
            logger.error(f"Unexpected error in bulk_upload: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'An error occurred while processing the upload request',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """
        Main POST handler - delegates to bulk_upload.
        """
        return self.bulk_upload(request)
