from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

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


class UserRegisterView(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        try:
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


### Custom Login Token View with Cookie Setup ###
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            user_data = UserRegisterTokenSerializer(self.user).data
            data.update(user_data)
            return data
        except AuthenticationFailed:
            raise AuthenticationFailed(
                detail="Invalid credentials, please try again.")


class UserLoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            # Call the super class's post method to obtain tokens
            response = super().post(request, *args, **kwargs)

            # Check if the response was successful
            if response.status_code == 200:
                data = response.data
                access_token = data.get('access')
                refresh_token = data.get('refresh')

                # Set cookies
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=access_token,
                    expires=timedelta(days=1),
                    httponly=True,
                    secure=settings.SIMPLE_JWT.get(
                        'AUTH_COOKIE_SECURE', False),
                    samesite='Lax'
                )
                response.set_cookie(
                    key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
                    value=refresh_token,
                    expires=timedelta(days=7),
                    httponly=True,
                    secure=settings.SIMPLE_JWT.get(
                        'AUTH_COOKIE_SECURE', False),
                    samesite='Lax'
                )

                # Update response data to include success message and tokens
                response.data = success_response({
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, "Login successful.").data

            return response

        except Exception as e:
            # Handle unexpected errors
            return error_response("An error occurred during login.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLogoutView(viewsets.ViewSet):
    def create(self, request):
        try:
            response = success_response(
                {"detail": "Logout successful."}, "Logout successful.")
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
            response.delete_cookie(settings.SIMPLE_JWT['REFRESH_COOKIE'])
            return response
        except Exception as e:
            return error_response("An error occurred during logout.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """Retrieve the current user's profile with addresses."""
        try:
            user = request.user
            serializer = ProfileSerializer(user)
            return success_response(serializer.data, "User profile retrieved.")
        except User.DoesNotExist:
            return error_response("User not found.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while retrieving the profile.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """Update the current user's profile."""
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

    def destroy(self, request, *args, **kwargs):
        """Delete the current user's account."""
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


### Address Viewset (CRUD Operations) ###
class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            address = self.get_object()
            if address.user != request.user:
                return error_response("You don't have permission to delete this address.", status.HTTP_403_FORBIDDEN)
            address.delete()
            return success_response(None, "Address successfully deleted.", status.HTTP_204_NO_CONTENT)
        except Address.DoesNotExist:
            return error_response("Address not found.", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred while deleting the address.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            address = self.get_object()
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
