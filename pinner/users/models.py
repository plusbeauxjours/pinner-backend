import os
import uuid
from django.db import models
from config import models as config_models
from django.contrib.auth.models import AbstractUser
from django.contrib.humanize.templatetags.humanize import naturaltime

from utils import notify_slack
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from cached_property import cached_property


class User(AbstractUser, config_models.TimeStampedModel):

    """ User Model """

    GENDERS = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other')
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, blank=True, null=True)
    push_token = models.CharField(blank=True, null=True, max_length=200)
    bio = models.TextField(default='', blank=True, null=True)
    distance = models.IntegerField(default=0, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    gender = models.CharField(max_length=15, blank=True, null=True, choices=GENDERS)
    residence = models.ForeignKey(
        'locations.Country', blank=True, null=True, on_delete=models.SET_NULL, related_name='residence')
    nationality = models.ForeignKey(
        'locations.Country', blank=True, null=True, on_delete=models.SET_NULL, related_name='nationality')
    avatar_url = models.CharField(max_length=300, blank=True, null=True)
    app_avatar_url = models.CharField(max_length=300, blank=True, null=True)
    country_phone_code = models.CharField(max_length=20, blank=True, null=True)
    country_phone_number = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    is_verified_phone_number = models.BooleanField(default=False)
    is_verified_email_address = models.BooleanField(default=False)
    email_address = models.EmailField(blank=True, null=True, max_length=50)
    fbId = models.CharField(blank=True, null=True, max_length=60)
    appleId = models.CharField(blank=True, null=True, max_length=80)
    is_dark_mode = models.BooleanField(default=True)
    is_hide_photos = models.BooleanField(default=False)
    is_hide_trips = models.BooleanField(default=False)
    is_hide_cities = models.BooleanField(default=False)
    is_hide_countries = models.BooleanField(default=False)
    is_hide_continents = models.BooleanField(default=False)
    is_auto_location_report = models.BooleanField(default=True)
    current_city = models.ForeignKey(
        'locations.City', on_delete=models.SET_NULL, null=True, blank=True, related_name='currentCity', )
    current_country = models.ForeignKey(
        'locations.Country', on_delete=models.SET_NULL, null=True, blank=True, related_name='currentCountry', )
    current_continent = models.ForeignKey(
        'locations.Continent', on_delete=models.SET_NULL, null=True, blank=True, related_name='currentContinent', )
    blocked_user = models.ManyToManyField('self',  blank=True, related_name='user_blocked')

    send_instagram = models.CharField(blank=True, null=True, max_length=200, default="")
    send_phone = models.CharField(blank=True, null=True, max_length=200, default="")
    send_email = models.EmailField(blank=True, null=True, max_length=200, default="")
    send_kakao = models.CharField(blank=True, null=True, max_length=200, default="")
    send_facebook = models.CharField(blank=True, null=True, max_length=200, default="")
    send_snapchat = models.CharField(blank=True, null=True, max_length=200, default="")
    send_line = models.CharField(blank=True, null=True, max_length=200, default="")
    send_wechat = models.CharField(blank=True, null=True, max_length=200, default="")
    send_kik = models.CharField(blank=True, null=True, max_length=200, default="")
    send_vk = models.CharField(blank=True, null=True, max_length=200, default="")
    send_whatsapp = models.CharField(blank=True, null=True, max_length=200, default="")
    send_twitter = models.CharField(blank=True, null=True, max_length=200, default="")
    send_youtube = models.CharField(blank=True, null=True, max_length=200, default="")
    send_telegram = models.CharField(blank=True, null=True, max_length=200, default="")
    send_behance = models.CharField(blank=True, null=True, max_length=200, default="")
    send_linkedin = models.CharField(blank=True, null=True, max_length=200, default="")
    send_pinterest = models.CharField(blank=True, null=True, max_length=200, default="")
    send_vine = models.CharField(blank=True, null=True, max_length=200, default="")
    send_tumblr = models.CharField(blank=True, null=True, max_length=200, default="")

    def __str__(self):
        return self.username

    @cached_property
    def id(self):
        return self.id

    @cached_property
    def photo_count(self):
        return self.avatar.all().order_by('-created_at').count()

    @cached_property
    def blocked_user_count(self):
        return self.blocked_user.all().order_by('-created_at').count()

    @cached_property
    def city_count(self):
        return self.moveNotificationUser.all().order_by('city').distinct('city').count()
        # return self.moveNotificationUser.all().order_by('city').count()

    @cached_property
    def country_count(self):
        return self.moveNotificationUser.all().order_by('city__country').distinct('city__country').count()
        # return self.moveNotificationUser.all().order_by('city__country').count()

    @cached_property
    def continent_count(self):
        return self.moveNotificationUser.all().order_by('city__country__continent').distinct('city__country__continent').count()
        # return self.moveNotificationUser.all().order_by('city__country__continent').count()

    @cached_property
    def trip_count(self):
        return self.moveNotificationUser.all().count()

    class Meta:
        ordering = ['-created_at']


@receiver(post_delete, sender=User)
def delete_attached_image(sender, **kwargs):
    instance = kwargs.pop('instance')
    instance.delete()


# @receiver(post_save, sender=User)
# def send_slack_notification_city_created(sender, instance, created,  **kwargs):
#     if created:
#         to_channel = "#user"
#         attachments = [{
#             "fallback": "New User on Pinner",
#             "color": "#569934",
#             # "pretext": "Optional text that appears above the attachment block",
#             # "author_name": instance.username,
#             # "author_link": "localhost:3000/%s" % (instance.username),
#             "title":  "New user: %s" % (instance.username),
#             "title_link": "https://www.pinner.fun/%s" % (instance.username),
#             "text": "From %s , %s %s. \n Total user until now is %s" % (instance.current_city, instance.current_city.country.country_name, instance.current_city.country.country_emoji, User.objects.all().count()),
#             "footer": "🙌🏻 New User!",
#         }]
#         notify_slack(to_channel,  attachments)


def upload_image(instance, filename):
    name, extension = os.path.splitext(filename)
    return os.path.join('profileAvatar/{}/image/{}{}').format(instance.creator.id, instance.uuid, extension.lower())


def upload_thumbnail(instance, filename):
    name, extension = os.path.splitext(filename)
    return os.path.join('profileAvatar/{}/thumbnail/{}{}').format(instance.creator.id, instance.uuid, extension.lower())


def upload_app_thumbnail(instance, filename):
    name, extension = os.path.splitext(filename)
    return os.path.join('profileAvatar/{}/app_thumbnail/{}{}').format(instance.creator.id, instance.uuid, extension.lower())


class Avatar(config_models.TimeStampedModel):
    is_main = models.BooleanField(default=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, blank=True, null=True)
    creator = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='avatar')
    image = ProcessedImageField(
        upload_to=upload_image,
        null=True,
        blank=True,
        processors=[ResizeToFill(935, 935)],
        format='JPEG',
        options={'quality': 100}
    )
    thumbnail = ProcessedImageField(
        upload_to=upload_thumbnail,
        null=True,
        blank=True,
        processors=[ResizeToFill(450, 450)],
        format='JPEG',
        options={'quality': 100}
    )
    app_thumbnail = ProcessedImageField(
        upload_to=upload_app_thumbnail,
        null=True,
        blank=True,
        processors=[ResizeToFill(240, 240)],
        format='JPEG',
        options={'quality': 100}
    )

    @cached_property
    def like_count(self):
        return self.likes.all().count()

    @property
    def natural_time(self):
        return naturaltime(self.created_at)

    class Meta:
        ordering = ['-created_at']


@receiver(post_delete, sender=Avatar)
def delete_attached_image(sender, **kwargs):
    instance = kwargs.pop('instance')
    instance.image.delete(save=False)
    instance.thumbnail.delete(save=False)

    @property
    def natural_time(self):
        return naturaltime(self.created_at)


def logo_image_upload_to(instance, filename):
    m = hashlib.md5()
    m.update(f'{instance.id}{filename}'.encode('utf-8'))
    return f'media/{m.hexdigest()}/{filename}'


class Like(config_models.TimeStampedModel):

    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name='avatar_likes')
    avatar = models.ForeignKey(
        Avatar, on_delete=models.CASCADE, null=True, related_name='likes')
