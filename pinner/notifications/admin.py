from django.contrib import admin
from . import models


@admin.register(models.Notification)
class NotificationAdmin(admin.ModelAdmin):

    search_fields = (
        'actor__username',
    )

    list_display = (
        'id',
        'actor',
        'target',
        'is_read',
        'verb',
    )


@admin.register(models.MoveNotification)
class MoveNotificationAdmin(admin.ModelAdmin):

    search_fields = (
        'actor__username',
    )

    list_display = (
        'id',
        'actor',
        'city',
        'start_date',
        'end_date',
        'verb',
        'diff_days',
    )
