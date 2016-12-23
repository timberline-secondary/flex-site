from django.contrib import admin

# Register your models here.
from .models import Event, Block, Location, Category, Registration


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "visible_in_event_list", "description"]

    class Meta:
        model = Category


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["event", "student"]

    class Meta:
        model = Registration


class BlockAdmin(admin.ModelAdmin):
    list_display = ["name", "start_time", "end_time"]

    class Meta:
        model = Block


class EventAdmin(admin.ModelAdmin):

    list_display = ["title", "location", "created_timestamp", "updated_timestamp", ]
    list_filter = ["created_timestamp", "updated_timestamp", ]
    # list_editable = ["title", ]
    # list_display_links = ["created_timestamp", ]

    search_fields = ["title", "description"]

    class Meta:
        model = Event


admin.site.register(Event, EventAdmin)
admin.site.register(Location)
admin.site.register(Block, BlockAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Registration, RegistrationAdmin)
