from django.contrib import admin

# Register your models here.
from .models import Profile, Excuse, ExcuseReasons


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "get_first_name", "get_last_name", "homeroom_teacher", "grade", "phone", "email", "excused"]
    list_filter = ["grade", "excused"]
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


class ExcuseAdmin(admin.ModelAdmin):
    list_display = ["student", "get_first_name", "get_last_name", "reason", "first_date", "last_date"]
    search_fields = ["student__username", "student__first_name", "student__last_name", ]
    list_filter = ["reason"]

    class Meta:
        model = Excuse

    def get_first_name(self, obj):
        return obj.student.first_name

    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'student__first_name'

    def get_last_name(self, obj):
        return obj.student.last_name

    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'student__last_name'


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Excuse, ExcuseAdmin)
admin.site.register(ExcuseReasons)
