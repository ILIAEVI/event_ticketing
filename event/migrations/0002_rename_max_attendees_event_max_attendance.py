# Generated by Django 5.1.4 on 2024-12-17 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='max_attendees',
            new_name='max_attendance',
        ),
    ]
