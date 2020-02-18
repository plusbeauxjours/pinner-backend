from django.db import models
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.html import escape, format_html
from config import models as config_models

from cached_property import cached_property

from utils import notify_slack
from django.dispatch import receiver
from django.db.models.signals import post_save


class Continent (config_models.TimeStampedModel):

    continent_name = models.CharField(max_length=100, null=True, blank=True)
    continent_photo = models.URLField(null=True, blank=True)
    continent_thumbnail = models.URLField(null=True, blank=True)
    continent_code = models.CharField(max_length=20, null=True, blank=True)

    @cached_property
    def country_count(self):
        return self.countries.all().count()
    country_count.short_description = "country"

    @cached_property
    def user_log_count(self):
        return self.moveNotificationContinent.values('actor__id').all().order_by('-actor__id').distinct('actor__id').count()
    user_log_count.short_description = "user log"

    def __str__(self):
        return self.continent_name

    def image_tag(self):
        return format_html(
            '<img src="{url}" style="width:50px; height:50px; object-fit: cover;">',
            url=self.continent_thumbnail)
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class Country (config_models.TimeStampedModel):

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    country_name = models.CharField(max_length=50, null=True, blank=True)
    country_name_native = models.CharField(max_length=50, null=True, blank=True)
    country_capital = models.CharField(max_length=50, null=True, blank=True)
    country_currency = models.CharField(max_length=20, null=True, blank=True)
    country_photo = models.URLField(null=True, blank=True)
    country_thumbnail = models.URLField(null=True, blank=True)
    country_emoji = models.CharField(max_length=20, null=True, blank=True)
    country_phone = models.CharField(max_length=20, null=True, blank=True)
    continent = models.ForeignKey(Continent, null=True, blank=True, on_delete=models.CASCADE, related_name='countries')

    @cached_property
    def city_count(self):
        return self.cities.all().count()
    city_count.short_description = "city"

    @cached_property
    def total_like_count(self):
        return Like.objects.filter(city__country=self).count()
    total_like_count.short_description = "like"

    @cached_property
    def user_log_count(self):
        return self.moveNotificationCountry.values('actor__id').all().order_by('-actor__id').distinct('actor__id').count()
    user_log_count.short_description = "user log"

    def __str__(self):
        return self.country_name

    def image_tag(self):
        return format_html(
            '<img src="{url}" style="width:50px; height:50px; object-fit: cover;">',
            url=self.country_thumbnail)
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class City (config_models.TimeStampedModel):

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name='cities')
    city_id = models.CharField(max_length=100, null=True, blank=True)
    city_name = models.CharField(max_length=100, null=True, blank=True)
    city_photo = models.URLField(null=True, blank=True)
    city_thumbnail = models.URLField(null=True, blank=True)
    population = models.IntegerField(null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    near_city = models.ManyToManyField(
        'self',  blank=True, symmetrical=False, related_name='near_cities')

    @cached_property
    def like_count(self):
        return self.likes.all().count()
    like_count.short_description = "like"

    @cached_property
    def user_count(self):
        return self.currentCity.values('id').all().count()
    user_count.short_description = "user"

    @cached_property
    def user_log_count(self):
        return self.moveNotificationCity.values('actor__id').all().order_by('-actor__id').distinct('actor__id').count()
    user_log_count.short_description = "user log"

    def __str__(self):
        return self.city_name

    def image_tag(self):
        return format_html(
            '<img src="{url}" style="width:50px; height:50px; object-fit: cover;">',
            url=self.city_thumbnail)
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


class Like(config_models.TimeStampedModel):

    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name='likes')
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, null=True, related_name='likes')

    @property
    def natural_time(self):
        return naturaltime(self.created_at)

    def __str__(self):
        return 'User: {} - City cityname: {}'.format(self.creator.username, self.city.city_name)


@receiver(post_save, sender=City)
def send_slack_notification_city_created(sender,  instance, created, **kwargs):
    if created:
        to_channel = "#location_%s" % (instance.country.continent.continent_code.lower())
        attachments = [{
            "fallback": "New City on Pinner",
            "color": "#569934",
            "title":  "New city: %s" % (instance.city_name),
            "title_link": "https://www.pinner.fun/city/%s" % (instance.city_id),
            "text": "Created new city on %s %s. \n Total cities on %s %s: %s." % (
                instance.country.country_name, instance.country.country_emoji, instance.country.country_name, instance.country.country_emoji, instance.country.city_count),
            "image_url": instance.city_photo,
            "footer": "🙌🏻 New City!",
        }]
        notify_slack(to_channel, attachments=attachments)


@receiver(post_save, sender=Country)
def send_slack_notification_country_created(sender,  instance, created, **kwargs):
    if created:
        to_channel = "#location_%s" % (instance.continent.continent_code.lower())
        attachments = [{
            "fallback": "New Country on Pinner",
            "color": "#569934",
            "title":   "Created new city on %s %s. \n Total cities on %s %s: %s." % (
                instance.country_name, instance.country_emoji, instance.country_name, instance.country_emoji, instance.city_count, ),
            "title_link": "https://www.pinner.fun/country/%s" % (instance.country_code),
            "text": "Optional text that appears within the attachment",
            "image_url": instance.country_photo,
            "footer": "🙌🏻 New Country!",
        }]
        notify_slack(to_channel, attachments=attachments)
