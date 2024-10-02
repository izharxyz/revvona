from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Address
from .serializers import (AddressSerializer, ProfileSerializer,
                          UserRegisterTokenSerializer, UserSerializer)


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


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        if not queryset.ordered:
            queryset = queryset.order_by('-created_at')
        return super().paginate_queryset(queryset, request, view)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            user_data = UserRegisterTokenSerializer(self.user).data
            data.update(user_data)

            # Add the user object to validated_data
            data['user'] = self.user  # Ensure user is included

            return data

        except AuthenticationFailed:
            return error_response("Invalid credentials, please try again.")
        except User.DoesNotExist:
            return error_response("User does not exist.")
        except Exception as e:
            # Handle any other exceptions
            return error_response("An error occurred during authentication.", str(e))


class UserAuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == 'logout_user':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def register_user(self, request, *args, **kwargs):
        """Register a new user."""
        try:
            if request.user.is_authenticated:
                return error_response("User already logged in.", f"{request.user}, you are already logged in.", status_code=status.HTTP_403_FORBIDDEN)

            data = request.data
            username = data.get("username", "")
            email = data.get("email", "")

            if not username or not email:
                return error_response("Username or email cannot be empty.", status_code=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                return error_response("A user with that username already exists!", status_code=status.HTTP_403_FORBIDDEN)

            if User.objects.filter(email=email).exists():
                return error_response("A user with that email address already exists!", status_code=status.HTTP_403_FORBIDDEN)

            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(data.get("password")),
            )

            # Generate tokens and set them as cookies
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = success_response({
                "access_token": access_token,
                "refresh_token": refresh_token
            }, "User registered successfully", status_code=status.HTTP_201_CREATED)

            # Set cookies
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                expires=timedelta(days=1),
                httponly=True,
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                samesite='Lax'
            )
            response.set_cookie(
                key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
                value=refresh_token,
                expires=timedelta(days=7),
                httponly=True,
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                samesite='Lax'
            )
            return response
        except Exception as e:
            return error_response("An error occurred while registering the user.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def login_user(self, request, *args, **kwargs):
        """Log in a user and set cookies."""
        try:
            if request.user.is_authenticated:
                return error_response("User already logged in.", f"{request.user}, you are already logged in.", status_code=status.HTTP_403_FORBIDDEN)
            # Obtain tokens using the serializer
            serializer = MyTokenObtainPairSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Retrieve the user from validated data
            user = serializer.validated_data.get(
                'user')  # Use get to avoid KeyError

            if user is None:
                return error_response("User not found.", status_code=status.HTTP_404_NOT_FOUND)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = success_response({
                "access_token": access_token,
                "refresh_token": refresh_token
            }, "Login successful.")

            # Set cookies
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=access_token,
                expires=timedelta(days=1),
                httponly=True,
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                samesite='Lax'
            )
            response.set_cookie(
                key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
                value=refresh_token,
                expires=timedelta(days=7),
                httponly=True,
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                samesite='Lax'
            )

            return response
        except AuthenticationFailed:
            return error_response("Invalid credentials, please try again.")
        except Exception as e:
            return error_response("An error occurred during login.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def logout_user(self, request):
        """Log out the user by deleting cookies."""
        try:
            response = success_response(
                {}, "Logout successful.")
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
            response.delete_cookie(settings.SIMPLE_JWT['REFRESH_COOKIE'])
            return response
        except Exception as e:
            return error_response("An error occurred during logout.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve_user_profile(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = ProfileSerializer(user)
            return success_response(serializer.data, "User profile retrieved.")
        except User.DoesNotExist:
            return error_response("User not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while retrieving the profile.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_user_profile(self, request, *args, **kwargs):
        try:
            user = request.user
            data = request.data

            # Update the user's username, email, and optionally the password
            user.username = data.get("username", user.username)
            user.email = data.get("email", user.email)

            if data.get("password"):
                user.password = make_password(data.get("password"))

            user.save()
            serializer = UserSerializer(user)
            return success_response(serializer.data, "User successfully updated.", status.HTTP_200_OK)
        except User.DoesNotExist:
            return error_response("User not found.", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while updating the profile.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete_user_profile(self, request, *args, **kwargs):
        try:
            user = request.user
            data = request.data

            # Check if the provided password matches the user's current password
            if 'password' in data and check_password(data['password'], user.password):
                user.delete()
                return success_response({}, "User account successfully deleted.", status.HTTP_204_NO_CONTENT)
            else:
                return error_response("Incorrect password.", status_code=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return error_response("User not found.", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while deleting the user account.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create_user_address(self, request, *args, **kwargs):
        try:
            data = request.data
            data['user'] = request.user.id  # Set the user field automatically
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return success_response(serializer.data, "Address successfully created.", status.HTTP_201_CREATED)
            else:
                return error_response("Invalid data.", serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response("An error occurred while creating the address.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list_user_addresses(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        paginator = CustomPagination()
        paginated_addresses = paginator.paginate_queryset(
            queryset, request, view=self)

        if paginated_addresses is None:
            return error_response("No addresses found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(paginated_addresses, many=True)
        return success_response({
            "addresses": serializer.data,
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link()
        }, message="Addresses retrieved successfully")

    def retrieve_user_address(self, request, *args, **kwargs):
        try:
            address = self.get_object()  # This will look up by primary key
            if address.user != request.user:
                return error_response("You don't have permission to view this address.", status.HTTP_403_FORBIDDEN)
            serializer = self.get_serializer(address)
            return success_response(serializer.data, "Address retrieved successfully.")
        except Address.DoesNotExist:
            return error_response("Address not found.", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while retrieving the address.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update_user_address(self, request, *args, **kwargs):
        try:
            address = self.get_object()  # This will look up by primary key
            if address.user != request.user:
                return error_response("You don't have permission to edit this address.", status.HTTP_403_FORBIDDEN)

            serializer = AddressSerializer(
                address, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return success_response(serializer.data, "Address successfully updated.")
            else:
                return error_response("Invalid data.", serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Address.DoesNotExist:
            return error_response("Address not found.", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while updating the address.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete_user_address(self, request, *args, **kwargs):
        try:
            address = self.get_object()  # This will look up by primary key
            if address.user != request.user:
                return error_response("You don't have permission to delete this address.", status.HTTP_403_FORBIDDEN)
            address.delete()
            return success_response(None, "Address successfully deleted.", status.HTTP_204_NO_CONTENT)
        except Address.DoesNotExist:
            return error_response("Address not found.", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while deleting the address.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
