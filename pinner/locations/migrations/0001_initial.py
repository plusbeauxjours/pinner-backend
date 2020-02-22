# Generated by Django 3.0 on 2020-02-21 03:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('city_id', models.CharField(blank=True, max_length=100, null=True)),
                ('city_name', models.CharField(blank=True, max_length=100, null=True)),
                ('city_photo', models.URLField(blank=True, null=True)),
                ('city_thumbnail', models.URLField(blank=True, null=True)),
                ('population', models.IntegerField(blank=True, null=True)),
                ('info', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Continent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('continent_name', models.CharField(blank=True, max_length=100, null=True)),
                ('continent_photo', models.URLField(blank=True, null=True)),
                ('continent_thumbnail', models.URLField(blank=True, null=True)),
                ('continent_code', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('city', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='locations.City')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('country_code', models.CharField(blank=True, max_length=10, null=True)),
                ('country_name', models.CharField(blank=True, max_length=50, null=True)),
                ('country_name_native', models.CharField(blank=True, max_length=50, null=True)),
                ('country_capital', models.CharField(blank=True, max_length=50, null=True)),
                ('country_currency', models.CharField(blank=True, max_length=20, null=True)),
                ('country_photo', models.URLField(blank=True, null=True)),
                ('country_thumbnail', models.URLField(blank=True, null=True)),
                ('country_emoji', models.CharField(blank=True, max_length=20, null=True)),
                ('country_phone', models.CharField(blank=True, max_length=20, null=True)),
                ('continent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='countries', to='locations.Continent')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='city',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='locations.Country'),
        ),
        migrations.AddField(
            model_name='city',
            name='near_city',
            field=models.ManyToManyField(blank=True, related_name='near_cities', to='locations.City'),
        ),
    ]
