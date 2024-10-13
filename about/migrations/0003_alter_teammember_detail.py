# Generated by Django 5.0 on 2024-10-24 20:05

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("about", "0002_rename_content_about_story"),
    ]

    operations = [
        migrations.AlterField(
            model_name="teammember",
            name="detail",
            field=models.TextField(
                validators=[django.core.validators.MinLengthValidator(500)]
            ),
        ),
    ]
