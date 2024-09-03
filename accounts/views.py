from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework import permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView  # for login page
from django.contrib.auth.hashers import check_password
from datetime import timedelta
from django.conf import settings

from .models import Address
from .serializers import (
    UserSerializer,
    UserRegisterTokenSerializer,
    AddressSerializer
)


# register user
class UserRegisterView(APIView):
    """To Register the User"""

    def post(self, request, format=None):
        data = request.data
        username = data["username"]
        email = data["email"]

        if username == "" or email == "":
            return Response({"detail": "username or email cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        check_username = User.objects.filter(username=username).exists()
        check_email = User.objects.filter(email=email).exists()

        if check_username:
            return Response({"detail": "A user with that username already exists!"}, status=status.HTTP_403_FORBIDDEN)
        if check_email:
            return Response({"detail": "A user with that email address already exists!"}, status=status.HTTP_403_FORBIDDEN)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(data["password"]),
        )

        # Automatically login the user by creating JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            "detail": "User registered successfully",
            "access_token": access_token,
            "refresh_token": refresh_token
        }, status=status.HTTP_201_CREATED)

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


# login user (customizing it so that we can see fields like username, email etc as a response
# from server, otherwise it will only provide access and refresh token)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        try:
            # Call the parent class validate to get token data
            data = super().validate(attrs)

            # Fetch additional user data
            user_data = UserRegisterTokenSerializer(self.user).data

            # Merge user data into the token response
            data.update(user_data)

            return data

        except AuthenticationFailed:
            # Custom error message on failed login
            raise AuthenticationFailed(
                detail="Invalid credentials, please try again.")


class UserLoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Get the token response
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            data = response.data
            access_token = data.get('access')
            refresh_token = data.get('refresh')

            # Set cookies
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],  # e.g. 'access_token'
                value=access_token,
                expires=timedelta(days=1),  # Adjust expiration if necessary
                httponly=True,
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                samesite='Lax'
            )

            response.set_cookie(
                # e.g. 'refresh_token'
                key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
                value=refresh_token,
                expires=timedelta(days=7),
                httponly=True,
                secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE', False),
                samesite='Lax'
            )

        return response


class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        response = Response({"detail": "Logout successful."},
                            status=status.HTTP_200_OK)

        # Clear the cookies
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['REFRESH_COOKIE'])

        return response


class UserProfileView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# update user account
class UserProfileUpdateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data

        if user:
            user.username = data["username"]
            user.email = data["email"]

            if data["password"] != "":
                user.password = make_password(data["password"])

            user.save()
            serializer = UserSerializer(user, many=False)
            message = {"detail": "User Successfully Updated.",
                       "user": serializer.data}
            return Response(message, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
