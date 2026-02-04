from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.api.serializers.update_password import UpdatePasswordSerializer
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class UpdatePasswordViewSet(viewsets.ViewSet):
    """
    ViewSet for updating password of authenticated user.
    Requires current password verification before allowing password change.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    @action(detail=False, methods=['post'], url_path='update')
    def update_password(self, request):
        """
        Update password for authenticated user.
        
        Endpoint: POST /api/accounts/update-password/
        
        Request Body:
        - current_password: User's current password (required)
        - new_password: New password (required)
        - confirm_password: Confirm new password (required)
        
        Returns success message if password updated successfully.
        """
        try:
            serializer = UpdatePasswordSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                user = request.user
                
                # Set the new password
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                logger.info(f"Password updated successfully for user: {user.email}")
                
                response = {
                    'success': True,
                    'message': 'Password updated successfully.',
                    'data': {
                        'email': user.email,
                        'full_name': user.full_name
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            
            logger.error(f"Password update validation failed: {serializer.errors}")
            response = {
                'success': False,
                'message': 'Password update failed.',
                'errors': serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        except ValidationError as e:
            logger.error(f"Validation error during password update: {str(e)}")
            response = {
                'success': False,
                'message': 'Validation error occurred.',
                'errors': str(e)
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error updating password: {str(e)}", exc_info=True)
            response = {
                'success': False,
                'message': 'An error occurred while updating password.',
                'error': str(e)
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
