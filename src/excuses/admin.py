from django.contrib import admin

# Register your models here.
from excuses.models import Excuse, ExcuseReason


class ExcuseAdmin(admin.ModelAdmin):
    list_display = ["reason", "first_date", "last_date"]
    # search_fields = ["student__username", "student__first_name", "student__last_name", ]
    list_filter = ["reason"]

    class Meta:
        model = Excuse


class ExcuseReasonAdmin(admin.ModelAdmin):
    list_display = ["reason", "flex_activity"]
    list_filter = ["flex_activity"]

    class Meta:
        model = Excuse


admin.site.register(Excuse, ExcuseAdmin)
admin.site.register(ExcuseReason, ExcuseReasonAdmin)