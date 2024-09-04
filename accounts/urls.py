from django.urls import path
from accounts import views

urlpatterns = [
    # user auth and profile
    path('register/', views.UserRegisterView.as_view(), name="register"),
    path('login/', views.UserLoginView.as_view(), name="login"),
    path('logout/', views.UserLogoutView.as_view(), name="logout"),

    path('profile/', views.UserProfileView.as_view(), name="user-profile"),
    path('profile/update/',
         views.UserProfileUpdateView.as_view(), name="user-profile-update"),
    path('delete/',
         views.UserAccountDeleteView.as_view(), name="user-delete"),

    # user address
    path('address/', views.UserAddressesListView.as_view(),
         name="address-list"),
    path('address/<int:pk>/',
         views.UserAddressDetailsView.as_view(), name="address-details"),

    path('address/create/', views.CreateUserAddressView.as_view(),
         name="create-address"),
    path('address/update/<int:pk>/', views.UpdateUserAddressView.as_view(),
         name="update-address"),
    path('address/delete/<int:pk>/',
         views.DeleteUserAddressView.as_view(), name="delete-address"),
]
