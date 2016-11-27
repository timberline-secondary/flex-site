from django.contrib import admin

# Register your models here.
from .models import Event, Block, Location, Category


class BlockAdmin(admin.ModelAdmin):
    list_display = ["name", "start_time", "end_time"]


class EventAdmin(admin.ModelAdmin):

    list_display = ["title", "location", "created_timestamp", "updated_timestamp", ]
    list_filter = ["created_timestamp", "updated_timestamp", ]
    # list_editable = ["title", ]
    # list_display_links = ["created_timestamp", ]

    search_fields = ["title", "description"]

    # Blocks
    # Date
    # Teacher
    # Category
    # Location
    # Max Participants
    # Registration cut_off (default will be 10 minutes prior to the event's start time.  If you need
    # Allow students to leave event after registration until date

    class Meta:
        model = Event


admin.site.register(Event, EventAdmin)
admin.site.register(Location)
admin.site.register(Block, BlockAdmin)
admin.site.register(Category)
