from django.contrib import admin

from . import models


@admin.register(models.Version)
class VersionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': ['publish_date', 'location_count'],
        }),
        ("Status", {
            'fields': ['is_active'],
        }),
    ]
    list_display = ['publish_date', 'location_count', 'is_active']
    list_filter = ['is_active']
    readonly_fields = ['publish_date', 'location_count']

    def location_count(self, obj):
        return obj.location_set.count()


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'latitude', 'longitude', 'density', '_version']
    list_display_links = None
    list_filter = ['version']

    def _version(self, obj):
        return obj.version.publish_date

    def has_change_permission(self, request, obj=None):
        return False if obj else True
