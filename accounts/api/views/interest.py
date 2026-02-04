from rest_framework import generics, permissions, status
from rest_framework.response import Response
from accounts.models.interest import Interest
from accounts.api.serializers.interest import InterestListSerializer, InterestSerializer
from accounts.api.utils import CommonPagination
from django.shortcuts import get_object_or_404


class InterestListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint to list all interests or create a new interest.
    
    GET /api/accounts/interests/ - List all interests (AllowAny)
    POST /api/accounts/interests/ - Create new interest (Admin only)
    """
    queryset = Interest.objects.all()
    pagination_class = CommonPagination
    
    def get_serializer_class(self):
        """Use different serializers for list and create operations."""
        if self.request.method == 'POST':
            return InterestSerializer
        return InterestListSerializer
    
    def get_permissions(self):
        """Allow anyone to list, but only admins to create."""
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def get(self, request, *args, **kwargs):
        """Return a paginated list of all interests."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Interests retrieved successfully',
            'data': serializer.data
        })
    
    def post(self, request, *args, **kwargs):
        """Create a new interest."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Interest created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Failed to create interest',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class InterestDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific interest.
    
    GET /api/accounts/interests/{uuid}/ - Retrieve interest (AllowAny)
    PUT /api/accounts/interests/{uuid}/ - Update interest (Admin only)
    PATCH /api/accounts/interests/{uuid}/ - Partial update (Admin only)
    DELETE /api/accounts/interests/{uuid}/ - Delete interest (Admin only)
    """
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    lookup_field = 'uuid'
    
    def get_permissions(self):
        """Allow anyone to retrieve, but only admins to update/delete."""
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def get(self, request, *args, **kwargs):
        """Retrieve a specific interest."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Interest retrieved successfully',
            'data': serializer.data
        })
    
    def put(self, request, *args, **kwargs):
        """Update an interest (full update)."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Interest updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update interest',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        """Partially update an interest."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Interest updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update interest',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        """Delete an interest."""
        instance = self.get_object()
        interest_name = instance.name
        instance.delete()
        return Response({
            'success': True,
            'message': f'Interest "{interest_name}" deleted successfully',
            'data': None
        }, status=status.HTTP_200_OK)
