from django.urls import path

from .views import (CategoryListView, FeaturedCategoryListView,
                    ProductByCategoryView, ProductDetailView, ProductListView,
                    ReviewCreateView, ReviewDeleteView, ReviewUpdateView)

urlpatterns = [
    path('products/', ProductListView.as_view(), name='products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/featured/', FeaturedCategoryListView.as_view(),
         name='featured-categories'),
    path('categories/<slug:category_slug>/',
         ProductByCategoryView.as_view(), name='products-by-category'),

    path('review/create/', ReviewCreateView.as_view(), name='create-review'),
    path('review/<int:pk>/update/',
         ReviewUpdateView.as_view(), name='update-review'),
    path('review/<int:pk>/delete/',
         ReviewDeleteView.as_view(), name='delete-review'),
]
