from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Standardized success response format
    """
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)


def error_response(message="Error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standardized error response format
    """
    response_data = {
        "success": False,
        "message": message
    }
    if errors:
        response_data["errors"] = errors
    return Response(response_data, status=status_code)


def paginated_response(queryset, serializer_class, request, message="Data retrieved successfully"):
    """
    Standardized paginated response format
    """
    from rest_framework.pagination import PageNumberPagination
    
    paginator = PageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(paginated_queryset, many=True)
    
    return Response({
        "success": True,
        "message": message,
        "count": paginator.page.paginator.count,
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
        "results": serializer.data
    })
