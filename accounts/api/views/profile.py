from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from accounts.models.profile import UserProfile
from accounts.models.media_storage import MediaStorage
from accounts.api.serializers.user import UserSerializer
from accounts.api.serializers.profile import CreateUpdateUserProfileSerializer, UserProfileSerializer
import uuid
import json


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CreateUpdateUserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ["post", "get", "put", "patch"]
    
    def get_queryset(self):
        """
        Return profiles based on user permissions.
        Regular users can only access their own profile.
        """
        if self.request.user.is_staff or self.request.user.is_superuser:
            return UserProfile.objects.select_related('user').all()
        return UserProfile.objects.filter(user=self.request.user).select_related('user')
    
    def get_serializer_class(self):
        """
        Use lightweight serializer for list view.
        """
        if self.action == 'list':
            return UserProfileSerializer
        return CreateUpdateUserProfileSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new profile for the authenticated user.
        """
        try:
            # Check if user already has a profile
            if hasattr(request.user, 'profile'):
                error = {
                    "success": False,
                    "message": "Profile already exists. Use update endpoint instead.",
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
            
            self.perform_create(serializer)
            
            response = {
                "success": True,
                "message": "Profile created successfully",
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            error = {
                "success": False,
                "message": "Failed to create profile",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Update the user's profile (full update).
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {
                    "success": False,
                    "message": "Validation failed",
                    "errors": e.args[0] if e.args else str(e)
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_update(serializer)
            user = request.user
            serializer = UserSerializer(user)
            response = {
                "success": True,
                "message": "Profile updated successfully",
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            error = {
                "success": False,
                "message": "Failed to update profile",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update the user's profile.
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @action(detail=False, methods=['post', 'put', 'patch'], url_path='setup')
    def setup_profile(self, request, *args, **kwargs):
        """
        Complete profile setup endpoint - handles role selection and all profile fields.
        This is the main endpoint for setting up user profile after signup.
        
        Can be used for both creating new profile and updating existing profile.
        Accepts: role, birth_date, gender, branch, rank, location, education, etc.
        
        For verification documents, you can:
        1. Send JSON with verification_documents array containing document_urls
        2. Upload files directly using multipart form data with field names like 'verification_document_0', 'verification_document_1', etc.
        """
        try:
            # Handle file uploads for verification documents
            # Check if files are uploaded via multipart form data
            data = request.data.copy()
            verification_documents = []
            
            # Check if verification_documents is already in JSON format
            if 'verification_documents' in data:
                # Already provided as JSON array
                if isinstance(data.get('verification_documents'), list):
                    verification_documents = data.get('verification_documents')
                elif isinstance(data.get('verification_documents'), str):
                    # Try to parse as JSON string
                    try:
                        verification_documents = json.loads(data.get('verification_documents'))
                    except:
                        pass
            
            # Process uploaded files from request.FILES
            # Look for files with names like 'verification_document', 'verification_document_0', etc.
            uploaded_files = {}
            for key in request.FILES.keys():
                if key.startswith('verification_document'):
                    uploaded_files[key] = request.FILES[key]
            
            # Convert uploaded files to document URLs
            if uploaded_files:
                for key, file_obj in uploaded_files.items():
                    # Create MediaStorage instance for the uploaded file
                    media_storage = MediaStorage.objects.create(
                        media=file_obj,
                        media_type='document'
                    )
                    
                    # Get the URL
                    if hasattr(media_storage.media, 'url'):
                        document_url = media_storage.media.url
                        if not document_url.startswith('http'):
                            document_url = request.build_absolute_uri(document_url)
                    else:
                        document_url = str(media_storage.uuid)
                    
                    # Extract document type from key if provided (e.g., 'verification_document_0_id_card')
                    document_type = ''
                    if '_' in key:
                        parts = key.split('_')
                        if len(parts) > 3:
                            document_type = '_'.join(parts[3:])  # Everything after 'verification_document_X'
                    
                    verification_documents.append({
                        'document_url': document_url,
                        'document_type': document_type
                    })
            
            # Update data with processed verification documents
            if verification_documents:
                data['verification_documents'] = verification_documents
            
            has_profile = hasattr(request.user, 'profile')
            
            if has_profile:
                # Update existing profile
                profile = request.user.profile
                partial = request.method in ['PATCH', 'POST']  # Allow partial updates
                serializer = self.get_serializer(profile, data=data, partial=partial)
            else:
                # Create new profile
                serializer = self.get_serializer(data=data)
            
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as e:
                error = {
                    "success": False,
                    "message": "Validation failed",
                    "errors": e.args[0] if e.args else str(e)
                }
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            
            if has_profile:
                serializer.save()
                message = "Profile updated successfully"
                status_code = status.HTTP_200_OK
            else:
                serializer.save()
                # Set is_profile=True on the user when profile is created
                request.user.is_profile = True
                request.user.save(update_fields=['is_profile'])
                message = "Profile created successfully"
                status_code = status.HTTP_201_CREATED
            
            serializer = UserSerializer(request.user)
            response = {
                "success": True,
                "message": message,
                "data": serializer.data
            }
            return Response(response, status=status_code)
            
        except Exception as e:
            error = {
                "success": False,
                "message": "Failed to setup profile",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='me')
    def get_my_profile(self, request, *args, **kwargs):
        """
        Get the current user's profile.
        """
        try:
            # Check if user has a profile
            if not hasattr(request.user, 'profile'):
                error = {
                    "success": False,
                    "message": "Profile not found. Please create your profile first.",
                    "data": {
                        "has_profile": False
                    }
                }
                return Response(error, status=status.HTTP_404_NOT_FOUND)
            
            user = request.user
            serializer = UserSerializer(user)
            response = {
                "success": True,
                "message": "Profile retrieved successfully",
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            error = {
                "success": False,
                "message": "Failed to retrieve profile",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put', 'patch'], url_path='me/update')
    def update_my_profile(self, request, *args, **kwargs):
        """
        Update the current user's profile.
        """
        try:
            # Check if user has a profile
            if not hasattr(request.user, 'profile'):
                error = {
                    "success": False,
                    "message": "Profile not found. Please create your profile first.",
                }
                return Response(error, status=status.HTTP_404_NOT_FOUND)
            
            partial = request.method == 'PATCH'
            profile = request.user.profile
            
            serializer = self.get_serializer(profile, data=request.data, partial=partial)
            
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
                "message": "Profile updated successfully",
                "data": serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            error = {
                "success": False,
                "message": "Failed to update profile",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='check-completion')
    def check_profile_completion(self, request, *args, **kwargs):
        """
        Check if the current user has completed their profile.
        Returns completion status and percentage.
        """
        try:
            has_profile = hasattr(request.user, 'profile')
            is_completed = False
            completion_percentage = 0
            missing_fields = []
            
            if has_profile:
                profile = request.user.profile
                is_completed = profile.is_profile_completed
                
                # Define required and optional fields with weights
                field_checks = {
                    'role': {'filled': bool(profile.role), 'required': True},
                    'birth_date': {'filled': bool(profile.birth_date), 'required': True},
                    'gender': {'filled': bool(profile.gender), 'required': True},
                    'branch': {'filled': bool(profile.branch), 'required': True},
                    'location': {'filled': bool(profile.location), 'required': True},
                    'education': {'filled': bool(profile.education), 'required': True},
                    'rank': {'filled': bool(profile.rank), 'required': False},
                    'mos_afsc': {'filled': bool(profile.mos_afsc), 'required': False},
                    'interest': {'filled': bool(profile.interest), 'required': False},
                    'affiliation': {'filled': bool(profile.affiliation), 'required': False},
                    'degree': {'filled': bool(profile.degree), 'required': False},
                    'military_civilian_skills': {
                        'filled': bool(profile.military_civilian_skills and len(profile.military_civilian_skills) > 0),
                        'required': False
                    },
                }
                
                # Calculate completion percentage
                total_fields = len(field_checks)
                filled_fields = sum(1 for check in field_checks.values() if check['filled'])
                completion_percentage = int((filled_fields / total_fields) * 100)
                
                # Get missing required fields
                missing_fields = [
                    field for field, check in field_checks.items() 
                    if check['required'] and not check['filled']
                ]
            else:
                missing_fields = ['role', 'birth_date', 'gender', 'branch', 'location', 'education']
            
            response = {
                "success": True,
                "message": "Profile completion status retrieved",
                "data": {
                    "has_profile": has_profile,
                    "is_completed": is_completed,
                    "completion_percentage": completion_percentage,
                    "missing_required_fields": missing_fields
                }
            }
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            error = {
                "success": False,
                "message": "Failed to check profile completion",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='role-info')
    def get_role_info(self, request, *args, **kwargs):
        """
        Get information about available roles and their descriptions.
        """
        try:
            roles_info = [
                {
                    "value": "customer",
                    "label": "Customer (General User)",
                    "description": "Military community members or supporters who browse, search, and connect with veteran-owned products or free support resources."
                },
                {
                    "value": "vendor",
                    "label": "Vendor (Paid Business)",
                    "description": "Verified veteran- or spouse-owned business offering purpose-driven products and services to the military community and its supporters."
                },
                {
                    "value": "community_support_provider",
                    "label": "Community Support Provider (VSO / Non-Profit)",
                    "description": "Verified veteran- or spouse-owned business offering purpose-driven products and services to the military community and its supporters."
                }
            ]
            
            response = {
                "success": True,
                "message": "Role information retrieved",
                "data": {
                    "roles": roles_info
                }
            }
            return Response(response, status=status.HTTP_200_OK)
            
        except Exception as e:
            error = {
                "success": False,
                "message": "Failed to get role information",
                "errors": str(e)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
