from django.contrib import admin

# Register your models here.
from utilities.models import MenuItem


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'sort_order', 'visible')

admin.site.register(MenuItem, MenuItemAdmin)