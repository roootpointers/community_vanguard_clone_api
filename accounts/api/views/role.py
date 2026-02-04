from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from accounts.models.role import UserRole
from accounts.api.serializers.role import (
    CreateUserRoleSerializer,
    UserRoleSerializer
)
from accounts.api.serializers.user import UserSerializer


class UserRoleViewSet(viewsets.ModelViewSet):
    serializer_class = CreateUserRoleSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ["post", "get", "patch", "put"]
    
    def get_queryset(self):
        """
        Return user roles based on permissions.
        Regular users can only see their own role.
        Admins can see all roles.
        """
        if self.request.user.is_staff or self.request.user.is_superuser:
            return UserRole.objects.select_related('user').all()
        return UserRole.objects.filter(user=self.request.user).select_related('user')
    
    def get_serializer_class(self):
        """
        Use appropriate serializer based on action.
        """
        if self.action == 'list':
            return UserRoleSerializer
        return CreateUserRoleSerializer
    
    @action(detail=False, methods=['post'], url_path='submit')
    def submit_role(self, request, *args, **kwargs):
        """
        Submit/Create a new user role.
        Users can set their role to Customer, Vendor, or Community Support Provider.
        """
        try:
            # Check if user has completed their profile
            if not hasattr(request.user, 'profile'):
                error = {
                    "success": False,
                    "message": "Please complete your profile before setting a role.",
                    "errors": {
                        "profile": "Profile not found. Please set up your profile first."
                    }
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user already has a role
            existing_role = UserRole.objects.filter(user=request.user).first()
            if existing_role:
                error = {
                    "success": False,
                    "message": "You already have a role. Use the update endpoint to modify it.",
                    "data": {
                        "current_role": UserRoleSerializer(existing_role).data
                    }
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(data=request.data)
            
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {
                    "success": False,
                    "message": "Validation failed",
                    "errors": e.args[0] if e.args else str(e)
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            
            # Set is_role=True on the user when role is assigned
            request.user.is_role = True
            request.user.is_profile_completed = True
            request.user.save(update_fields=['is_role', 'is_profile_completed'])
            
            # Prepare response message based on role
            role = serializer.data['role']
            if role == 'customer':
                message = "Your role has been set to Customer."
            elif role == 'vendor':
                message = "Your role has been set to Vendor."
            elif role == 'community_support_provider':
                message = "Your role has been set to Community Support Provider."
            else:
                message = "Role submitted successfully."
            user = request.user
            serializer = UserSerializer(user)
            response = {
                "success": True,
                "message": message,
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            error = {
                "success": False,
                "message": "Failed to submit role",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
    
    @action(detail=False, methods=['put', 'patch'], url_path='my-role/update')
    def update_my_role(self, request, *args, **kwargs):
        """
        Update the current user's role.
        """
        try:
            user_role = UserRole.objects.filter(user=request.user).first()
            
            if not user_role:
                error = {
                    "success": False,
                    "message": "You haven't set a role yet. Please use submit endpoint first.",
                }
                return Response(error, status=status.HTTP_404_NOT_FOUND)
            
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(user_role, data=request.data, partial=partial)
            
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {
                    "success": False,
                    "message": "Validation failed",
                    "errors": e.args[0] if e.args else str(e)
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            user = request.user
            serializer = UserSerializer(user)
            response = {
                "success": True,
                "message": "Role updated successfully",
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            error = {
                "success": False,
                "message": "Failed to update role",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put', 'patch'], url_path='(?P<role_uuid>[^/.]+)/update', permission_classes=[IsAdminUser])
    def update_role_by_uuid(self, request, role_uuid=None, *args, **kwargs):
        """
        Admin endpoint to update any user's role by UUID.
        Only accessible by admin users.
        """
        try:
            try:
                user_role = UserRole.objects.select_related('user').get(uuid=role_uuid)
            except UserRole.DoesNotExist:
                error = {
                    "success": False,
                    "message": "Role not found with the provided UUID.",
                }
                return Response(error, status=status.HTTP_404_NOT_FOUND)
            
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(user_role, data=request.data, partial=partial)
            
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {
                    "success": False,
                    "message": "Validation failed",
                    "errors": e.args[0] if e.args else str(e)
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            
            # Update user flags if needed
            user_role.user.is_role = True
            user_role.user.save(update_fields=['is_role'])
            
            user = user_role.user
            user_serializer = UserSerializer(user)
            response = {
                "success": True,
                "message": f"Role updated successfully for user {user.email}",
                "data": user_serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            error = {
                "success": False,
                "message": "Failed to update role",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    