from django.urls import path

from . import views

urlpatterns = [
    # Product Management
    path('products/',
         views.ProductViewSet.as_view({'get': 'list_products'}), name="product-list"),
    path('products/<int:pk>/',
         views.ProductViewSet.as_view({'get': 'retrieve_product'}), name="product-detail"),
    path('products/<int:product_id>/reviews/',
         views.ReviewViewSet.as_view({'get': 'list_reviews'}), name="review-list"),

    # Review Management
    path('reviews/create/',
         views.ReviewViewSet.as_view({'post': 'create_review'}), name="review-create"),
    path('reviews/<int:pk>/',
         views.ReviewViewSet.as_view({'get': 'retrieve_review'}), name="review-detail"),
    path('reviews/<int:pk>/update/',
         views.ReviewViewSet.as_view({'put': 'update_review'}), name="review-update"),
    path('reviews/<int:pk>/delete/',
         views.ReviewViewSet.as_view({'delete': 'delete_review'}), name="review-delete"),

    # Category Management
    path('categories/',
         views.CategoryViewSet.as_view({'get': 'list_categories'}), name="category-list"),
    path('categories/featured/',
         views.CategoryViewSet.as_view({'get': 'list_featured_categories'}), name="featured-category-list"),
    path('categories/<slug:category_slug>/products/',
         views.CategoryViewSet.as_view({'get': 'list_products_by_category'}), name="products-by-category"),
]
