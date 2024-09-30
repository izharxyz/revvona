from django.urls import path
from rest_framework.routers import DefaultRouter

from accounts import views

router = DefaultRouter()

urlpatterns = [
    # 1. User Registration and Authentication
    path('register/',
         views.UserRegisterView.as_view({'post': 'create'}), name="register"),
    path('login/', views.UserLoginView.as_view(), name="login"),
    path(
        'logout/', views.UserLogoutView.as_view({'post': 'create'}), name="logout"),

    # 2. User Profile Management (via ProfileViewSet)
    path('profile/',
         views.ProfileViewSet.as_view({'get': 'retrieve'}), name="user-profile"),
    path('profile/update/',
         views.ProfileViewSet.as_view({'put': 'update'}), name="user-profile-update"),
    path('profile/delete/',
         views.ProfileViewSet.as_view({'delete': 'destroy'}), name="user-delete"),

    # 3. Address Management (via AddressViewSet)
    path('addresses/',
         views.AddressViewSet.as_view({'get': 'list'}), name="address-list"),
    path('addresses/create/',
         views.AddressViewSet.as_view({'post': 'create'}), name="address-create"),
    path('addresses/<int:pk>/',
         views.AddressViewSet.as_view({'get': 'retrieve'}), name="address-detail"),
    path('addresses/update/<int:pk>/',
         views.AddressViewSet.as_view({'put': 'update'}), name="address-update"),
    path('addresses/delete/<int:pk>/',
         views.AddressViewSet.as_view({'delete': 'destroy'}), name="address-delete"),
]
