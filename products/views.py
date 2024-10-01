from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Category, Product, Review
from .serializers import (CategorySerializer, ProductSerializer,
                          ReviewSerializer)


### Helper Functions for Consistent Responses ###
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


# Product ViewSet
class ProductViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list_products(self, request):
        limit = request.query_params.get('limit')
        skip = request.query_params.get('skip')
        queryset = Product.objects.all()

        # Apply skip parameter (offset)
        if skip is not None:
            try:
                skip = int(skip)
                queryset = queryset[skip:]
            except ValueError:
                return error_response("Invalid skip value. It must be an integer.", status_code=status.HTTP_400_BAD_REQUEST)

        # Apply limit parameter
        if limit is not None:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                return error_response("Invalid limit value. It must be an integer.", status_code=status.HTTP_400_BAD_REQUEST)

        if not queryset.exists():
            return error_response("No products found.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(queryset, many=True)
        return success_response(serializer.data)

    def retrieve_product(self, request, pk=None):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return success_response(serializer.data)
        except Product.DoesNotExist:
            return error_response("Product not found.", status_code=status.HTTP_404_NOT_FOUND)


# Review ViewSet
class ReviewViewSet(viewsets.ViewSet):

    def get_permissions(self):
        """
        Allow anyone to list reviews, but require authentication for other actions.
        """
        if self.action == 'list_reviews':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def list_reviews(self, request, product_id=None):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return error_response('Product not found.', status_code=status.HTTP_404_NOT_FOUND)

        limit = request.query_params.get('limit', 5)
        skip = request.query_params.get('skip', 0)

        try:
            limit = int(limit)
            skip = int(skip)
        except ValueError:
            return error_response('Invalid limit or skip parameter. Must be integers.')

        queryset = Review.objects.filter(product=product).order_by(
            '-created_at')[skip:skip + limit]
        serializer = ReviewSerializer(queryset, many=True)

        return success_response({
            'count': Review.objects.filter(product_id=product_id).count(),
            'reviews': serializer.data
        })

    def create_review(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return error_response('Product ID is required to create a review.')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return error_response('Product not found.')

        if Review.objects.filter(product=product, user=request.user).exists():
            return error_response('You have already reviewed this product.')

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return success_response(serializer.data, "Review created successfully.", status_code=status.HTTP_201_CREATED)
        return error_response("Invalid data.", serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    def update_review(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk, user=request.user)
        except Review.DoesNotExist:
            return error_response("Review not found or you do not have permission to update it.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, "Review updated successfully.")
        return error_response("Invalid data.", serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

    def delete_review(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk, user=request.user)
            review.delete()
            return success_response(None, "Review deleted successfully.", status_code=status.HTTP_204_NO_CONTENT)
        except Review.DoesNotExist:
            return error_response("Review not found or you do not have permission to delete it.", status_code=status.HTTP_404_NOT_FOUND)


# Category ViewSet
class CategoryViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list_categories(self, request):
        queryset = Category.objects.all()
        if not queryset.exists():
            return error_response("No categories found.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(queryset, many=True)
        return success_response(serializer.data)

    def list_featured_categories(self, request):
        queryset = Category.objects.filter(featured=True)
        if not queryset.exists():
            return error_response("No featured categories found.", status_code=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(queryset, many=True)
        return success_response(serializer.data)

    def list_products_by_category(self, request, category_slug=None):
        try:
            category = Category.objects.get(slug=category_slug)
            queryset = Product.objects.filter(category=category)

            if not queryset.exists():
                return error_response("No products found in this category.", status_code=status.HTTP_404_NOT_FOUND)

            # Get limit and skip from request parameters, with defaults
            limit = request.query_params.get('limit', 10)
            skip = request.query_params.get('skip', 0)

            try:
                limit = int(limit)
                skip = int(skip)
            except ValueError:
                return error_response("Invalid limit or skip parameter. Must be integers.")

            # Paginate the queryset
            paginated_queryset = queryset[skip:skip + limit]

            serializer = ProductSerializer(paginated_queryset, many=True)

            return success_response({
                "count": queryset.count(),  # Total products in the category
                "products": serializer.data
            })

        except Category.DoesNotExist:
            return error_response("Category not found.", status_code=status.HTTP_404_NOT_FOUND)
