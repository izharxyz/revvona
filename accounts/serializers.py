from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from revvona.utils import CustomSerializer, error_response

from .models import Address


class AddressSerializer(CustomSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class UserSerializer(CustomSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ProfileSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["first_name", "last_name"]


# Creating tokens manually (with user registration we will also create tokens)
class UserRegisterTokenSerializer(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "token"]

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
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
