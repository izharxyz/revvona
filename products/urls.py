from django.urls import path
from .views import ProductListView, ProductDetailView, CategoryListView, FeaturedCategoryListView, ProductByCategoryView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/featured/', FeaturedCategoryListView.as_view(), name='featured-categories'),
    path('categories/<slug:category_slug>/', ProductByCategoryView.as_view(), name='products-by-category'),
]
