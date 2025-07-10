# movie_app/migrations/0002_add_date_fields_to_userinteraction.py
# Generated for adding date tracking fields to UserInteraction model

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('movie_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinteraction',
            name='has_liked_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userinteraction',
            name='has_seen_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
