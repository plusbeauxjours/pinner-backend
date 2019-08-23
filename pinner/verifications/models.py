import random
import math
import uuid
import secrets

from django.db import models
from django.contrib.auth.models import User
from config import models as config_models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Verification(config_models.TimeStampedModel):

    TARGETS = (
        ('phone', 'Phone'),
        ('email', 'Email')
    )
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='verification')
    target = models.CharField(max_length=10, choices=TARGETS)
    payload = models.CharField(max_length=30)
    key = models.CharField(max_length=300, blank=True)
    is_verified = models.BooleanField(default=False)
    is_edit = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.payload


@receiver(pre_save, sender=Verification)
def create_key(sender, **kwargs):
    instance = kwargs.pop('instance')
    if instance.target == "phone" and instance.is_verified == False:
        instance.key = str(math.floor(random.random() * 1000000)).zfill(6)
    elif instance.target == "email" and instance.is_verified == False:
        instance.key = secrets.token_urlsafe(120)
    else:
        pass
