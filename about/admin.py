from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget

from .models import About, Instagram, Legal, Socials, TeamMember, Testimonial


# Inline model for Team under About
class TeamInline(StackedInline):
    model = TeamMember
    extra = 1  # Number of empty inlines to show
    can_delete = True  # Allow deletion of team members in admin
    show_change_link = True

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }


# About Admin with Team Inline
class AboutAdmin(ModelAdmin):
    inlines = [TeamInline]
    list_display = ('title', 'created_at', 'updated_at')

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }


# Inline model for Socials under Instagram
class SocialsInline(StackedInline):
    model = Socials
    extra = 1  # Number of empty inlines to show
    show_change_link = True
    can_delete = True


# Instagram Admin with Socials Inline
class InstagramAdmin(ModelAdmin):
    inlines = [SocialsInline]
    list_display = ('username', 'user_id', 'created_at', 'updated_at')


# Legal Admin
class LegalAdmin(ModelAdmin):
    list_display = ('created_at', 'updated_at')

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }


# Testimonial Admin
class TestimonialAdmin(ModelAdmin):
    list_display = ('name', 'position', 'rating', 'created_at', 'updated_at')


# Registering all models
admin.site.register(About, AboutAdmin)
admin.site.register(Instagram, InstagramAdmin)
admin.site.register(Legal, LegalAdmin)
admin.site.register(Testimonial, TestimonialAdmin)
