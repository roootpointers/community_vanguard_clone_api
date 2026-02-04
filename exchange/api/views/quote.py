from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from exchange.models import ExchangeQuote, Exchange
from exchange.api.serializers.quote import (
    ExchangeQuoteSerializer,
    ExchangeQuoteListSerializer,
    ExchangeQuoteResponseSerializer
)
from exchange.api.pagination import StandardPagination
from django.db.models import Q


class ExchangeQuoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing quote requests.
    """
    queryset = ExchangeQuote.objects.all()
    serializer_class = ExchangeQuoteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    lookup_field = 'uuid'
    
    def get_queryset(self):
        """Filter quotes based on user role and query params."""
        user = self.request.user
        queryset = ExchangeQuote.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by exchange
        exchange_uuid = self.request.query_params.get('exchange', None)
        if exchange_uuid:
            queryset = queryset.filter(exchange__uuid=exchange_uuid)
        
        # Regular users see only their quotes
        # Exchange owners see quotes for their exchanges
        if not user.is_staff and not user.is_superuser:
            queryset = queryset.filter(
                Q(user=user) | Q(exchange__user=user)
            )
        
        return queryset.select_related('exchange', 'user')
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action."""
        if self.action == 'list':
            return ExchangeQuoteListSerializer
        elif self.action == 'respond_to_quote':
            return ExchangeQuoteResponseSerializer
        return ExchangeQuoteSerializer
    
    def create(self, request, *args, **kwargs):
        """Create quote request with custom response format."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quote = serializer.save(user=request.user)
        
        return Response({
            'success': True,
            'message': 'Quote Request Submitted Successfully',
            'data': ExchangeQuoteSerializer(quote).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_quotes(self, request):
        """
        Get all quote requests sent by the current user.
        These are quotes the user has requested from exchanges.
        
        Query params:
        - status: Filter by quote status (pending, approved, rejected)
        """
        quotes = ExchangeQuote.objects.filter(
            user=request.user
        ).select_related('exchange', 'user').order_by('-created_at')
        
        # Filter by status if provided
        status_filter = request.query_params.get('status', None)
        if status_filter:
            quotes = quotes.filter(status=status_filter)
        
        serializer = ExchangeQuoteListSerializer(quotes, many=True)
        
        return Response({
            'success': True,
            'message': 'Sent quote requests retrieved successfully',
            'count': quotes.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def exchange_quotes(self, request):
        """
        Get all quote requests received on the current user's exchanges.
        These are quotes other users have requested from exchanges owned by this user.
        
        Query params:
        - exchange: Filter by specific exchange UUID
        - status: Filter by quote status (pending, approved, rejected)
        """
        user_exchanges = Exchange.objects.filter(user=request.user)
        
        if not user_exchanges.exists():
            return Response({
                'success': True,
                'message': 'You do not own any exchanges yet.',
                'count': 0,
                'next': None,
                'previous': None,
                'results': []
            })
        
        quotes = ExchangeQuote.objects.filter(
            exchange__in=user_exchanges
        ).select_related('exchange', 'user').order_by('-created_at')
        
        # Filter by specific exchange if provided
        exchange_uuid = request.query_params.get('exchange', None)
        if exchange_uuid:
            quotes = quotes.filter(exchange__uuid=exchange_uuid)
        
        # Filter by status if provided
        status_filter = request.query_params.get('status', None)
        if status_filter:
            quotes = quotes.filter(status=status_filter)
        
        serializer = ExchangeQuoteListSerializer(quotes, many=True)
        
        return Response({
            'success': True,
            'message': 'Received quote requests retrieved successfully',
            'count': quotes.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        })
    
    @action(detail=True, methods=['patch'])
    def respond_to_quote(self, request, uuid=None):
        """
        Exchange owner responds to a quote request.
        Can provide response message, quoted amount, and update status.
        """
        quote = self.get_object()
        
        # Check permissions - only exchange owner or staff
        if not (request.user.is_staff or 
                request.user.is_superuser or 
                quote.exchange.user == request.user):
            return Response(
                {
                    'success': False,
                    'message': 'You do not have permission to respond to this quote.'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ExchangeQuoteResponseSerializer(
            quote, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Quote response submitted successfully',
                'data': ExchangeQuoteSerializer(quote).data
            })
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, uuid=None):
        """
        Update quote request status.
        Only exchange owner or staff can update status.
        """
        quote = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {
                    'success': False,
                    'message': 'Status field is required.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        valid_statuses = ['pending', 'approved', 'rejected']
        if new_status not in valid_statuses:
            return Response(
                {
                    'success': False,
                    'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        if not (request.user.is_staff or 
                request.user.is_superuser or 
                quote.exchange.user == request.user):
            return Response(
                {
                    'success': False,
                    'message': 'You do not have permission to update this quote status.'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        quote.status = new_status
        quote.save()
        
        return Response({
            'success': True,
            'message': 'Quote status updated successfully',
            'data': ExchangeQuoteSerializer(quote).data
        })
