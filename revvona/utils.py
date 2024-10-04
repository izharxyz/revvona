from rest_framework import serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


# This custom serializer will convert the id field to a string for better compatibility with the frontend
class CustomSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'id' in representation:
            representation['id'] = str(representation['id'])
        return representation


def success_response(data, message="Success", status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)


def error_response(message="Error", details=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "message": message,
        "details": details
    }, status=status_code)


# Custom pagination class to order the queryset by updated_at field
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if not queryset.ordered:
            queryset = queryset.order_by('-updated_at')
        return super().paginate_queryset(queryset, request, view)
