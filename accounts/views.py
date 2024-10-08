from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status, viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from revvona.utils import CustomPagination, error_response, success_response

from .models import Address
from .serializers import (AddressSerializer, CustomTokenObtainPairSerializer,
                          ProfileSerializer, UserRegisterTokenSerializer,
                          UserSerializer)


class UserAuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == 'logout_user' or self.action == 'change_password':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def register_user(self, request, *args, **kwargs):
        try:
            # Check if the user is already logged in
            if request.user.is_authenticated:
                return error_response("User already logged in.", "You are already logged in.", status_code=status.HTTP_403_FORBIDDEN)

            data = request.data
            username = data.get("username", "").strip()
            email = data.get("email", "").strip()

            # Ensure both username and email are provided
            if not username or not email:
                return error_response("Username and email cannot be empty.", status_code=status.HTTP_400_BAD_REQUEST)

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                return error_response("A user with that username already exists!", status_code=status.HTTP_403_FORBIDDEN)

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                return error_response("A user with that email address already exists!", status_code=status.HTTP_403_FORBIDDEN)

            # Create the user with is_active=False for email verification
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(data.get("password")),
                is_active=False
            )

            # Send verification email
            self.send_verification_email(user)

            # Return success response
            return success_response(
                {"user": user.id},
                "User registered successfully. Please verify your email to activate your account.",
                status_code=status.HTTP_201_CREATED
            )

        except Exception as e:
            # Handle any unexpected errors gracefully
            return error_response(
                "An error occurred while registering the user.",
                str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def send_verification_email(self, user):
        """Send a verification email to the user with a frontend-based verification link."""
        token = urlsafe_base64_encode(force_bytes(user.pk))  # Encode user ID
        # Replace with your actual frontend URL
        frontend_url = f"{
            settings.FRONTEND_URL}/verify?uid={token}&token={token}"

        subject = "Verify Your Email Address"
        html_message = render_to_string('verification_email.html', {
            'token': frontend_url,
            'frontend_url': frontend_url
        })

        send_mail(
            subject,
            "",  # Plain text message can be left empty if only HTML is used
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=html_message  # Use the html_message argument for HTML emails
        )

    def verify_email(self, request):
        """Verify email with uid and token sent from the frontend."""
        try:
            uid = request.GET.get('uid')
            token = request.GET.get('token')

            if not uid or not token:
                return error_response("Invalid or missing token.", status_code=status.HTTP_400_BAD_REQUEST)

            # Decode the uid to get the user ID
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)

            if user.is_active:
                return error_response("This account is already verified.", status_code=status.HTTP_400_BAD_REQUEST)

            # Mark the user as active
            user.is_active = True
            user.save(update_fields=['is_active'])

            return success_response({}, "Email verified successfully. You can now log in.", status_code=status.HTTP_200_OK)
        except User.DoesNotExist:
            return error_response("User does not exist.", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response("An error occurred during email verification.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def login_user(self, request, *args, **kwargs):
        """Log in a user using either username or email and password."""
        try:
            if request.user.is_authenticated:
                return error_response("User already logged in.", "You are already logged in.", status_code=status.HTTP_403_FORBIDDEN)

            # Extract the username (which could be either username or email) and password from the request
            username_or_email = request.data.get('username')
            password = request.data.get('password')

            if not username_or_email or not password:
                return error_response("Username/Email and password are required.", status_code=status.HTTP_400_BAD_REQUEST)

            try:
                # Check if the input is an email
                validate_email(username_or_email)
                # If it's a valid email, retrieve the user by email
                user = User.objects.filter(email=username_or_email).first()
                if not user:
                    return error_response("User with this email does not exist.", status_code=status.HTTP_404_NOT_FOUND)
                username = user.username  # Get the username associated with the email
            except ValidationError:
                # If it's not a valid email, treat it as a username
                username = username_or_email
                user = User.objects.filter(username=username).first()
                if not user:
                    return error_response("User with this username does not exist.", status_code=status.HTTP_404_NOT_FOUND)

            # Now pass the username and password to the serializer
            serializer = CustomTokenObtainPairSerializer(data={
                'username': username,
                'password': password
            })
            serializer.is_valid(raise_exception=True)

            # Update last_login in the view because django doesn't do it automatically when using JWT
            user = serializer.user
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            # Retrieve tokens from the serializer
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Return successful response with tokens
            response = success_response({
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "access_token": access_token,
                "refresh_token": refresh_token
            }, "Login successful.")

            return response

        except AuthenticationFailed as e:
            return error_response(str(e))
        except Exception as e:
            return error_response("An error occurred during login.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def refresh_token(self, request, *args, **kwargs):
        """Handle token refresh using the refresh token."""
        try:
            refresh_token = request.data.get('refresh_token')

            if not refresh_token:
                return error_response("Refresh token is required.", status_code=status.HTTP_400_BAD_REQUEST)

            try:
                refresh = RefreshToken(refresh_token)
                access_token = str(refresh.access_token)

                return success_response({
                    "access_token": access_token,
                }, "Access token refreshed successfully.")
            except Exception as e:
                return error_response("Invalid or expired refresh token.", str(e), status_code=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return error_response("An error occurred while refreshing the token.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def logout_user(self, request):
        """Log out the user."""
        try:
            # Perform logout logic for JWT-based auth (typically just a client-side action)
            return success_response({}, "Logout successful.", status_code=status.HTTP_200_OK)
        except Exception as e:
            return error_response("An error occurred during logout.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def change_password(self, request, *args, **kwargs):
        try:
            user = request.user

            # Extract passwords from request data
            curr_password = request.data.get("curr_password")
            new_password = request.data.get("new_password")

            # Ensure all required fields are provided
            if not curr_password or not new_password:
                return error_response("Current password and new password are required.", status_code=status.HTTP_400_BAD_REQUEST)

            # Check if current password is correct
            if not user.check_password(curr_password):
                return error_response("Current password is incorrect.", status_code=status.HTTP_400_BAD_REQUEST)

            # Validate the new password using Django's built-in password validators
            try:
                validate_password(new_password, user=user)
            except ValidationError as e:
                return error_response("Password validation error.", str(e), status_code=status.HTTP_400_BAD_REQUEST)

            # Set and save the new password
            user.set_password(new_password)
            user.save(update_fields=['password'])

            # Optionally, log the user out of all sessions by invalidating tokens (JWT)
            # refresh_token = request.data.get("refresh_token")
            # if refresh_token:
            #     try:
            #         token = RefreshToken(refresh_token)
            #         token.blacklist()
            #     except Exception:
            #         pass  # Handle errors if needed

            return success_response({}, "Password updated successfully.", status_code=status.HTTP_200_OK)

        except Exception as e:
            return error_response("An error occurred while changing the password.", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

            # Get the new email from the request data
            new_email = data.get("email", user.email)

            # Check if the new email is already taken by another user
            if new_email != user.email and User.objects.filter(email=new_email).exists():
                return error_response("This email is already in use by another account.", status_code=status.HTTP_400_BAD_REQUEST)

            # Update the user's username, email, first_name, and last_name
            user.username = data.get("username", user.username)
            user.email = new_email
            user.first_name = data.get("first_name", user.first_name)
            user.last_name = data.get("last_name", user.last_name)

            user.save()

            # Serialize the updated user data
            serializer = ProfileSerializer(user)
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
