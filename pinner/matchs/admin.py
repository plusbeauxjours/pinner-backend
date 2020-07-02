from django.contrib import admin
from . import models


@admin.register(models.Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'city',
        'guest',
        'is_read_by_guest',
        'host',
        'is_read_by_host',
    )
