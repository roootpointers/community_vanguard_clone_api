from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from accounts.models.user import User
from accounts.api.serializers.existence import ExistenceCheckSerializer


class ExistenceCheckView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            serializer = ExistenceCheckSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                social_id = serializer.validated_data.get('social_id')
                
                is_email = User.objects.filter(email__iexact=email).exists() if email else False
                is_social = User.objects.filter(social_id=social_id).exists() if social_id else False
                
                response = {
                    "success": True,
                    "message": "Existence check completed successfully.",
                    "data": {
                        "is_email": is_email,
                        "is_social": is_social
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "success": False,
                    "message": "Something went wrong.",
                    "errors": serializer.errors
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = {
                "success": False,
                "message": "Something went wrong.",
                "errors": str(e)
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
