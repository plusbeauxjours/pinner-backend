from django.contrib import admin
from . import models


@admin.register(models.Verification)
class Verifications(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'target',
        'is_edit',
        'is_verified',
        'payload',
        'key',
    )
