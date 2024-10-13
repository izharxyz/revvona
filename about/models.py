import cloudinary
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class About(models.Model):
    title = models.CharField(max_length=100)
    story = models.TextField(validators=[MinLengthValidator(1000)])
    image = models.ImageField(upload_to='about/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        # Delete the image from Cloudinary
        if self.image:
            cloudinary.uploader.destroy(self.image.name)
        super().delete(*args, **kwargs)


class TeamMember(models.Model):
    about = models.ForeignKey(
        About, related_name="team_members", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team/')
    detail = models.TextField(validators=[MinLengthValidator(500)])
    instagram = models.URLField(
        null=True, blank=True, verbose_name=_("Instagram Profile"))
    linkedin = models.URLField(
        null=True, blank=True, verbose_name=_("LinkedIn Profile"))
    twitter = models.URLField(null=True, blank=True,
                              verbose_name=_("Twitter Profile"))

    email = models.EmailField(null=True, blank=True,
                              verbose_name=_("Email Address"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Delete the image from Cloudinary
        if self.image:
            cloudinary.uploader.destroy(self.image.name)
        super().delete(*args, **kwargs)


class Legal(models.Model):
    terms_and_conditions = models.TextField(
        validators=[MinLengthValidator(500)])
    privacy_policy = models.TextField(validators=[MinLengthValidator(500)])
    return_policy = models.TextField(
        validators=[MinLengthValidator(500)], null=True, blank=True)

    # For any disclaimers regarding content or third parties
    disclaimer = models.TextField(
        validators=[MinLengthValidator(500)], null=True, blank=True)

    # Especially important if dealing with physical products
    shipping_policy = models.TextField(
        validators=[MinLengthValidator(500)], null=True, blank=True)

    # Explain how payments are processed, refunds, etc.
    payment_policy = models.TextField(
        validators=[MinLengthValidator(500)], null=True, blank=True)

    cookie_policy = models.TextField(validators=[MinLengthValidator(
        500)], null=True, blank=True)  # Compliance for cookies and user data

    # Any terms specific to Razorpay or payment gateways
    razorpay_compliance = models.TextField(
        validators=[MinLengthValidator(500)], null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Legal")
        verbose_name_plural = _("Legal")


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to='testimonial/')
    content = models.TextField(validators=[MinLengthValidator(100)])
    rating = models.PositiveSmallIntegerField(
        default=5,
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name=_("Rating (1-5)")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Delete the image from Cloudinary
        if self.image:
            cloudinary.uploader.destroy(self.image.name)
        super().delete(*args, **kwargs)


# this is usefull for displaying instagram feed on the frontend
class Instagram(models.Model):
    username = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100, blank=True)
    token = models.CharField(max_length=255)
    next_page = models.CharField(max_length=255, blank=True)  # For pagination
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _("Instagram Marketing")
        verbose_name_plural = _("Instagram Marketing")


class Socials(models.Model):
    instagram = models.OneToOneField(Instagram, on_delete=models.CASCADE)
    twitter = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)
    pinterest = models.URLField(null=True, blank=True)
    whatsapp = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return _("Social Media Links")

    class Meta:
        verbose_name = _("Social Media")
        verbose_name_plural = _("Social Media")
