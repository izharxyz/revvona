from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny

from revvona.utils import error_response, success_response

from .models import About, Legal, Socials, Testimonial
from .serializers import (AboutSerializer, SocialsSerializer,
                          TestimonialSerializer)


# About ViewSet with Team Members
class AboutViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def brand_story(self, request):
        try:
            about = About.objects.first()  # Assuming only one record exists
            if not about:
                return error_response("About info not available", status_code=status.HTTP_404_NOT_FOUND)

            serializer = AboutSerializer(about)
            return success_response(serializer.data, "About info retrieved successfully")
        except Exception as e:
            return error_response("An error occurred while retrieving About info", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Legal ViewSet with a generic method
class LegalViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_legal_field(self, request, field_name):
        try:
            legal = Legal.objects.first()
            if not legal or not getattr(legal, field_name):
                return error_response(f"Owner is too lazy to configure {field_name.replace('_', ' ')}", status_code=status.HTTP_404_NOT_FOUND)

            return success_response({field_name: getattr(legal, field_name)}, f"{field_name.replace('_', ' ').capitalize()} retrieved successfully")
        except Exception as e:
            return error_response(f"An error occurred while retrieving {field_name.replace('_', ' ')}", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_terms_and_conditions(self, request):
        return self.get_legal_field(request, 'terms_and_conditions')

    def get_privacy_policy(self, request):
        return self.get_legal_field(request, 'privacy_policy')

    def get_cancellation_policy(self, request):
        return self.get_legal_field(request, 'cancellation_policy')

    def get_return_policy(self, request):
        return self.get_legal_field(request, 'return_policy')

    def get_disclaimer(self, request):
        return self.get_legal_field(request, 'disclaimer')

    def get_shipping_policy(self, request):
        return self.get_legal_field(request, 'shipping_policy')

    def get_payment_policy(self, request):
        return self.get_legal_field(request, 'payment_policy')

    def get_cookie_policy(self, request):
        return self.get_legal_field(request, 'cookie_policy')

    def get_razorpay_compliance(self, request):
        return self.get_legal_field(request, 'razorpay_compliance')


# Testimonial ViewSet
class TestimonialViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list_testimonials(self, request):
        try:
            testimonials = Testimonial.objects.all()
            serializer = TestimonialSerializer(testimonials, many=True)
            return success_response(serializer.data, "Testimonials retrieved successfully")
        except Exception as e:
            return error_response("An error occurred while retrieving testimonials", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Socials ViewSet including Instagram data
class SocialsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def get_social_links(self, request):
        try:
            socials = Socials.objects.first()  # Assuming only one record exists
            if not socials:
                return error_response("Social media links not available", status_code=status.HTTP_404_NOT_FOUND)

            serializer = SocialsSerializer(socials)
            return success_response(serializer.data, "Social media links retrieved successfully")
        except Exception as e:
            return error_response("An error occurred while retrieving social media links", str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
