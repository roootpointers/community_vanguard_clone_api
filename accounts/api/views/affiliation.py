from rest_framework import generics, permissions, status
from rest_framework.response import Response
from accounts.models.affiliation import Affiliation
from accounts.api.serializers.affiliation import AffiliationListSerializer, AffiliationSerializer
from accounts.api.utils import CommonPagination
from django.shortcuts import get_object_or_404


class AffiliationListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint to list all affiliations or create a new affiliation.
    
    GET /api/accounts/affiliations/ - List all affiliations (AllowAny)
    POST /api/accounts/affiliations/ - Create new affiliation (Admin only)
    """
    queryset = Affiliation.objects.all()
    pagination_class = CommonPagination
    
    def get_serializer_class(self):
        """Use different serializers for list and create operations."""
        if self.request.method == 'POST':
            return AffiliationSerializer
        return AffiliationListSerializer
    
    def get_permissions(self):
        """Allow anyone to list, but only admins to create."""
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def get(self, request, *args, **kwargs):
        """Return a paginated list of all affiliations."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'message': 'Affiliations retrieved successfully',
            'data': serializer.data
        })
    
    def post(self, request, *args, **kwargs):
        """Create a new affiliation."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Affiliation created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Failed to create affiliation',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class AffiliationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a specific affiliation.
    
    GET /api/accounts/affiliations/{uuid}/ - Retrieve affiliation (AllowAny)
    PUT /api/accounts/affiliations/{uuid}/ - Update affiliation (Admin only)
    PATCH /api/accounts/affiliations/{uuid}/ - Partial update (Admin only)
    DELETE /api/accounts/affiliations/{uuid}/ - Delete affiliation (Admin only)
    """
    queryset = Affiliation.objects.all()
    serializer_class = AffiliationSerializer
    lookup_field = 'uuid'
    
    def get_permissions(self):
        """Allow anyone to retrieve, but only admins to update/delete."""
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]
    
    def get(self, request, *args, **kwargs):
        """Retrieve a specific affiliation."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'message': 'Affiliation retrieved successfully',
            'data': serializer.data
        })
    
    def put(self, request, *args, **kwargs):
        """Update an affiliation (full update)."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Affiliation updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update affiliation',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, *args, **kwargs):
        """Partially update an affiliation."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Affiliation updated successfully',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Failed to update affiliation',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        """Delete an affiliation."""
        instance = self.get_object()
        affiliation_name = instance.name
        instance.delete()
        return Response({
            'success': True,
            'message': f'Affiliation "{affiliation_name}" deleted successfully',
            'data': None
        }, status=status.HTTP_200_OK)
