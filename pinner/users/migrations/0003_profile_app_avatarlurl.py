# Generated by Django 2.2.4 on 2019-09-21 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_avatar_app_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='app_avatarlUrl',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]