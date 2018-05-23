import bleach as bleach
from django.contrib import admin

# Register your models here.
from django.db import transaction

from .models import Event, Block, Location, Category, Registration, CoreCompetency


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "sort_priority", "color", "visible_in_event_list", "description"]

    class Meta:
        model = Category

class CoreCompetencyAdmin(admin.ModelAdmin):
    list_display = ["name", "link"]

    class Meta:
        model = CoreCompetency


class RegistrationAdmin(admin.ModelAdmin):
    list_display = ["get_event_date", "event", "block", "student", "get_first_name", "get_last_name", ]
    search_fields = ["event__title", "student__first_name", "student__last_name", ]
    list_filter = ["event__date", "block", ]

    class Meta:
        model = Registration

    def get_event_date(self, obj):
        return obj.event.date
    get_event_date.short_description = 'Date'
    get_event_date.admin_order_field = 'event__date'

    def get_first_name(self, obj):
        return obj.student.first_name
    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'student__first_name'

    def get_last_name(self, obj):
        return obj.student.last_name
    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'student__last_name'


class BlockAdmin(admin.ModelAdmin):
    list_display = ["name", "start_time", "end_time"]

    class Meta:
        model = Block


# Was used to cache images from link that existed before caching was implemented
def resave(eventadmin, request, queryset):
    for event in queryset:
        event.save()


# Used to remove tags when description was switched to plain text
@transaction.atomic
def bleach_html(eventadmin, request, queryset):
    for event in queryset:
        description = event.description
        description = description.replace("</p>", "\n\n")
        description = description.replace("</P>", "\n\n")
        description = description.replace("<br>", "\n")
        description = description.replace("<br />", "\n")
        description = description.replace("<br/>", "\n")
        event.description = bleach.clean(description, strip=True)
        event.save()
bleach_html.short_description = "Remove undesired HTML tags from event descriptions."

@transaction.atomic
def remove_links(eventadmin, request, queryset):
    for event in queryset:
        link = event.description_link
        if link and link.endswith(('jpg','jpeg','png','gif')):
            event.description_link = None
            event.save()
remove_links.short_description = "Remove description links that are images."

class EventAdmin(admin.ModelAdmin):

    list_display = ["title", "creator", "date", "location", ]
    list_filter = ["date", "blocks", ]
    # list_editable = ["title", ]
    # list_display_links = ["created_timestamp", ]
    actions = [resave, bleach_html, remove_links]

    search_fields = ["title", "description"]

    class Meta:
        model = Event


admin.site.register(Event, EventAdmin)
admin.site.register(Location)
admin.site.register(Block, BlockAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(CoreCompetency, CoreCompetencyAdmin)
