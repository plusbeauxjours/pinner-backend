# Generated by Django 2.2.4 on 2019-09-22 03:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190922_1212'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='app_avatarl_url',
            new_name='app_avatar_url',
        ),
    ]