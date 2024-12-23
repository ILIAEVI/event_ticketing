# Generated by Django 5.1.4 on 2024-12-23 12:32

import contact.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialmedia',
            name='icon',
            field=models.ImageField(blank=True, null=True, upload_to=contact.utils.generate_image_path),
        ),
    ]