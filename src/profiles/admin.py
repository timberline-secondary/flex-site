from django.contrib import admin

# Register your models here.
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "first_name", "last_name", "homeroom_teacher", ]
    list_filter = ["homeroom_teacher", ]
    # list_editable = ["title", ]
    # list_display_links = ["created_timestamp", ]

    search_fields = ["first_name", "last_name", "homeroom_teacher",]

    class Meta:
        model = Profile


admin.site.register(Profile, ProfileAdmin)
