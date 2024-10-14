from rest_framework import serializers

from .models import About, Instagram, Legal, Socials, TeamMember, Testimonial


# Serializer for Instagram (as part of Socials)
class InstagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instagram
        fields = ['username', 'user_id',
                  'next_page', 'created_at', 'updated_at']

# Serializer for Socials (with Instagram as a field)


class SocialsSerializer(serializers.ModelSerializer):
    instagram = InstagramSerializer()

    class Meta:
        model = Socials
        fields = ['instagram', 'twitter', 'linkedin', 'youtube',
                  'pinterest', 'whatsapp', 'facebook', 'created_at', 'updated_at']

# Serializer for TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['name', 'position', 'image', 'detail', 'instagram',
                  'linkedin', 'twitter', 'email', 'created_at', 'updated_at']

# Serializer for About


class AboutSerializer(serializers.ModelSerializer):
    team_members = TeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = About
        fields = ['title', 'story', 'image',
                  'team_members', 'created_at', 'updated_at']

# Serializer for Legal


class LegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legal
        fields = ['terms_and_conditions', 'privacy_policy', 'return_policy', 'disclaimer', 'shipping_policy',
                  'payment_policy', 'cookie_policy', 'razorpay_compliance', 'created_at', 'updated_at']

# Serializer for Testimonial


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['name', 'position', 'image', 'content',
                  'rating', 'created_at', 'updated_at']
