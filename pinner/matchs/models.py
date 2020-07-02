from django.db import models
from config import models as config_models

from django.contrib.humanize.templatetags.humanize import naturaltime


class Match(config_models.TimeStampedModel):

    city = models.ForeignKey('locations.City', on_delete=models.CASCADE, null=True, blank=True)
    host = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='host')
    guest = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='guest')
    is_read_by_host = models.BooleanField(default=False)
    is_read_by_guest = models.BooleanField(default=False)

    @property
    def country_count(self):
        return self.countries.all().count()

    @property
    def natural_time(self):
        return naturaltime(self.created_at)
