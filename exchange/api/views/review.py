from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg, Count, Q
import logging

from exchange.models import ExchangeReview, Exchange
from exchange.api.serializers.review import ExchangeReviewSerializer, ExchangeReviewListSerializer
from exchange.api.pagination import StandardPagination

logger = logging.getLogger(__name__)


class ExchangeReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing exchange reviews.
    
    Endpoints:
    - POST /api/exchange-reviews/ - Submit a review
    - GET /api/exchange-reviews/ - List all reviews
    - GET /api/exchange-reviews/{uuid}/ - Get specific review
    - PATCH /api/exchange-reviews/{uuid}/ - Update own review
    - DELETE /api/exchange-reviews/{uuid}/ - Delete own review
    - GET /api/exchange-reviews/exchange/{exchange_uuid}/ - Get reviews for specific exchange
    - GET /api/exchange-reviews/my-reviews/ - Get authenticated user's reviews
    """
    queryset = ExchangeReview.objects.select_related('user', 'exchange').all()
    serializer_class = ExchangeReviewSerializer
    pagination_class = StandardPagination
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve', 'exchange_reviews']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Use list serializer for list actions."""
        if self.action in ['list', 'exchange_reviews', 'my_reviews']:
            return ExchangeReviewListSerializer
        return ExchangeReviewSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Submit a new review for an exchange.
        
        Request body:
        {
            "exchange": "exchange-uuid",
            "rating": 5,
            "review_text": "Great service!"
        }
        """
        try:
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                # Verify exchange exists
                exchange_uuid = request.data.get('exchange')
                try:
                    exchange = Exchange.objects.get(uuid=exchange_uuid)
                except Exchange.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'Exchange not found.',
                        'errors': {'exchange': ['Exchange does not exist.']}
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Save review with authenticated user
                review = serializer.save(user=request.user)
                
                logger.info(f"Review created by {request.user.email} for {exchange.business_name}")
                
                # Get updated exchange stats
                review_stats = ExchangeReview.objects.filter(exchange=exchange).aggregate(
                    average_rating=Avg('rating'),
                    total_reviews=Count('uuid')
                )
                
                return Response({
                    'success': True,
                    'message': 'Review submitted successfully',
                    'data': ExchangeReviewSerializer(review).data,
                    'exchange_stats': {
                        'average_rating': round(review_stats['average_rating'], 1) if review_stats['average_rating'] else 0,
                        'total_reviews': review_stats['total_reviews']
                    }
                }, status=status.HTTP_201_CREATED)
            
            logger.warning(f"Review validation errors: {serializer.errors}")
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating review: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to create review',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self, request, *args, **kwargs):
        """List all reviews with pagination."""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
            
            serializer = self.get_serializer(paginated_queryset, many=True)
            
            response = paginator.get_paginated_response(serializer.data)
            response.data['message'] = 'Reviews retrieved successfully'
            
            return response
            
        except Exception as e:
            logger.error(f"Error listing reviews: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve reviews',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Get specific review details."""
        try:
            instance = self.get_object()
            serializer = ExchangeReviewSerializer(instance)
            
            return Response({
                'success': True,
                'message': 'Review retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ExchangeReview.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Review not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving review: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve review',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Update own review (full update)."""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            # Check if user is the review owner
            if instance.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You can only update your own reviews'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                serializer.save()
                
                logger.info(f"Review updated by {request.user.email}")
                
                return Response({
                    'success': True,
                    'message': 'Review updated successfully',
                    'data': ExchangeReviewSerializer(instance).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error updating review: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to update review',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Delete own review."""
        try:
            instance = self.get_object()
            
            # Check if user is the review owner
            if instance.user != request.user:
                return Response({
                    'success': False,
                    'message': 'You can only delete your own reviews'
                }, status=status.HTTP_403_FORBIDDEN)
            
            exchange_name = instance.exchange.business_name
            instance.delete()
            
            logger.info(f"Review deleted by {request.user.email} for {exchange_name}")
            
            return Response({
                'success': True,
                'message': 'Review deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting review: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to delete review',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='exchange/(?P<exchange_uuid>[^/.]+)')
    def exchange_reviews(self, request, exchange_uuid=None):
        """
        Get all reviews for a specific exchange with statistics.
        
        Endpoint: GET /api/exchange-reviews/exchange/{exchange_uuid}/
        """
        try:
            # Verify exchange exists
            try:
                exchange = Exchange.objects.get(uuid=exchange_uuid)
            except Exchange.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Exchange not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get reviews for this exchange
            queryset = ExchangeReview.objects.filter(
                exchange=exchange
            ).select_related('user').order_by('-created_at')
            
            # Get statistics
            review_stats = queryset.aggregate(
                average_rating=Avg('rating'),
                total_reviews=Count('uuid'),
                five_star=Count('uuid', filter=Q(rating=5)),
                four_star=Count('uuid', filter=Q(rating=4)),
                three_star=Count('uuid', filter=Q(rating=3)),
                two_star=Count('uuid', filter=Q(rating=2)),
                one_star=Count('uuid', filter=Q(rating=1)),
            )
            
            # Paginate reviews
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
            
            serializer = self.get_serializer(paginated_queryset, many=True)
            
            response = paginator.get_paginated_response(serializer.data)
            response.data['message'] = f'Reviews for {exchange.business_name} retrieved successfully'
            response.data['exchange'] = {
                'uuid': str(exchange.uuid),
                'business_name': exchange.business_name,
                'business_logo': exchange.business_logo
            }
            response.data['statistics'] = {
                'average_rating': round(review_stats['average_rating'], 1) if review_stats['average_rating'] else 0,
                'total_reviews': review_stats['total_reviews'],
                'rating_breakdown': {
                    '5': review_stats['five_star'],
                    '4': review_stats['four_star'],
                    '3': review_stats['three_star'],
                    '2': review_stats['two_star'],
                    '1': review_stats['one_star'],
                }
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error retrieving exchange reviews: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve exchange reviews',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='my-reviews')
    def my_reviews(self, request):
        """
        Get all reviews by the authenticated user.
        
        Endpoint: GET /api/exchange-reviews/my-reviews/
        """
        try:
            queryset = ExchangeReview.objects.filter(
                user=request.user
            ).select_related('exchange').order_by('-created_at')
            
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
            
            serializer = self.get_serializer(paginated_queryset, many=True)
            
            response = paginator.get_paginated_response(serializer.data)
            response.data['message'] = 'Your reviews retrieved successfully'
            
            return response
            
        except Exception as e:
            logger.error(f"Error retrieving user reviews: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to retrieve your reviews',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
