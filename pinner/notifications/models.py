from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Q
from datetime import date

from django.core.exceptions import ValidationError

from config import models as config_models
from matchs import models as match_models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Notification(config_models.TimeStampedModel):

    VERBS = (
        ('match', 'MATCH'),
    )

    actor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notification_from')
    target = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='notification_to')
    verb = models.CharField(max_length=10, choices=VERBS, default='match')
    is_read = models.BooleanField(default=False)
    match = models.ForeignKey(
        match_models.Match, on_delete=models.CASCADE, null=True, blank=True, related_name='notification')

    @property
    def natural_time(self):
        return naturaltime(self.created_at)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '{} / From: {} {} 👉🏻 To:  Read:{}'.format(
            self.id,
            self.actor.username,
            self.verb,
            self.is_read
        )


class MoveNotification(config_models.TimeStampedModel):

    VERBS = (
        ('move', 'MOVE'),
        ('upload', 'UPLOAD'),

    )

    actor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='moveNotificationUser')
    verb = models.CharField(max_length=10, choices=VERBS, default='move')
    city = models.ForeignKey(
        'locations.City', on_delete=models.CASCADE, null=True, blank=True, related_name='moveNotificationCity')
    country = models.ForeignKey(
        'locations.Country', on_delete=models.CASCADE, null=True, blank=True, related_name='moveNotificationCountry')
    continent = models.ForeignKey(
        'locations.Continent', on_delete=models.CASCADE, null=True, blank=True, related_name='moveNotificationContinent')

    @property
    def natural_time(self):
        return naturaltime(self.created_at)

    class Meta:
        ordering = ['-created_at']
