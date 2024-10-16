# Generated by Django 5.0 on 2024-10-24 18:14

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="About",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                (
                    "content",
                    models.TextField(
                        validators=[django.core.validators.MinLengthValidator(1000)]
                    ),
                ),
                ("image", models.ImageField(upload_to="about/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Instagram",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("username", models.CharField(max_length=100)),
                ("user_id", models.CharField(blank=True, max_length=100)),
                ("token", models.CharField(max_length=255)),
                ("next_page", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Instagram Marketing",
                "verbose_name_plural": "Instagram Marketing",
            },
        ),
        migrations.CreateModel(
            name="Legal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "terms_and_conditions",
                    models.TextField(
                        validators=[django.core.validators.MinLengthValidator(500)]
                    ),
                ),
                (
                    "privacy_policy",
                    models.TextField(
                        validators=[django.core.validators.MinLengthValidator(500)]
                    ),
                ),
                (
                    "return_policy",
                    models.TextField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinLengthValidator(500)],
                    ),
                ),
                (
                    "disclaimer",
                    models.TextField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinLengthValidator(500)],
                    ),
                ),
                (
                    "shipping_policy",
                    models.TextField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinLengthValidator(500)],
                    ),
                ),
                (
                    "payment_policy",
                    models.TextField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinLengthValidator(500)],
                    ),
                ),
                (
                    "cookie_policy",
                    models.TextField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinLengthValidator(500)],
                    ),
                ),
                (
                    "razorpay_compliance",
                    models.TextField(
                        blank=True,
                        null=True,
                        validators=[django.core.validators.MinLengthValidator(500)],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Legal",
                "verbose_name_plural": "Legal",
            },
        ),
        migrations.CreateModel(
            name="Testimonial",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("position", models.CharField(max_length=100)),
                ("image", models.ImageField(upload_to="testimonial/")),
                (
                    "content",
                    models.TextField(
                        validators=[django.core.validators.MinLengthValidator(100)]
                    ),
                ),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                        default=5,
                        verbose_name="Rating (1-5)",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Socials",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("twitter", models.URLField(blank=True, null=True)),
                ("linkedin", models.URLField(blank=True, null=True)),
                ("youtube", models.URLField(blank=True, null=True)),
                ("pinterest", models.URLField(blank=True, null=True)),
                ("whatsapp", models.URLField(blank=True, null=True)),
                ("facebook", models.URLField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "instagram",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="about.instagram",
                    ),
                ),
            ],
            options={
                "verbose_name": "Social Media",
                "verbose_name_plural": "Social Media",
            },
        ),
        migrations.CreateModel(
            name="TeamMember",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("position", models.CharField(max_length=100)),
                ("image", models.ImageField(upload_to="team/")),
                (
                    "detail",
                    models.TextField(
                        validators=[django.core.validators.MinLengthValidator(1000)]
                    ),
                ),
                (
                    "instagram",
                    models.URLField(
                        blank=True, null=True, verbose_name="Instagram Profile"
                    ),
                ),
                (
                    "linkedin",
                    models.URLField(
                        blank=True, null=True, verbose_name="LinkedIn Profile"
                    ),
                ),
                (
                    "twitter",
                    models.URLField(
                        blank=True, null=True, verbose_name="Twitter Profile"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                        verbose_name="Email Address",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "about",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="team_members",
                        to="about.about",
                    ),
                ),
            ],
        ),
    ]