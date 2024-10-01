from django.db.models import QuerySet
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
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


# Pagination Class
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset: QuerySet, request, view=None):
        if queryset.ordered is False:
            queryset = queryset.order_by('-created_at')

        return super().paginate_queryset(queryset, request, view)


# Product ViewSet
class ProductViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    pagination_class = CustomPagination  # Use custom pagination class

    def list_products(self, request):
        try:
            queryset = Product.objects.all()
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            if not paginated_queryset:
                return error_response("No products found.", status_code=status.HTTP_404_NOT_FOUND)

            serializer = ProductSerializer(paginated_queryset, many=True)
            return success_response({
                "results": serializer.data,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link()
            })

        except Exception as e:
            return error_response("An error occurred while listing products.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve_product(self, request, pk=None):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return success_response(serializer.data)
        except Product.DoesNotExist:
            return error_response("Product not found.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while retrieving the product.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Review ViewSet
class ReviewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Allow anyone to list reviews, but require authentication for other actions.
        """
        if self.action == 'list_reviews':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def list_reviews(self, request, product_id=None):
        try:
            product = Product.objects.get(pk=product_id)
            queryset = Review.objects.filter(
                product=product).order_by('-created_at')
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializer = ReviewSerializer(paginated_queryset, many=True)
            return success_response({
                "products": serializer.data,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link()
            })

        except Product.DoesNotExist:
            return error_response('Product not found.', status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while listing reviews.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_review(self, request):
        try:
            product_id = request.data.get('product_id')
            if not product_id:
                return error_response('Product ID is required to create a review.')

            product = Product.objects.get(id=product_id)

            if Review.objects.filter(product=product, user=request.user).exists():
                return error_response('You have already reviewed this product.')

            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, product=product)
                return success_response(serializer.data, "Review created successfully.", status_code=status.HTTP_201_CREATED)

            return error_response("Invalid data.", serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        except Product.DoesNotExist:
            return error_response('Product not found.', status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while creating the review.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_review(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk, user=request.user)
            serializer = ReviewSerializer(review, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_response(serializer.data, "Review updated successfully.")

            return error_response("Invalid data.", serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

        except Review.DoesNotExist:
            return error_response("Review not found or you do not have permission to update it.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while updating the review.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete_review(self, request, pk=None):
        try:
            review = Review.objects.get(pk=pk, user=request.user)
            review.delete()
            return success_response(None, "Review deleted successfully.", status_code=status.HTTP_204_NO_CONTENT)

        except Review.DoesNotExist:
            return error_response("Review not found or you do not have permission to delete it.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while deleting the review.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Category ViewSet
class CategoryViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    pagination_class = CustomPagination  # Use custom pagination class

    def list_categories(self, request):
        try:
            queryset = Category.objects.all()
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            if not paginated_queryset:
                return error_response("No categories found.", status_code=status.HTTP_404_NOT_FOUND)

            serializer = CategorySerializer(paginated_queryset, many=True)
            return success_response({
                "categories": serializer.data,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link()
            })

        except Exception as e:
            return error_response("An error occurred while listing categories.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list_featured_categories(self, request):
        try:
            queryset = Category.objects.filter(featured=True)
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            if not paginated_queryset:
                return error_response("No featured categories found.", status_code=status.HTTP_404_NOT_FOUND)

            serializer = CategorySerializer(paginated_queryset, many=True)
            return success_response({
                "categories": serializer.data,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link()
            })

        except Exception as e:
            return error_response("An error occurred while listing featured categories.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list_products_by_category(self, request, category_slug=None):
        try:
            category = Category.objects.get(slug=category_slug)
            queryset = Product.objects.filter(category=category)

            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            if not paginated_queryset:
                return error_response("No products found in this category.", status_code=status.HTTP_404_NOT_FOUND)

            serializer = ProductSerializer(paginated_queryset, many=True)
            return success_response({
                "products": serializer.data,
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link()
            })

        except Category.DoesNotExist:
            return error_response("Category not found.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while listing products by category.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
