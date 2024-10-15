from django.urls import path

from . import views

urlpatterns = [
    # About and Team Members
    path('story/',
         views.AboutViewSet.as_view({'get': 'brand_story'}), name="brand-story"),

    # Legal Information
    path('legal/terms-and-conditions/',
         views.LegalViewSet.as_view({'get': 'get_terms_and_conditions'}), name="terms-and-conditions"),
    path('legal/privacy-policy/',
         views.LegalViewSet.as_view({'get': 'get_privacy_policy'}), name="privacy-policy"),
    path('legal/return-policy/',
         views.LegalViewSet.as_view({'get': 'get_return_policy'}), name="return-policy"),
    path('legal/disclaimer/',
         views.LegalViewSet.as_view({'get': 'get_disclaimer'}), name="disclaimer"),
    path('legal/shipping-policy/',
         views.LegalViewSet.as_view({'get': 'get_shipping_policy'}), name="shipping-policy"),
    path('legal/payment-policy/',
         views.LegalViewSet.as_view({'get': 'get_payment_policy'}), name="payment-policy"),
    path('legal/cookie-policy/',
         views.LegalViewSet.as_view({'get': 'get_cookie_policy'}), name="cookie-policy"),
    path('legal/razorpay-compliance/',
         views.LegalViewSet.as_view({'get': 'get_razorpay_compliance'}), name="razorpay-compliance"),

    # Testimonials
    path('testimonials/',
         views.TestimonialViewSet.as_view({'get': 'list_testimonials'}), name="testimonials-list"),

    # Social Media Links
    path('socials/',
         views.SocialsViewSet.as_view({'get': 'get_social_links'}), name="social-links"),
]
