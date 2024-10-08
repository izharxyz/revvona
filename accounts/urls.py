from django.urls import path

from . import views

urlpatterns = [
    # User Registration and Authentication
    path('register/',
         views.UserAuthViewSet.as_view({'post': 'register_user'}), name="register"),
    path('verify-email/',
         views.UserAuthViewSet.as_view({'get': 'verify_email'}), name="verify-email"),
    path(
        'login/', views.UserAuthViewSet.as_view({'post': 'login_user'}), name="login"),
    path('token-refresh/', views.UserAuthViewSet.as_view(
        {'post': 'refresh_token'}), name="token-refresh"),
    path('logout/',
         views.UserAuthViewSet.as_view({'post': 'logout_user'}), name="logout"),
    path('password/change/', views.UserAuthViewSet.as_view(
        {'patch': 'change_password'}), name="change-password"),

    # User Profile Management (via ProfileViewSet)
    path('profile/',
         views.ProfileViewSet.as_view({'get': 'retrieve_user_profile'}), name="user-profile"),
    path('profile/update/',
         views.ProfileViewSet.as_view({'patch': 'update_user_profile'}), name="user-profile-update"),
    path('profile/delete/',
         views.ProfileViewSet.as_view({'delete': 'delete_user_profile'}), name="user-delete"),

    # Address Management (via AddressViewSet)
    path('addresses/',
         views.AddressViewSet.as_view({'get': 'list_user_addresses'}), name="address-list"),
    path('addresses/create/',
         views.AddressViewSet.as_view({'post': 'create_user_address'}), name="address-create"),
    path('addresses/<int:pk>/',
         views.AddressViewSet.as_view({'get': 'retrieve_user_address'}), name="address-detail"),
    path('addresses/<int:pk>/update/',
         views.AddressViewSet.as_view({'patch': 'update_user_address'}), name="address-update"),
    path('addresses/<int:pk>/delete/',
         views.AddressViewSet.as_view({'delete': 'delete_user_address'}), name="address-delete"),
]
