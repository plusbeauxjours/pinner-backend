# Generated by Django 2.2.4 on 2019-12-11 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile_push_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='push_token',
            field=models.CharField(default='', max_length=200),
        ),
    ]
