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
