from rest_framework import generics, permissions, status
from rest_framework.response import Response
from accounts.models.preferred_contribution_path import PreferredContributionPath
from accounts.api.serializers.preferred_contribution_path import PreferredContributionPathListSerializer, PreferredContributionPathSerializer
from accounts.api.utils import CommonPagination
from django.shortcuts import get_object_or_404


class PreferredContributionPathListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint to list all preferred contribution paths or create a new path.
    
    GET /api/accounts/preferred-contribution-paths/ - List all paths (AllowAny)
    POST /api/accounts/preferred-contribution-paths/ - Create new path (Admin only)
    """
    queryset = PreferredContributionPath.objects.all()
    pagination_class = CommonPagination
    
    def get_serializer_class(self):
        """Use different serializers for list and create operations."""
        if self.request.method == 'POST':
            return PreferredContributionPathSerializer
        return PreferredContributionPathListSerializer
    
    def get_permissions(self):
        """Allow anyone to list, but only admins to create."""
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def get(self, request, *args, **kwargs):
        """Return a paginated list of all preferred contribution paths."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Preferred contribution paths retrieved successfully',
            'data': serializer.data
        })
    
    def post(self, request, *args, **kwargs):
        """Create a new preferred contribution path."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Preferred contribution path created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Failed to create preferred contribution path',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PreferredContributionPathDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific preferred contribution path.
    
    GET /api/accounts/preferred-contribution-paths/{uuid}/ - Retrieve path (AllowAny)
    PUT /api/accounts/preferred-contribution-paths/{uuid}/ - Update path (Admin only)
    PATCH /api/accounts/preferred-contribution-paths/{uuid}/ - Partial update (Admin only)
    DELETE /api/accounts/preferred-contribution-paths/{uuid}/ - Delete path (Admin only)
    """
    queryset = PreferredContributionPath.objects.all()
    serializer_class = PreferredContributionPathSerializer
    lookup_field = 'uuid'
    
    def get_permissions(self):
        """Allow anyone to retrieve, but only admins to update/delete."""
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def get(self, request, *args, **kwargs):
        """Retrieve a specific preferred contribution path."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Preferred contribution path retrieved successfully',
            'data': serializer.data
        })
    
    def put(self, request, *args, **kwargs):
        """Update a preferred contribution path (full update)."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Preferred contribution path updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update preferred contribution path',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        """Partially update a preferred contribution path."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Preferred contribution path updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update preferred contribution path',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        """Delete a preferred contribution path."""
        instance = self.get_object()
        path_name = instance.name
        instance.delete()
        return Response({
            'success': True,
            'message': f'Preferred contribution path "{path_name}" deleted successfully',
            'data': None
        }, status=status.HTTP_200_OK)
