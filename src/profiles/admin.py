from django.contrib import admin

# Register your models here.
from .models import Profile


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "get_first_name", "get_last_name", "homeroom_teacher",
                    "grade", "phone", "email", "permission", "updated", ]
    readonly_fields = ["updated", ]
    list_filter = ["grade", "permission", ]
    actions = ["reset_permission_form_records"]
    # list_editable = ["title", ]
    # list_display_links = ["created_timestamp", ]

    search_fields = ["user__username", "user__first_name", "user__last_name", ]

    class Meta:
        model = Profile

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'user__first_name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'user__last_name'

    def reset_permission_form_records(self, request, queryset):
        rows_updated = queryset.update(permission=None)
        self.message_user(request, "Permissions records reset for {} students.".format(rows_updated))
    reset_permission_form_records.short_description = "Reset permission records for selected students"


admin.site.register(Profile, ProfileAdmin)
