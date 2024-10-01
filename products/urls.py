from django.urls import path

from . import views

urlpatterns = [
    # Product Management
    path('products/',
         views.ProductViewSet.as_view({'get': 'list'}), name="product-list"),
    path('products/<int:pk>/',
         views.ProductViewSet.as_view({'get': 'retrieve'}), name="product-detail"),
    path('products/<int:product_id>/reviews/',
         views.ReviewViewSet.as_view({'get': 'list'}), name="review-list"),

    # Review Management
    path('reviews/create/',
         views.ReviewViewSet.as_view({'post': 'create'}), name="review-create"),
    path('reviews/<int:pk>/',
         views.ReviewViewSet.as_view({'get': 'retrieve'}), name="review-detail"),
    path('reviews/update/<int:pk>/',
         views.ReviewViewSet.as_view({'put': 'update'}), name="review-update"),
    path('reviews/delete/<int:pk>/',
         views.ReviewViewSet.as_view({'delete': 'destroy'}), name="review-delete"),

    # Category Management
    path('categories/',
         views.CategoryViewSet.as_view({'get': 'list'}), name="category-list"),
    path('categories/<int:pk>/',
         views.CategoryViewSet.as_view({'get': 'retrieve'}), name="category-detail"),

    # Featured Categories
    path('categories/featured/',
         views.CategoryViewSet.as_view({'get': 'featured'}), name="featured-category-list"),

    # Products by Category
    path('categories/<slug:category_slug>/products/',
         views.CategoryViewSet.as_view({'get': 'products'}), name="products-by-category"),
]
