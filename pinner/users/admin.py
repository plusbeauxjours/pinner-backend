from django.contrib import admin
from . import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):

    fieldsets = (
        (
            "Basic Info",
            {"fields": (
                "first_name",
                "last_name",
                "gender",
                "nationality",
                "residence",
                "bio",
                "distance",
            )},
        ),
        ("Contact", {"fields": ("phone_number", "is_verified_phone_number",
                                "email_address", "is_verified_email_address",), }),
        ("Location", {"fields": ("current_city", "current_country", "current_continent")}),
        ("Blocked User", {"fields": ("blocked_user", )}),
        ("Token",
         {
             "classes": ("collapse",),
             "fields": (
                 "push_token",
                 "fbId",
                 "appleId",
             ),
         },
         ),
        (
            "More About the SNS",
            {
                "classes": ("collapse",),
                "fields": (
                    "send_instagram",
                    "send_phone",
                    "send_email",
                    "send_kakao",
                    "send_facebook",
                    "send_snapchat",
                    "send_line",
                    "send_wechat",
                    "send_kik",
                    "send_vk",
                    "send_whatsapp",
                    "send_twitter",
                    "send_youtube",
                    "send_telegram",
                    "send_behance",
                    "send_linkedin",
                    "send_pinterest",
                    "send_vine",
                    "send_tumblr",
                ),
            },
        ),
        ("Settings",
            {
                "classes": ("collapse",),
                "fields": (
                    "is_dark_mode",
                    "is_hide_photos",
                    "is_hide_trips",
                    "is_hide_cities",
                    "is_hide_countries",
                    "is_hide_continents",
                    "is_auto_location_report",
                ),
            },
         )
    )

    list_display = (
        "id",
        "uuid",
        "username",
        "gender",
        "phone_number",
        "email_address",
        "current_city",
        "current_country",
        "current_continent",
        "photo_count",
        "city_count",
        "trip_count",
        "country_count",
        "continent_count",
        "nationality",
        "residence",
        "is_verified_phone_number",
        "is_verified_email_address",
    )


@admin.register(models.Avatar)
class AvatarAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "uuid",
        "creator",
        "is_main",
        "image",
        "thumbnail",
    )


@admin.register(models.Like)
class LikeAdmin(admin.ModelAdmin):

    list_display = (
        "creator",
        "avatar",
    )
